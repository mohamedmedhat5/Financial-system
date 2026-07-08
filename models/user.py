from datetime import datetime

from db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    age = db.Column(db.Integer)

    country = db.Column(db.String(100))

    occupation_level = db.Column(db.String(100))

    salary = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    transactions = db.relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def get_id(self):
        return str(self.id)