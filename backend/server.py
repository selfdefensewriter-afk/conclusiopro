from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import io
import json
import aiofiles
import shutil
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

# MongoDB connection with SSL fix
import certifi
import ssl

mongo_url = os.environ['MONGO_URL']

# Create SSL context that works with MongoDB Atlas
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = AsyncIOMotorClient(
    mongo_url,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000
)
db = client[os.environ['DB_NAME']]

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

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    credits: int = 0
    created_at: datetime

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
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

class CodeCivilArticle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    article_id: str
    numero: str
    titre: str
    contenu: str
    categorie: str

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

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    transaction_id: str
    user_id: str
    session_id: str
    amount: float
    currency: str
    package_id: str
    payment_status: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# Fixed packages - NEVER accept amounts from frontend
PACKAGES = {
    "essentielle": {
        "price": 29.0,
        "currency": "eur",
        "name": "Offre Essentielle",
        "credits": 1
    }
}

# Authentication Helper
async def get_current_user(request: Request) -> User:
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expirée")
    
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return User(**user_doc)

# Auth Routes - Google OAuth
@api_router.get("/auth/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro-frontend.onrender.com')
    redirect_uri = os.environ.get('BACKEND_URL', str(request.base_url).rstrip('/')) + '/api/auth/google/callback'
    
    # Store the frontend URL in session for redirect after auth
    request.session['frontend_redirect'] = frontend_url + '/dashboard'
    
    return await oauth.google.authorize_redirect(request, redirect_uri)

@api_router.get("/auth/google/callback")
async def google_callback(request: Request, response: Response):
    """Handle Google OAuth callback"""
    try:
        logger.info("OAuth callback received")
        token = await oauth.google.authorize_access_token(request)
        logger.info(f"Token received: {bool(token)}")
        
        user_info = token.get('userinfo')
        if not user_info:
            # Try to get from id_token
            user_info = token.get('id_token')
            if not user_info:
                logger.error("No user info in token")
                raise HTTPException(status_code=400, detail="Could not get user info")
        
        logger.info(f"User info: {user_info.get('email', 'no email')}")
        
        # Find or create user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        existing_user = await db.users.find_one(
            {"email": user_info["email"]},
            {"_id": 0}
        )
        
        if existing_user:
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture")
                }}
            )
            logger.info(f"User updated: {user_id}")
        else:
            user_doc = {
                "user_id": user_id,
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture"),
                "credits": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user_doc)
            logger.info(f"User created: {user_id}")
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.user_sessions.insert_one(session_doc)
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
        frontend_url = os.environ.get('FRONTEND_URL', 'https://conclusiopro-frontend.onrender.com')
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed", status_code=302)

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, current_user: User = Depends(get_current_user)):
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", samesite="none", secure=True)
    return {"message": "Déconnexion réussie"}

# Code Civil Routes
@api_router.get("/code-civil/search")
async def search_code_civil(q: str, current_user: User = Depends(get_current_user)):
    articles = await db.code_civil_articles.find(
        {
            "$or": [
                {"titre": {"$regex": q, "$options": "i"}},
                {"contenu": {"$regex": q, "$options": "i"}},
                {"numero": {"$regex": q, "$options": "i"}}
            ]
        },
        {"_id": 0}
    ).limit(20).to_list(20)
    
    return articles

