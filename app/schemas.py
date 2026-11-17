## Gestionnaire des protections et Transcriptions des requetes venant des interfaces
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from typing import Literal

class UserCreate(BaseModel):
    nom: str = Field(...,min_length=2,max_length=50)
    email: EmailStr
    motdepasse: str = Field(...,min_length=4,max_length=50, description="Au Moins 04 Caracteres")

class UserResponse(BaseModel):
    id: int
    nom: str
    email: EmailStr
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)

class  Token(BaseModel):
    access_token: str
    token_type: str

class TransactionCreate(BaseModel):
    titre:str = Field(...,min_length=2,max_length=100)
    montant:float = Field(...,gt=0)
    devise: str = Field(default="EUR", min_length=3,max_length=3, description="Code Devise (ex: EUR,XOF,XAF,USD,CAD)")
    type_operation: Literal["revenu","depense"]
    categorie:str = Field(...,min_length=2,max_length=50)

class TransactionResponse(TransactionCreate):
    id:int
    date_creation:datetime
    model_config = ConfigDict(from_attributes=True)

class TransactionResult(BaseModel):
    transaction: TransactionResponse
    anomalie: str | None = None