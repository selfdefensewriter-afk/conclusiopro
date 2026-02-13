from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Float, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta
import uuid
import secrets

# Database
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None
Base = declarative_base()

# Models
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    picture = Column(Text)
    credits = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class UserSessionModel(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class LegalConclusionModel(Base):
    __tablename__ = "legal_conclusions"
    id = Column(Integer, primary_key=True)
    conclusion_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    parties = Column(JSON)
    faits = Column(Text)
    demandes = Column(Text)
    conclusion_text = Column(Text)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

if engine:
    Base.metadata.create_all(bind=engine)

def get_user_from_token(token, db):
    session = db.query(UserSessionModel).filter(UserSessionModel.session_token == token).first()
    if not session:
        return None
    if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return None
    user = db.query(UserModel).filter(UserModel.user_id == session.user_id).first()
    return user

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}).encode())
            return
        
        if path == '/api/auth/google/login':
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            redirect_uri = os.environ.get('BACKEND_URL', '') + '/api/auth/google/callback'
            scope = 'openid email profile'
            google_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
            
            self.send_response(302)
            self.send_header('Location', google_url)
            self.end_headers()
            return
        
        if path == '/api/auth/google/callback':
            # Handle OAuth callback
            query = parse_qs(parsed.query)
            code = query.get('code', [None])[0]
            
            if code:
                import urllib.request
                import urllib.parse
                
                # Exchange code for token
                token_url = 'https://oauth2.googleapis.com/token'
                data = urllib.parse.urlencode({
                    'code': code,
                    'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                    'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
                    'redirect_uri': os.environ.get('BACKEND_URL', '') + '/api/auth/google/callback',
                    'grant_type': 'authorization_code'
                }).encode()
                
                try:
                    req = urllib.request.Request(token_url, data=data, method='POST')
                    with urllib.request.urlopen(req) as response:
                        token_data = json.loads(response.read().decode())
                    
                    # Get user info
                    access_token = token_data.get('access_token')
                    userinfo_req = urllib.request.Request(
                        'https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    with urllib.request.urlopen(userinfo_req) as response:
                        user_info = json.loads(response.read().decode())
                    
                    # Create or update user
                    db = SessionLocal()
                    try:
                        user = db.query(UserModel).filter(UserModel.email == user_info['email']).first()
                        if user:
                            user.name = user_info.get('name', '')
                            user.picture = user_info.get('picture')
                        else:
                            user = UserModel(
                                user_id=f"user_{uuid.uuid4().hex[:12]}",
                                email=user_info['email'],
                                name=user_info.get('name', ''),
                                picture=user_info.get('picture'),
                                credits=0
                            )
                            db.add(user)
                        db.commit()
                        
                        # Create session
                        session_token = secrets.token_urlsafe(32)
                        new_session = UserSessionModel(
                            user_id=user.user_id,
                            session_token=session_token,
                            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
                        )
                        db.add(new_session)
                        db.commit()
                        
                        frontend_url = os.environ.get('FRONTEND_URL', '')
                        self.send_response(302)
                        self.send_header('Location', f"{frontend_url}/dashboard")
                        self.send_header('Set-Cookie', f"session_token={session_token}; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=604800")
                        self.end_headers()
                        return
                    finally:
                        db.close()
                except Exception as e:
                    frontend_url = os.environ.get('FRONTEND_URL', '')
                    self.send_response(302)
                    self.send_header('Location', f"{frontend_url}?error=auth_failed")
                    self.end_headers()
                    return
            
            frontend_url = os.environ.get('FRONTEND_URL', '')
            self.send_response(302)
            self.send_header('Location', f"{frontend_url}?error=no_code")
            self.end_headers()
            return
        
        if path == '/api/auth/me':
            cookies = self.headers.get('Cookie', '')
            token = None
            for cookie in cookies.split(';'):
                if 'session_token=' in cookie:
                    token = cookie.split('=')[1].strip()
                    break
            
            if not token:
                auth = self.headers.get('Authorization', '')
                if auth.startswith('Bearer '):
                    token = auth[7:]
            
            if not token:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Non authentifié"}).encode())
                return
            
            db = SessionLocal()
            try:
                user = get_user_from_token(token, db)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "Session invalide"}).encode())
                    return
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "user_id": user.user_id,
                    "email": user.email,
                    "name": user.name or "",
                    "picture": user.picture,
                    "credits": user.credits,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }).encode())
            finally:
                db.close()
            return
        
        if path == '/api/conclusions':
            cookies = self.headers.get('Cookie', '')
            token = None
            for cookie in cookies.split(';'):
                if 'session_token=' in cookie:
                    token = cookie.split('=')[1].strip()
                    break
            
            if not token:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Non authentifié"}).encode())
                return
            
            db = SessionLocal()
            try:
                user = get_user_from_token(token, db)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "Session invalide"}).encode())
                    return
                
                conclusions = db.query(LegalConclusionModel).filter(
                    LegalConclusionModel.user_id == user.user_id
                ).order_by(LegalConclusionModel.created_at.desc()).all()
                
                result = [{
                    "conclusion_id": c.conclusion_id,
                    "user_id": c.user_id,
                    "type": c.type,
                    "parties": c.parties or {},
                    "faits": c.faits or "",
                    "demandes": c.demandes or "",
                    "conclusion_text": c.conclusion_text or "",
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None
                } for c in conclusions]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            finally:
                db.close()
            return
        
        # Default 404
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"detail": "Not found"}).encode())
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        if path == '/api/conclusions':
            cookies = self.headers.get('Cookie', '')
            token = None
            for cookie in cookies.split(';'):
                if 'session_token=' in cookie:
                    token = cookie.split('=')[1].strip()
                    break
            
            if not token:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Non authentifié"}).encode())
                return
            
            db = SessionLocal()
            try:
                user = get_user_from_token(token, db)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "Session invalide"}).encode())
                    return
                
                now = datetime.now(timezone.utc)
                conclusion = LegalConclusionModel(
                    conclusion_id=f"concl_{uuid.uuid4().hex[:12]}",
                    user_id=user.user_id,
                    type=data.get('type', ''),
                    parties=data.get('parties', {}),
                    faits=data.get('faits', ''),
                    demandes=data.get('demandes', ''),
                    conclusion_text='',
                    status='draft',
                    created_at=now,
                    updated_at=now
                )
                db.add(conclusion)
                db.commit()
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "conclusion_id": conclusion.conclusion_id,
                    "user_id": conclusion.user_id,
                    "type": conclusion.type,
                    "parties": conclusion.parties or {},
                    "faits": conclusion.faits or "",
                    "demandes": conclusion.demandes or "",
                    "conclusion_text": conclusion.conclusion_text or "",
                    "status": conclusion.status,
                    "created_at": conclusion.created_at.isoformat(),
                    "updated_at": conclusion.updated_at.isoformat()
                }).encode())
            finally:
                db.close()
            return
        
        if path == '/api/auth/logout':
            cookies = self.headers.get('Cookie', '')
            token = None
            for cookie in cookies.split(';'):
                if 'session_token=' in cookie:
                    token = cookie.split('=')[1].strip()
                    break
            
            if token and SessionLocal:
                db = SessionLocal()
                try:
                    db.query(UserSessionModel).filter(UserSessionModel.session_token == token).delete()
                    db.commit()
                finally:
                    db.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Set-Cookie', 'session_token=; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=0')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Déconnexion réussie"}).encode())
            return
        
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"detail": "Not found"}).encode())
