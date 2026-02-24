from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
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

    loans: Mapped[List["Loan"]] = db.relationship(
        back_populates="member"
    )  # relationship attribute to link to the Loan model


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date] = mapped_column(db.Date)
    member_id: Mapped[int] = mapped_column(db.ForeignKey("members.id"))

    member: Mapped["Member"] = db.relationship(
        back_populates="loans"
    )  # relationship attribute to link to the Member model
    books: Mapped[List["Book"]] = db.relationship(
        "Book", secondary="loan_books", back_populates="loans"
    )  # relationship attribute to link to the Book model through the association table


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(255), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)

    loans: Mapped[List["Loan"]] = db.relationship(
        "Loan", secondary="loan_books", back_populates="books"
    )  # relationship attribute to link to the Loan model through the association table
