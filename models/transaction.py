from datetime import datetime

from db import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)

    category = db.Column(db.String(100), nullable=False)

    note = db.Column(db.Text)

    amount = db.Column(db.Float, nullable=False)

    type = db.Column(db.String(20), nullable=False)

    currency = db.Column(
        db.String(10),
        default="USD"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="transactions"
    )

    def __repr__(self):
        return f"<Transaction {self.category}>"