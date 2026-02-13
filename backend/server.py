from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
from authlib.integrations.starlette_client import OAuth
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
import io
import json
import aiofiles
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create uploads directory
UPLOADS_DIR = ROOT_DIR / 'uploads' / 'pieces'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Max file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Session secret key
SESSION_SECRET = os.environ.get('SESSION_SECRET', secrets.token_hex(32))

# PostgreSQL Database Setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    picture = Column(Text, nullable=True)
    credits = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UserSessionModel(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class LegalConclusionModel(Base):
    __tablename__ = "legal_conclusions"
    
    id = Column(Integer, primary_key=True, index=True)
    conclusion_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    type = Column(String(50), nullable=False)
    parties = Column(JSON, nullable=True)
    faits = Column(Text, nullable=True)
    demandes = Column(Text, nullable=True)
    conclusion_text = Column(Text, nullable=True)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PieceModel(Base):
    __tablename__ = "pieces"
    
    id = Column(Integer, primary_key=True, index=True)
    piece_id = Column(String(50), unique=True, index=True, nullable=False)
    conclusion_id = Column(String(50), index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    numero = Column(Integer, nullable=False)
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PaymentTransactionModel(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    package_id = Column(String(50), nullable=False)
    payment_status = Column(String(50), default="pending")
    payment_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class CodeCivilArticleModel(Base):
    __tablename__ = "code_civil_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String(50), unique=True, index=True, nullable=False)
    numero = Column(String(50), nullable=False)
    titre = Column(String(500), nullable=False)
    contenu = Column(Text, nullable=False)
    categorie = Column(String(100), nullable=True)

class ConclusionTemplateModel(Base):
    __tablename__ = "conclusion_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=True)
    faits_template = Column(Text, nullable=True)
    demandes_template = Column(Text, nullable=True)
    articles_pertinents = Column(JSON, nullable=True)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

api_router = APIRouter(prefix="/api")

# Google OAuth configuration
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models for API
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    credits: int = 0
    created_at: datetime

class LegalConclusion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    conclusion_id: str
    user_id: str
    type: str
    parties: Dict[str, Any]
    faits: str
    demandes: str
    conclusion_text: str
    status: str = "draft"
    created_at: datetime
    updated_at: datetime

class ConclusionCreateRequest(BaseModel):
    type: str
    parties: Dict[str, Any]
    faits: str
    demandes: str

class ConclusionUpdateRequest(BaseModel):
    conclusion_text: Optional[str] = None
    status: Optional[str] = None

class GenerateConclusionRequest(BaseModel):
    type: str
    parties: Dict[str, Any]
    faits: str
    demandes: str

class ConclusionTemplate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    template_id: str
    name: str
    description: str
    type: str
    category: str
    faits_template: str
    demandes_template: str
    articles_pertinents: List[str]

class Piece(BaseModel):
    model_config = ConfigDict(extra="ignore")
    piece_id: str
    conclusion_id: str
    user_id: str
    numero: int
    nom: str
    description: Optional[str] = ""
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime

class PieceUpdateRequest(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None

class PieceReorderRequest(BaseModel):
    piece_ids: List[str]

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str

# Fixed packages - NEVER accept amounts from frontend
PACKAGES = {
    "essentielle": {
        "price": 29.0,
        "currency": "eur",
        "name": "Offre Essentielle",
        "credits": 1
    }
}

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication Helper
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    session = db.query(UserSessionModel).filter(
        UserSessionModel.session_token == session_token
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expirée")
    
    user = db.query(UserModel).filter(
        UserModel.user_id == session.user_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return User(
        user_id=user.user_id,
        email=user.email,
        name=user.name or "",
        picture=user.picture,
        credits=user.credits,
        created_at=user.created_at
    )

# Auth Routes - Google OAuth
@api_router.get("/auth/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro-frontend.onrender.com')
    redirect_uri = os.environ.get('BACKEND_URL', str(request.base_url).rstrip('/')) + '/api/auth/google/callback'
    
    request.session['frontend_redirect'] = frontend_url + '/dashboard'
    
    return await oauth.google.authorize_redirect(request, redirect_uri)

@api_router.get("/auth/google/callback")
async def google_callback(request: Request, response: Response, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        logger.info("OAuth callback received")
        token = await oauth.google.authorize_access_token(request)
        logger.info(f"Token received: {bool(token)}")
        
        user_info = token.get('userinfo')
        if not user_info:
            user_info = token.get('id_token')
            if not user_info:
                logger.error("No user info in token")
                raise HTTPException(status_code=400, detail="Could not get user info")
        
        logger.info(f"User info: {user_info.get('email', 'no email')}")
        
        # Find or create user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        existing_user = db.query(UserModel).filter(
            UserModel.email == user_info["email"]
        ).first()
        
        if existing_user:
            user_id = existing_user.user_id
            existing_user.name = user_info.get("name", "")
            existing_user.picture = user_info.get("picture")
            db.commit()
            logger.info(f"User updated: {user_id}")
        else:
            new_user = UserModel(
                user_id=user_id,
                email=user_info["email"],
                name=user_info.get("name", ""),
                picture=user_info.get("picture"),
                credits=0,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_user)
            db.commit()
            logger.info(f"User created: {user_id}")
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        new_session = UserSessionModel(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_session)
        db.commit()
        logger.info(f"Session created for user: {user_id}")
        
        # Get frontend redirect URL
        frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro-frontend.onrender.com')
        frontend_redirect = f"{frontend_url}/dashboard"
        
        # Create redirect response with cookie
        redirect_response = RedirectResponse(url=frontend_redirect, status_code=302)
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7*24*60*60,
            path="/",
            domain=None
        )
        
        logger.info(f"Redirecting to: {frontend_redirect}")
        return redirect_response
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        db.rollback()
        frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro-frontend.onrender.com')
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed", status_code=302)

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    
    if session_token:
        db.query(UserSessionModel).filter(
            UserSessionModel.session_token == session_token
        ).delete()
        db.commit()
    
    response.delete_cookie(key="session_token", path="/", samesite="none", secure=True)
    return {"message": "Déconnexion réussie"}

# Code Civil Routes
@api_router.get("/code-civil/search")
async def search_code_civil(q: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    articles = db.query(CodeCivilArticleModel).filter(
        (CodeCivilArticleModel.titre.ilike(f"%{q}%")) |
        (CodeCivilArticleModel.contenu.ilike(f"%{q}%")) |
        (CodeCivilArticleModel.numero.ilike(f"%{q}%"))
    ).limit(20).all()
    
    return [
        {
            "article_id": a.article_id,
            "numero": a.numero,
            "titre": a.titre,
            "contenu": a.contenu,
            "categorie": a.categorie
        }
        for a in articles
    ]

@api_router.get("/code-civil/articles")
async def get_all_articles(category: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(CodeCivilArticleModel)
    if category:
        query = query.filter(CodeCivilArticleModel.categorie == category)
    
    articles = query.limit(1000).all()
    return [
        {
            "article_id": a.article_id,
            "numero": a.numero,
            "titre": a.titre,
            "contenu": a.contenu,
            "categorie": a.categorie
        }
        for a in articles
    ]

# Templates Routes
@api_router.get("/templates")
async def get_templates(type: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(ConclusionTemplateModel)
    if type:
        query = query.filter(ConclusionTemplateModel.type == type)
    
    templates = query.limit(100).all()
    return [
        ConclusionTemplate(
            template_id=t.template_id,
            name=t.name,
            description=t.description or "",
            type=t.type,
            category=t.category or "",
            faits_template=t.faits_template or "",
            demandes_template=t.demandes_template or "",
            articles_pertinents=t.articles_pertinents or []
        )
        for t in templates
    ]

@api_router.get("/templates/{template_id}")
async def get_template(template_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    template = db.query(ConclusionTemplateModel).filter(
        ConclusionTemplateModel.template_id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    
    return ConclusionTemplate(
        template_id=template.template_id,
        name=template.name,
        description=template.description or "",
        type=template.type,
        category=template.category or "",
        faits_template=template.faits_template or "",
        demandes_template=template.demandes_template or "",
        articles_pertinents=template.articles_pertinents or []
    )

# Payment Routes
@api_router.post("/payments/create-checkout")
async def create_checkout(
    data: CheckoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail="Package invalide")
    
    package = PACKAGES[data.package_id]
    stripe_api_key = os.environ.get('STRIPE_API_KEY')
    
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    base_url = str(request.base_url).rstrip('/')
    webhook_url = f"{base_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    success_url = f"{data.origin_url}/payment-success?session_id={{{{CHECKOUT_SESSION_ID}}}}"
    cancel_url = f"{data.origin_url}/tarifs"
    
    transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
    
    checkout_request = CheckoutSessionRequest(
        amount=package["price"],
        currency=package["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": current_user.user_id,
            "transaction_id": transaction_id,
            "package_id": data.package_id,
            "package_name": package["name"]
        }
    )
    
    session_resp: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
    new_transaction = PaymentTransactionModel(
        transaction_id=transaction_id,
        user_id=current_user.user_id,
        session_id=session_resp.session_id,
        amount=package["price"],
        currency=package["currency"],
        package_id=data.package_id,
        payment_status="pending",
        payment_metadata=checkout_request.metadata,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(new_transaction)
    db.commit()
    
    return {"url": session_resp.url, "session_id": session_resp.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stripe_api_key = os.environ.get('STRIPE_API_KEY')
    
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    base_url = os.environ.get('BACKEND_URL', str(request.base_url).rstrip('/'))
    webhook_url = f"{base_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
    
    transaction = db.query(PaymentTransactionModel).filter(
        PaymentTransactionModel.session_id == session_id,
        PaymentTransactionModel.user_id == current_user.user_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    if checkout_status.payment_status == "paid" and transaction.payment_status != "paid":
        transaction.payment_status = "paid"
        transaction.updated_at = datetime.now(timezone.utc)
        
        package = PACKAGES.get(transaction.package_id, {})
        credits = package.get("credits", 1)
        
        user = db.query(UserModel).filter(UserModel.user_id == current_user.user_id).first()
        if user:
            user.credits += credits
        
        db.commit()
    
    return {
        "status": checkout_status.status,
        "payment_status": checkout_status.payment_status,
        "amount": checkout_status.amount_total / 100,
        "currency": checkout_status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    stripe_api_key = os.environ.get('STRIPE_API_KEY')
    
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    base_url = str(request.base_url).rstrip('/')
    webhook_url = f"{base_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            transaction = db.query(PaymentTransactionModel).filter(
                PaymentTransactionModel.session_id == webhook_response.session_id
            ).first()
            
            if transaction and transaction.payment_status != "paid":
                transaction.payment_status = "paid"
                transaction.updated_at = datetime.now(timezone.utc)
                
                user_id = webhook_response.metadata.get("user_id")
                package_id = webhook_response.metadata.get("package_id")
                
                if user_id and package_id:
                    package = PACKAGES.get(package_id, {})
                    credits = package.get("credits", 1)
                    
                    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
                    if user:
                        user.credits += credits
                
                db.commit()
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Conclusions Routes
@api_router.post("/conclusions", status_code=201)
async def create_conclusion(data: ConclusionCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion_id = f"concl_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    new_conclusion = LegalConclusionModel(
        conclusion_id=conclusion_id,
        user_id=current_user.user_id,
        type=data.type,
        parties=data.parties,
        faits=data.faits,
        demandes=data.demandes,
        conclusion_text="",
        status="draft",
        created_at=now,
        updated_at=now
    )
    db.add(new_conclusion)
    db.commit()
    db.refresh(new_conclusion)
    
    return LegalConclusion(
        conclusion_id=new_conclusion.conclusion_id,
        user_id=new_conclusion.user_id,
        type=new_conclusion.type,
        parties=new_conclusion.parties or {},
        faits=new_conclusion.faits or "",
        demandes=new_conclusion.demandes or "",
        conclusion_text=new_conclusion.conclusion_text or "",
        status=new_conclusion.status,
        created_at=new_conclusion.created_at,
        updated_at=new_conclusion.updated_at
    )

@api_router.get("/conclusions")
async def get_conclusions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusions = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.user_id == current_user.user_id
    ).order_by(LegalConclusionModel.created_at.desc()).all()
    
    return [
        LegalConclusion(
            conclusion_id=c.conclusion_id,
            user_id=c.user_id,
            type=c.type,
            parties=c.parties or {},
            faits=c.faits or "",
            demandes=c.demandes or "",
            conclusion_text=c.conclusion_text or "",
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in conclusions
    ]

@api_router.get("/conclusions/{conclusion_id}")
async def get_conclusion(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    return LegalConclusion(
        conclusion_id=conclusion.conclusion_id,
        user_id=conclusion.user_id,
        type=conclusion.type,
        parties=conclusion.parties or {},
        faits=conclusion.faits or "",
        demandes=conclusion.demandes or "",
        conclusion_text=conclusion.conclusion_text or "",
        status=conclusion.status,
        created_at=conclusion.created_at,
        updated_at=conclusion.updated_at
    )

@api_router.put("/conclusions/{conclusion_id}")
async def update_conclusion(
    conclusion_id: str,
    data: ConclusionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    if data.conclusion_text is not None:
        conclusion.conclusion_text = data.conclusion_text
    if data.status is not None:
        conclusion.status = data.status
    conclusion.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(conclusion)
    
    return LegalConclusion(
        conclusion_id=conclusion.conclusion_id,
        user_id=conclusion.user_id,
        type=conclusion.type,
        parties=conclusion.parties or {},
        faits=conclusion.faits or "",
        demandes=conclusion.demandes or "",
        conclusion_text=conclusion.conclusion_text or "",
        status=conclusion.status,
        created_at=conclusion.created_at,
        updated_at=conclusion.updated_at
    )

@api_router.delete("/conclusions/{conclusion_id}")
async def delete_conclusion(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    # Delete all pieces associated with this conclusion
    pieces = db.query(PieceModel).filter(
        PieceModel.conclusion_id == conclusion_id,
        PieceModel.user_id == current_user.user_id
    ).all()
    
    for piece in pieces:
        file_path = UPLOADS_DIR / piece.filename
        if file_path.exists():
            file_path.unlink()
        db.delete(piece)
    
    db.delete(conclusion)
    db.commit()
    
    return {"message": "Conclusion supprimée"}

# Pieces Routes
@api_router.post("/conclusions/{conclusion_id}/pieces", status_code=201)
async def upload_piece(
    conclusion_id: str,
    file: UploadFile = File(...),
    nom: str = Form(...),
    description: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify conclusion exists and belongs to user
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 10 Mo")
    
    # Get next piece number
    last_piece = db.query(PieceModel).filter(
        PieceModel.conclusion_id == conclusion_id
    ).order_by(PieceModel.numero.desc()).first()
    
    next_numero = (last_piece.numero + 1) if last_piece else 1
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{conclusion_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = UPLOADS_DIR / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create piece record
    piece_id = f"piece_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    new_piece = PieceModel(
        piece_id=piece_id,
        conclusion_id=conclusion_id,
        user_id=current_user.user_id,
        numero=next_numero,
        nom=nom,
        description=description,
        filename=unique_filename,
        original_filename=file.filename or "fichier",
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        created_at=now,
        updated_at=now
    )
    db.add(new_piece)
    db.commit()
    db.refresh(new_piece)
    
    return Piece(
        piece_id=new_piece.piece_id,
        conclusion_id=new_piece.conclusion_id,
        user_id=new_piece.user_id,
        numero=new_piece.numero,
        nom=new_piece.nom,
        description=new_piece.description or "",
        filename=new_piece.filename,
        original_filename=new_piece.original_filename,
        file_size=new_piece.file_size,
        mime_type=new_piece.mime_type,
        created_at=new_piece.created_at,
        updated_at=new_piece.updated_at
    )

@api_router.get("/conclusions/{conclusion_id}/pieces")
async def get_pieces(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify conclusion exists and belongs to user
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    pieces = db.query(PieceModel).filter(
        PieceModel.conclusion_id == conclusion_id,
        PieceModel.user_id == current_user.user_id
    ).order_by(PieceModel.numero.asc()).all()
    
    return [
        Piece(
            piece_id=p.piece_id,
            conclusion_id=p.conclusion_id,
            user_id=p.user_id,
            numero=p.numero,
            nom=p.nom,
            description=p.description or "",
            filename=p.filename,
            original_filename=p.original_filename,
            file_size=p.file_size,
            mime_type=p.mime_type,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pieces
    ]

@api_router.put("/conclusions/{conclusion_id}/pieces/reorder")
async def reorder_pieces(
    conclusion_id: str,
    data: PieceReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify conclusion exists and belongs to user
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    # Update piece numbers based on new order
    for idx, piece_id in enumerate(data.piece_ids, start=1):
        piece = db.query(PieceModel).filter(
            PieceModel.piece_id == piece_id,
            PieceModel.conclusion_id == conclusion_id,
            PieceModel.user_id == current_user.user_id
        ).first()
        if piece:
            piece.numero = idx
            piece.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Return updated pieces
    pieces = db.query(PieceModel).filter(
        PieceModel.conclusion_id == conclusion_id,
        PieceModel.user_id == current_user.user_id
    ).order_by(PieceModel.numero.asc()).all()
    
    return [
        Piece(
            piece_id=p.piece_id,
            conclusion_id=p.conclusion_id,
            user_id=p.user_id,
            numero=p.numero,
            nom=p.nom,
            description=p.description or "",
            filename=p.filename,
            original_filename=p.original_filename,
            file_size=p.file_size,
            mime_type=p.mime_type,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pieces
    ]

@api_router.put("/conclusions/{conclusion_id}/pieces/{piece_id}")
async def update_piece(
    conclusion_id: str,
    piece_id: str,
    data: PieceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    piece = db.query(PieceModel).filter(
        PieceModel.piece_id == piece_id,
        PieceModel.conclusion_id == conclusion_id,
        PieceModel.user_id == current_user.user_id
    ).first()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    if data.nom is not None:
        piece.nom = data.nom
    if data.description is not None:
        piece.description = data.description
    piece.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(piece)
    
    return Piece(
        piece_id=piece.piece_id,
        conclusion_id=piece.conclusion_id,
        user_id=piece.user_id,
        numero=piece.numero,
        nom=piece.nom,
        description=piece.description or "",
        filename=piece.filename,
        original_filename=piece.original_filename,
        file_size=piece.file_size,
        mime_type=piece.mime_type,
        created_at=piece.created_at,
        updated_at=piece.updated_at
    )

@api_router.delete("/conclusions/{conclusion_id}/pieces/{piece_id}")
async def delete_piece(
    conclusion_id: str,
    piece_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    piece = db.query(PieceModel).filter(
        PieceModel.piece_id == piece_id,
        PieceModel.conclusion_id == conclusion_id,
        PieceModel.user_id == current_user.user_id
    ).first()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    # Delete file
    file_path = UPLOADS_DIR / piece.filename
    if file_path.exists():
        file_path.unlink()
    
    # Delete record
    db.delete(piece)
    db.commit()
    
    # Renumber remaining pieces
    remaining_pieces = db.query(PieceModel).filter(
        PieceModel.conclusion_id == conclusion_id,
        PieceModel.user_id == current_user.user_id
    ).order_by(PieceModel.numero.asc()).all()
    
    for idx, p in enumerate(remaining_pieces, start=1):
        if p.numero != idx:
            p.numero = idx
            p.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"message": "Pièce supprimée"}

@api_router.get("/pieces/{piece_id}/download")
async def download_piece(piece_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    piece = db.query(PieceModel).filter(
        PieceModel.piece_id == piece_id,
        PieceModel.user_id == current_user.user_id
    ).first()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    file_path = UPLOADS_DIR / piece.filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    return FileResponse(
        path=str(file_path),
        filename=piece.original_filename,
        media_type=piece.mime_type
    )

# AI Generation Route
@api_router.post("/generate/conclusion")
async def generate_conclusion(
    data: GenerateConclusionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(
        UserModel.user_id == current_user.user_id
    ).first()
    
    if not user or user.credits <= 0:
        raise HTTPException(
            status_code=403, 
            detail="Crédits insuffisants. Veuillez acheter des crédits pour générer une conclusion."
        )
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Clé API non configurée")
    
    # Get relevant articles
    category = "famille" if data.type == "jaf" else "penal"
    articles = db.query(CodeCivilArticleModel).filter(
        CodeCivilArticleModel.categorie == category
    ).limit(5).all()
    
    articles_context = "\n".join([
        f"Article {art.numero} - {art.titre}:\n{art.contenu}"
        for art in articles
    ])
    
    if data.type == "jaf":
        type_label = "Juge aux Affaires Familiales (JAF)"
        system_prompt = f"""Vous êtes un assistant pédagogique spécialisé en rédaction d'écrits juridiques en droit de la famille français.

IMPORTANT : Vous NE FOURNISSEZ PAS de conseil juridique. Vous aidez uniquement à structurer et rédiger de manière claire.

Votre rôle :
1. Structurer le document selon les usages du barreau
2. Améliorer la clarté et le vocabulaire
3. Rendre le texte plus factuel et moins émotionnel

Vous NE devez PAS :
- Donner des conseils sur la stratégie juridique
- Interpréter les textes de loi
- Dire ce qui va se passer au tribunal
- Garantir un résultat

Structure standard d'un écrit en JAF :
1. EN-TÊTE : Tribunal, numéro, parties
2. EXPOSÉ DES FAITS : Présentation chronologique factuelle
3. ARGUMENTATION : Exposition des demandes avec références aux textes
4. DISPOSITIF : Demandes précises et numérotées
5. Formule de clôture et signature

Articles du Code Civil souvent cités dans ce type d'affaires :
{articles_context}

Rédigez un document structuré en aidant l'utilisateur à présenter ses faits et demandes de manière claire."""
    else:
        type_label = "affaire pénale"
        system_prompt = f"""Vous êtes un assistant pédagogique spécialisé en rédaction d'écrits juridiques en droit pénal français.

IMPORTANT : Vous NE FOURNISSEZ PAS de conseil juridique. Vous aidez uniquement à structurer et rédiger de manière claire.

Votre rôle :
1. Structurer le document selon les usages
2. Améliorer la clarté et le vocabulaire juridique approprié
3. Rendre le texte factuel et argumenté

Vous NE devez PAS :
- Conseiller sur la défense à adopter
- Prédire l'issue du procès
- Interpréter les faits juridiquement
- Garantir un résultat

Structure standard d'un écrit pénal :
1. EN-TÊTE : Juridiction, numéro, parties
2. RAPPEL DES FAITS : Présentation factuelle
3. ARGUMENTATION : Discussion des éléments
4. DEMANDES : Ce qui est sollicité
5. Formule de clôture

Articles souvent cités :
{articles_context}

Aidez l'utilisateur à présenter ses éléments de manière structurée et claire."""
    
    parties_str = json.dumps(data.parties, ensure_ascii=False, indent=2)
    user_prompt = f"""Aidez-moi à structurer un document pour une {type_label}.

RAPPEL : Vous êtes un assistant pédagogique. Ne donnez PAS de conseil juridique.
Aidez uniquement à structurer et clarifier la rédaction.

PARTIES:
{parties_str}

FAITS (tels que décrits par l'utilisateur):
{data.faits}

DEMANDES (telles que formulées par l'utilisateur):
{data.demandes}

Produisez un document structuré qui aide l'utilisateur à présenter ces éléments de manière claire et organisée.
Ajoutez des [NOTES PÉDAGOGIQUES] pour expliquer chaque section si nécessaire."""
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"gen_{current_user.user_id}_{uuid.uuid4().hex[:8]}",
        system_message=system_prompt
    )
    chat.with_model("gemini", "gemini-3-flash-preview")
    
    user_message = UserMessage(text=user_prompt)
    response = await chat.send_message(user_message)
    
    # Deduct credit
    user.credits -= 1
    db.commit()
    
    return {"conclusion_text": response, "credits_used": 1}

# PDF Export Route
@api_router.get("/conclusions/{conclusion_id}/pdf")
async def export_pdf(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(
        LegalConclusionModel.conclusion_id == conclusion_id,
        LegalConclusionModel.user_id == current_user.user_id
    ).first()
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 14)
    y = height - 2*cm
    p.drawString(2*cm, y, f"CONCLUSIONS - {conclusion.type.upper()}")
    
    y -= 1.5*cm
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y, f"Généré le {datetime.now(timezone.utc).strftime('%d/%m/%Y')}")
    
    y -= 2*cm
    p.setFont("Helvetica", 11)
    
    text = conclusion.conclusion_text or ""
    lines = text.split('\n')
    
    for line in lines:
        if y < 3*cm:
            p.showPage()
            y = height - 2*cm
            p.setFont("Helvetica", 11)
        
        wrapped_lines = simpleSplit(line, "Helvetica", 11, width - 4*cm)
        for wrapped_line in wrapped_lines:
            if y < 3*cm:
                p.showPage()
                y = height - 2*cm
                p.setFont("Helvetica", 11)
            p.drawString(2*cm, y, wrapped_line)
            y -= 0.5*cm
    
    p.save()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=conclusion_{conclusion_id}.pdf"}
    )

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.on_event("shutdown")
async def shutdown_db():
    engine.dispose()
