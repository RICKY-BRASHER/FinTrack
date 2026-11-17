from fastapi import FastAPI,Depends,HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import models,schemas,services,security
from app.database import get_db,engine
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="FinTrack API",
    description="API de gestion de budget personnel et détection d'anomalies",
    version="1.0.3"
)
liste_origines = (
    ["*"]
    if settings.origins_autorisees == "*"
    else [url.strip() for url in settings.origins_autorisees.split(",")]
)

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=liste_origines, # type: ignore
    allow_credentials=liste_origines != ["*"], # type: ignore
    allow_methods=["*"], # type: ignore
    allow_headers=["*"], # type: ignore
)
@app.get("/")
def lire_racine() -> dict[str, str]:
    return {"statut": "en ligne","message": "Bienvenue sur FinTrack API"}
@app.post("/inscription", status_code=201, response_model=schemas.UserResponse)
def inscrire_utilisateur(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Vérifier si l'e-mail existe déjà
    utilisateur_existant = db.query(models.User).filter(models.User.email == user.email).first()
    if utilisateur_existant:
        raise HTTPException(status_code=400, detail="Cet e-mail est déjà utilisé")

    # 2. Hacher le mot de passe et enregistrer le nouvel utilisateur
    mot_de_passe_securise = security.hacher(user.motdepasse)
    nouvel_utilisateur = models.User(nom=user.nom,email=user.email, motdepasse=mot_de_passe_securise)
    db.add(nouvel_utilisateur)
    db.commit()
    db.refresh(nouvel_utilisateur)
    return nouvel_utilisateur


@app.post("/connexion", response_model=schemas.Token)
def connecter_utilisateur(
    formulaire: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm utilise le champ "username" pour recevoir l'e-mail
    utilisateur = db.query(models.User).filter(models.User.email == formulaire.username).first()

    if not utilisateur or not security.verify_password(
        formulaire.password, utilisateur.motdepasse
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # On fabrique le badge JWT contenant l'e-mail de l'utilisateur
    token = security.creer_token(donnees={"sub": utilisateur.email})
    return {"access_token": token, "token_type": "bearer"}
@app.post("/transactions", status_code=201, response_model=schemas.TransactionResult)
async def creer_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db),
                      user_actuel: models.User = Depends(security.obtenir_utilisateur_actuel)):
    montant_eur = await services.conversion(transaction.montant,transaction.devise)
    alerte = None
    if transaction.type_operation == "depense":
        alerte = services.anomalie(
            db,user_actuel.id,transaction.categorie,montant_eur
        )
    donnees_bd = transaction.model_dump(exclude={"devise"})
    donnees_bd["montant"] = montant_eur
    nouvelle_transaction = models.Transaction(**donnees_bd,user_id = user_actuel.id)
    db.add(nouvelle_transaction)
    db.commit()
    db.refresh(nouvelle_transaction)
    return {"transaction": nouvelle_transaction, "anomalie": alerte}
@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def lister_transactions(
    db: Session = Depends(get_db),
    utilisateur_actuel: models.User = Depends(security.obtenir_utilisateur_actuel)
):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == utilisateur_actuel.id)
        .all()
    )
@app.get("/transactions/bilan")
def bilan(
    db: Session = Depends(get_db),
    utilisateur_actuel: models.User = Depends(security.obtenir_utilisateur_actuel)
) -> dict[str, float]:
    return services.bilan_financier(db, utilisateur_actuel.id)
@app.get("/transactions/categories")
def repartition_categories(
        db: Session = Depends(get_db), user_actual: models.User = Depends(security.obtenir_utilisateur_actuel)
)->dict[str, float]:
    return services.analyse_depense(db,user_actual.id)
@app.put("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
## Je dois ameliorer l'affichage de l'anomalie meme quand on met a jour une transaction
def mettre_a_jour_transaction(
    transaction_id: int,
    donnees_maj: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    utilisateur_actuel: models.User = Depends(security.obtenir_utilisateur_actuel)
):
    transaction = services.recup_transaction(db, transaction_id, utilisateur_actuel.id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    return services.modifier_transaction(db, transaction, donnees_maj)


@app.delete("/transactions/{transaction_id}", status_code=204)
def effacer_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    utilisateur_actuel: models.User = Depends(security.obtenir_utilisateur_actuel)
):
    transaction = services.recup_transaction(db, transaction_id, utilisateur_actuel.id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    services.supprimer_transaction(db, transaction)
    return None
