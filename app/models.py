from datetime import datetime
from sqlalchemy import String,Float,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    motdepasse: Mapped[str] = mapped_column(String(50), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="proprietaire")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    titre: Mapped[str] = mapped_column(String(100), nullable=False)
    montant: Mapped[float] = mapped_column(Float,nullable=False)
    type_operation: Mapped[str] = mapped_column(String(20), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    proprietaire: Mapped["User"] = relationship(back_populates="transactions")