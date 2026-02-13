from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from mangum import Mangum
import os
import logging
from pathlib import Path
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from authlib.integrations.starlette_client import OAuth
from urllib.parse import quote_plus
import secrets
import json
import io

# Database Setup
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

# Create tables
Base.metadata.create_all(bind=engine)

# Session secret
SESSION_SECRET = os.environ.get('SESSION_SECRET', secrets.token_hex(32))

app = FastAPI()

# Session middleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
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

# Packages
PACKAGES = {
    "essentielle": {"price": 29.0, "currency": "eur", "name": "Offre Essentielle", "credits": 1}
}

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth helper
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    session = db.query(UserSessionModel).filter(UserSessionModel.session_token == session_token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expirée")
    
    user = db.query(UserModel).filter(UserModel.user_id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return User(user_id=user.user_id, email=user.email, name=user.name or "", picture=user.picture, credits=user.credits, created_at=user.created_at)

# Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/auth/google/login")
async def google_login(request: Request):
    frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro.vercel.app')
    redirect_uri = os.environ.get('BACKEND_URL', str(request.base_url).rstrip('/')) + '/api/auth/google/callback'
    request.session['frontend_redirect'] = frontend_url + '/dashboard'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo') or token.get('id_token')
        if not user_info:
            raise HTTPException(status_code=400, detail="Could not get user info")
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        existing_user = db.query(UserModel).filter(UserModel.email == user_info["email"]).first()
        
        if existing_user:
            user_id = existing_user.user_id
            existing_user.name = user_info.get("name", "")
            existing_user.picture = user_info.get("picture")
            db.commit()
        else:
            new_user = UserModel(user_id=user_id, email=user_info["email"], name=user_info.get("name", ""), picture=user_info.get("picture"), credits=0)
            db.add(new_user)
            db.commit()
        
        session_token = secrets.token_urlsafe(32)
        new_session = UserSessionModel(user_id=user_id, session_token=session_token, expires_at=datetime.now(timezone.utc) + timedelta(days=7))
        db.add(new_session)
        db.commit()
        
        frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro.vercel.app')
        redirect_response = RedirectResponse(url=f"{frontend_url}/dashboard", status_code=302)
        redirect_response.set_cookie(key="session_token", value=session_token, httponly=True, secure=True, samesite="none", max_age=7*24*60*60, path="/")
        return redirect_response
    except Exception as e:
        logger.error(f"OAuth error: {e}")
        db.rollback()
        frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro.vercel.app')
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed", status_code=302)

@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if session_token:
        db.query(UserSessionModel).filter(UserSessionModel.session_token == session_token).delete()
        db.commit()
    response.delete_cookie(key="session_token", path="/", samesite="none", secure=True)
    return {"message": "Déconnexion réussie"}

# Conclusions
@app.post("/api/conclusions", status_code=201)
async def create_conclusion(data: ConclusionCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion_id = f"concl_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    new_conclusion = LegalConclusionModel(conclusion_id=conclusion_id, user_id=current_user.user_id, type=data.type, parties=data.parties, faits=data.faits, demandes=data.demandes, conclusion_text="", status="draft", created_at=now, updated_at=now)
    db.add(new_conclusion)
    db.commit()
    db.refresh(new_conclusion)
    return LegalConclusion(conclusion_id=new_conclusion.conclusion_id, user_id=new_conclusion.user_id, type=new_conclusion.type, parties=new_conclusion.parties or {}, faits=new_conclusion.faits or "", demandes=new_conclusion.demandes or "", conclusion_text=new_conclusion.conclusion_text or "", status=new_conclusion.status, created_at=new_conclusion.created_at, updated_at=new_conclusion.updated_at)

@app.get("/api/conclusions")
async def get_conclusions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusions = db.query(LegalConclusionModel).filter(LegalConclusionModel.user_id == current_user.user_id).order_by(LegalConclusionModel.created_at.desc()).all()
    return [LegalConclusion(conclusion_id=c.conclusion_id, user_id=c.user_id, type=c.type, parties=c.parties or {}, faits=c.faits or "", demandes=c.demandes or "", conclusion_text=c.conclusion_text or "", status=c.status, created_at=c.created_at, updated_at=c.updated_at) for c in conclusions]

@app.get("/api/conclusions/{conclusion_id}")
async def get_conclusion(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(LegalConclusionModel.conclusion_id == conclusion_id, LegalConclusionModel.user_id == current_user.user_id).first()
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    return LegalConclusion(conclusion_id=conclusion.conclusion_id, user_id=conclusion.user_id, type=conclusion.type, parties=conclusion.parties or {}, faits=conclusion.faits or "", demandes=conclusion.demandes or "", conclusion_text=conclusion.conclusion_text or "", status=conclusion.status, created_at=conclusion.created_at, updated_at=conclusion.updated_at)

@app.put("/api/conclusions/{conclusion_id}")
async def update_conclusion(conclusion_id: str, data: ConclusionUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(LegalConclusionModel.conclusion_id == conclusion_id, LegalConclusionModel.user_id == current_user.user_id).first()
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    if data.conclusion_text is not None:
        conclusion.conclusion_text = data.conclusion_text
    if data.status is not None:
        conclusion.status = data.status
    conclusion.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(conclusion)
    return LegalConclusion(conclusion_id=conclusion.conclusion_id, user_id=conclusion.user_id, type=conclusion.type, parties=conclusion.parties or {}, faits=conclusion.faits or "", demandes=conclusion.demandes or "", conclusion_text=conclusion.conclusion_text or "", status=conclusion.status, created_at=conclusion.created_at, updated_at=conclusion.updated_at)

@app.delete("/api/conclusions/{conclusion_id}")
async def delete_conclusion(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(LegalConclusionModel.conclusion_id == conclusion_id, LegalConclusionModel.user_id == current_user.user_id).first()
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    db.query(PieceModel).filter(PieceModel.conclusion_id == conclusion_id).delete()
    db.delete(conclusion)
    db.commit()
    return {"message": "Conclusion supprimée"}

# Pieces (simplified for serverless - no file storage)
@app.get("/api/conclusions/{conclusion_id}/pieces")
async def get_pieces(conclusion_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conclusion = db.query(LegalConclusionModel).filter(LegalConclusionModel.conclusion_id == conclusion_id, LegalConclusionModel.user_id == current_user.user_id).first()
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    pieces = db.query(PieceModel).filter(PieceModel.conclusion_id == conclusion_id).order_by(PieceModel.numero.asc()).all()
    return [Piece(piece_id=p.piece_id, conclusion_id=p.conclusion_id, user_id=p.user_id, numero=p.numero, nom=p.nom, description=p.description or "", filename=p.filename, original_filename=p.original_filename, file_size=p.file_size, mime_type=p.mime_type, created_at=p.created_at, updated_at=p.updated_at) for p in pieces]

# Handler for Vercel
handler = Mangum(app)