@api_router.get("/code-civil/articles")
async def get_all_articles(category: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if category:
        query["categorie"] = category
    
    articles = await db.code_civil_articles.find(query, {"_id": 0}).to_list(1000)
    return articles

# Templates Routes
@api_router.get("/templates")
async def get_templates(type: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if type:
        query["type"] = type
    
    templates = await db.conclusion_templates.find(query, {"_id": 0}).to_list(100)
    return [ConclusionTemplate(**t) for t in templates]

@api_router.get("/templates/{template_id}")
async def get_template(template_id: str, current_user: User = Depends(get_current_user)):
    template = await db.conclusion_templates.find_one(
        {"template_id": template_id},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    
    return ConclusionTemplate(**template)

# Payment Routes
@api_router.post("/payments/create-checkout")
async def create_checkout(
    data: CheckoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
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
    
    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
    transaction_doc = {
        "transaction_id": transaction_id,
        "user_id": current_user.user_id,
        "session_id": session.session_id,
        "amount": package["price"],
        "currency": package["currency"],
        "package_id": data.package_id,
        "payment_status": "pending",
        "metadata": checkout_request.metadata,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.payment_transactions.insert_one(transaction_doc)
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request, current_user: User = Depends(get_current_user)):
    stripe_api_key = os.environ.get('STRIPE_API_KEY')
    
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    base_url = os.environ.get('BACKEND_URL', str(request.base_url).rstrip('/'))
    webhook_url = f"{base_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
    
    transaction = await db.payment_transactions.find_one(
        {"session_id": session_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    if checkout_status.payment_status == "paid" and transaction["payment_status"] != "paid":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "payment_status": "paid",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        package = PACKAGES.get(transaction["package_id"], {})
        credits = package.get("credits", 1)
        
        await db.users.update_one(
            {"user_id": current_user.user_id},
            {"$inc": {"credits": credits}}
        )
    
    return {
        "status": checkout_status.status,
        "payment_status": checkout_status.payment_status,
        "amount": checkout_status.amount_total / 100,
        "currency": checkout_status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
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
            transaction = await db.payment_transactions.find_one(
                {"session_id": webhook_response.session_id},
                {"_id": 0}
            )
            
            if transaction and transaction["payment_status"] != "paid":
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {
                        "payment_status": "paid",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                user_id = webhook_response.metadata.get("user_id")
                package_id = webhook_response.metadata.get("package_id")
                
                if user_id and package_id:
                    package = PACKAGES.get(package_id, {})
                    credits = package.get("credits", 1)
                    
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$inc": {"credits": credits}}
                    )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Conclusions Routes
@api_router.post("/conclusions", status_code=201)
async def create_conclusion(data: ConclusionCreateRequest, current_user: User = Depends(get_current_user)):
    conclusion_id = f"concl_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    conclusion_doc = {
        "conclusion_id": conclusion_id,
        "user_id": current_user.user_id,
        "type": data.type,
        "parties": data.parties,
        "faits": data.faits,
        "demandes": data.demandes,
        "conclusion_text": "",
        "status": "draft",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await db.legal_conclusions.insert_one(conclusion_doc)
    
    conclusion_doc['created_at'] = now
    conclusion_doc['updated_at'] = now
    
    return LegalConclusion(**conclusion_doc)

@api_router.get("/conclusions")
async def get_conclusions(current_user: User = Depends(get_current_user)):
    conclusions = await db.legal_conclusions.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    for c in conclusions:
        if isinstance(c['created_at'], str):
            c['created_at'] = datetime.fromisoformat(c['created_at'])
        if isinstance(c['updated_at'], str):
            c['updated_at'] = datetime.fromisoformat(c['updated_at'])
    
    return [LegalConclusion(**c) for c in conclusions]

@api_router.get("/conclusions/{conclusion_id}")
async def get_conclusion(conclusion_id: str, current_user: User = Depends(get_current_user)):
    conclusion = await db.legal_conclusions.find_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    if isinstance(conclusion['created_at'], str):
        conclusion['created_at'] = datetime.fromisoformat(conclusion['created_at'])
    if isinstance(conclusion['updated_at'], str):
        conclusion['updated_at'] = datetime.fromisoformat(conclusion['updated_at'])
    
    return LegalConclusion(**conclusion)

@api_router.put("/conclusions/{conclusion_id}")
async def update_conclusion(
    conclusion_id: str,
    data: ConclusionUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if data.conclusion_text is not None:
        update_data["conclusion_text"] = data.conclusion_text
    if data.status is not None:
        update_data["status"] = data.status
    
    result = await db.legal_conclusions.update_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    conclusion = await db.legal_conclusions.find_one(
        {"conclusion_id": conclusion_id},
        {"_id": 0}
    )
    
    if isinstance(conclusion['created_at'], str):
        conclusion['created_at'] = datetime.fromisoformat(conclusion['created_at'])
    if isinstance(conclusion['updated_at'], str):
        conclusion['updated_at'] = datetime.fromisoformat(conclusion['updated_at'])
    
    return LegalConclusion(**conclusion)

@api_router.delete("/conclusions/{conclusion_id}")
async def delete_conclusion(conclusion_id: str, current_user: User = Depends(get_current_user)):
    result = await db.legal_conclusions.delete_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    # Also delete all pieces associated with this conclusion
    pieces = await db.pieces.find(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    ).to_list(1000)
    
    for piece in pieces:
        file_path = UPLOADS_DIR / piece["filename"]
        if file_path.exists():
            file_path.unlink()
    
    await db.pieces.delete_many({"conclusion_id": conclusion_id})
    
    return {"message": "Conclusion supprimée"}

# Pieces Routes
@api_router.post("/conclusions/{conclusion_id}/pieces", status_code=201)
async def upload_piece(
    conclusion_id: str,
    file: UploadFile = File(...),
    nom: str = Form(...),
    description: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    # Verify conclusion exists and belongs to user
    conclusion = await db.legal_conclusions.find_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 10 Mo")
    
    # Get next piece number
    last_piece = await db.pieces.find_one(
        {"conclusion_id": conclusion_id},
        sort=[("numero", -1)]
    )
    next_numero = (last_piece["numero"] + 1) if last_piece else 1
    
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
    
    piece_doc = {
        "piece_id": piece_id,
        "conclusion_id": conclusion_id,
        "user_id": current_user.user_id,
        "numero": next_numero,
        "nom": nom,
        "description": description,
        "filename": unique_filename,
        "original_filename": file.filename or "fichier",
        "file_size": file_size,
        "mime_type": file.content_type or "application/octet-stream",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await db.pieces.insert_one(piece_doc)
    
    piece_doc['created_at'] = now
    piece_doc['updated_at'] = now
    
    return Piece(**piece_doc)

@api_router.get("/conclusions/{conclusion_id}/pieces")
async def get_pieces(conclusion_id: str, current_user: User = Depends(get_current_user)):
    # Verify conclusion exists and belongs to user
    conclusion = await db.legal_conclusions.find_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    pieces = await db.pieces.find(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    ).sort("numero", 1).to_list(1000)
    
    for p in pieces:
        if isinstance(p['created_at'], str):
            p['created_at'] = datetime.fromisoformat(p['created_at'])
        if isinstance(p['updated_at'], str):
            p['updated_at'] = datetime.fromisoformat(p['updated_at'])
    
    return [Piece(**p) for p in pieces]

# IMPORTANT: Reorder route must be defined BEFORE {piece_id} routes to avoid route collision
@api_router.put("/conclusions/{conclusion_id}/pieces/reorder")
async def reorder_pieces(
    conclusion_id: str,
    data: PieceReorderRequest,
    current_user: User = Depends(get_current_user)
):
    # Verify conclusion exists and belongs to user
    conclusion = await db.legal_conclusions.find_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    # Update piece numbers based on new order
    for idx, piece_id in enumerate(data.piece_ids, start=1):
        await db.pieces.update_one(
            {"piece_id": piece_id, "conclusion_id": conclusion_id, "user_id": current_user.user_id},
            {"$set": {"numero": idx, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    # Return updated pieces
    pieces = await db.pieces.find(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    ).sort("numero", 1).to_list(1000)
    
    for p in pieces:
        if isinstance(p['created_at'], str):
            p['created_at'] = datetime.fromisoformat(p['created_at'])
        if isinstance(p['updated_at'], str):
            p['updated_at'] = datetime.fromisoformat(p['updated_at'])
    
    return [Piece(**p) for p in pieces]

@api_router.put("/conclusions/{conclusion_id}/pieces/{piece_id}")
async def update_piece(
    conclusion_id: str,
    piece_id: str,
    data: PieceUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if data.nom is not None:
        update_data["nom"] = data.nom
    if data.description is not None:
        update_data["description"] = data.description
    
    result = await db.pieces.update_one(
        {"piece_id": piece_id, "conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    piece = await db.pieces.find_one({"piece_id": piece_id}, {"_id": 0})
    
    if isinstance(piece['created_at'], str):
        piece['created_at'] = datetime.fromisoformat(piece['created_at'])
    if isinstance(piece['updated_at'], str):
        piece['updated_at'] = datetime.fromisoformat(piece['updated_at'])
    
    return Piece(**piece)

@api_router.delete("/conclusions/{conclusion_id}/pieces/{piece_id}")
async def delete_piece(
    conclusion_id: str,
    piece_id: str,
    current_user: User = Depends(get_current_user)
):
    piece = await db.pieces.find_one(
        {"piece_id": piece_id, "conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    # Delete file
    file_path = UPLOADS_DIR / piece["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Delete record
    await db.pieces.delete_one({"piece_id": piece_id})
    
    # Renumber remaining pieces
    remaining_pieces = await db.pieces.find(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    ).sort("numero", 1).to_list(1000)
    
    for idx, p in enumerate(remaining_pieces, start=1):
        if p["numero"] != idx:
            await db.pieces.update_one(
                {"piece_id": p["piece_id"]},
                {"$set": {"numero": idx, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
    
    return {"message": "Pièce supprimée"}

@api_router.get("/pieces/{piece_id}/download")
async def download_piece(piece_id: str, current_user: User = Depends(get_current_user)):
    piece = await db.pieces.find_one(
        {"piece_id": piece_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    file_path = UPLOADS_DIR / piece["filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    return FileResponse(
        path=str(file_path),
        filename=piece["original_filename"],
        media_type=piece["mime_type"]
    )

# AI Generation Route
@api_router.post("/generate/conclusion")
async def generate_conclusion(
    data: GenerateConclusionRequest,
    current_user: User = Depends(get_current_user)
):
    user_doc = await db.users.find_one(
        {"user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not user_doc or user_doc.get("credits", 0) <= 0:
        raise HTTPException(
            status_code=403, 
            detail="Crédits insuffisants. Veuillez acheter des crédits pour générer une conclusion."
        )
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Clé API non configurée")
    
    relevant_articles = await db.code_civil_articles.find(
        {"categorie": "famille" if data.type == "jaf" else "penal"},
        {"_id": 0}
    ).limit(5).to_list(5)
    
    articles_context = "\n".join([
        f"Article {art['numero']} - {art['titre']}:\n{art['contenu']}"
        for art in relevant_articles
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
    
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$inc": {"credits": -1}}
    )
    
    return {"conclusion_text": response, "credits_used": 1}

# PDF Export Route
@api_router.get("/conclusions/{conclusion_id}/pdf")
async def export_pdf(conclusion_id: str, current_user: User = Depends(get_current_user)):
    conclusion = await db.legal_conclusions.find_one(
        {"conclusion_id": conclusion_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    
    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion non trouvée")
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 14)
    y = height - 2*cm
    p.drawString(2*cm, y, f"CONCLUSIONS - {conclusion['type'].upper()}")
    
    y -= 1.5*cm
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y, f"Généré le {datetime.now(timezone.utc).strftime('%d/%m/%Y')}")
    
    y -= 2*cm
    p.setFont("Helvetica", 11)
    
    text = conclusion['conclusion_text']
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

# Health check endpoint for Railway
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()