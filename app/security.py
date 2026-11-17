from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from jwt.exceptions import InvalidTokenError
from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app import models
from app.database import get_db
CLE_SECRETE = settings.cle_secrete
ALGORITHME = "HS256"
DUREE_VALIDITE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="connexion")
password_hash = PasswordHash.recommended()
def hacher(mdp: str):
    return password_hash.hash(mdp)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
def creer_token(donnees: dict)-> str:
    a_encoder = donnees.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=DUREE_VALIDITE_MINUTES)
    a_encoder.update({"exp": expiration})
    return jwt.encode(a_encoder,CLE_SECRETE,algorithm=ALGORITHME)
def obtenir_utilisateur_actuel(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Décode le badge JWT et renvoie l'utilisateur connecté, ou bloque avec une erreur 401."""
    erreur_identifiants = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Badge d'accès invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CLE_SECRETE, algorithms=[ALGORITHME])
        email: str | None = payload.get("sub")
        if email is None:
            raise erreur_identifiants
    except InvalidTokenError:
        raise erreur_identifiants

    utilisateur = db.query(models.User).filter(models.User.email == email).first()
    if utilisateur is None:
        raise erreur_identifiants
    return utilisateur