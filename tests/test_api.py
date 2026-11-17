import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# 1. Configuration d'une base de données SQLite dédiée uniquement aux tests
URL_BDD_TEST = "sqlite:///./test_fintrack.db"
engine_test = create_engine(URL_BDD_TEST, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# On remplace la vraie base de données par celle de test
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def preparer_bdd_propre():
    """Recrée des tables vierges avant chaque test et supprime le fichier après."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    engine_test.dispose()
    if os.path.exists("./test_fintrack.db"):
        os.remove("./test_fintrack.db")


def test_route_racine():
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "en ligne"


def test_acces_refuse_sans_token():
    reponse = client.get("/transactions")
    assert reponse.status_code == 401


def test_inscription_connexion_et_transaction():
    # 1. Inscription d'un utilisateur de test
    res_inscription = client.post(
        "/inscription",
        json={"nom": "TestUser", "email": "test@fintrack.com", "motdepasse": "password123"}
    )
    assert res_inscription.status_code == 201
    assert "motdepasse" not in res_inscription.json()  # Vérifie que le mot de passe est bien masqué !

    # 2. Connexion pour récupérer le badge JWT
    res_connexion = client.post(
        "/connexion",
        data={"username": "test@fintrack.com", "password": "password123"}
    )
    assert res_connexion.status_code == 200
    token = res_connexion.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Création d'une transaction protégée
    res_tx = client.post(
        "/transactions",
        json={"titre": "Salaire", "montant": 2500.0, "type_operation": "revenu", "categorie": "Travail"},
        headers=headers
    )
    assert res_tx.status_code == 201
    assert res_tx.json()["transaction"]["montant"] == 2500.0

    # 4. Vérification du bilan financier
    res_bilan = client.get("/transactions/bilan", headers=headers)
    assert res_bilan.status_code == 200
    assert res_bilan.json()["solde"] == 2500.0
