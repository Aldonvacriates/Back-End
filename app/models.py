from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date
from typing import List


# Create a base class for our models
class Base(DeclarativeBase):
    pass


# Instantiate your SQLAlchemy database
db = SQLAlchemy(model_class=Base)


loan_book = db.Table(
    "loan_books",
    Base.metadata,
    db.Column("loan_id", db.Integer, db.ForeignKey("loans.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("books.id")),
)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    DOB: Mapped[date] = mapped_column(db.Date, nullable=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date] = mapped_column(db.Date)
    member_id: Mapped[int] = mapped_column(db.ForeignKey("members.id"))

    member: Mapped["Member"] = relationship(back_populates="loans")
    books: Mapped[List["Book"]] = relationship(
        "Book", secondary="loan_books", back_populates="loans"
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(255), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = relationship(
        "Loan", secondary="loan_books", back_populates="books"
    )
