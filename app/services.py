from sqlalchemy.orm import Session
from app import models,schemas
import httpx
from fastapi import HTTPException

def recup_transaction(db: Session, transaction_id: int, user_id: int)->models.Transaction | None:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id)
        .first()
    )
def modifier_transaction(db: Session, transaction_bd: models.Transaction,
                         donnees: schemas.TransactionCreate)->models.Transaction | None:
    for cle, valeur in donnees.model_dump().items():
        setattr(transaction_bd,cle,valeur)
    db.commit()
    db.refresh(transaction_bd)
    return transaction_bd
def supprimer_transaction(db: Session, transaction_bd: models.Transaction)-> None:
    db.delete(transaction_bd)
    db.commit()

def bilan_financier(db: Session, user_id: int)-> dict[str,float]:
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    total_revenus = sum(t.montant for t in transactions if t.type_operation == "revenu")
    total_depenses = sum(t.montant for t in transactions if t.type_operation == "depense")
    solde = total_revenus - total_depenses
    return {
        "total_revenus": round(total_revenus, 2),
        "total_depenses": round(total_depenses, 2),
        "solde": round(solde, 2),
    }
def anomalie(
        db: Session, user_id: int, categorie: str, new_montant: float
)->str | None:

    last_depense = (db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type_operation == "depense",
        models.Transaction.categorie == categorie
    ).all())
    if len(last_depense) < 2:
        return None
    moyenne = sum(d.montant for d in last_depense) / len(last_depense)
    if new_montant > (moyenne * 2):
        return (
            f"Nouvelle depense inhabituelle qui depasse les standards habituels"
        )
    return None

def analyse_depense(db: Session, user_id: int)->dict[str,float]:
    depenses = (db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type_operation == "depense",
    ).all())
    repartition: dict[str,float] = {}
    for d in depenses:
        repartition[d.categorie] = round(repartition.get(d.categorie,0.0) + d.montant, 2)
    return repartition

async def conversion(montant: float, devise: str)->float:
    devise_propre = devise.upper().strip()
    if devise_propre == "EUR":
        return montant
    url = f"https://frankfurter.app/latest?amount={montant}&from={devise_propre}&to=EUR"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            reponse = await client.get(url)
            reponse.raise_for_status()
            donnees = reponse.json()
            return round(donnees["rates"]["EUR"],2)
        except httpx.HTTPError:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de convertir la devise '{devise_propre}'. Verifier le code ISO(USD,CAD,GBP,XOF)"
            )