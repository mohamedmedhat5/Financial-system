from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from models import User


def create_user(data):

    user = User(
        name=data["name"].strip(),

        email=data["email"].strip().lower(),

        password_hash=generate_password_hash(
            data["password"]
        ),

        age=int(data.get("age") or 0),

        occupation_level=data.get("occupation") or "",

        salary=float(data.get("salary") or 0),
    )

    db.session.add(user)

    db.session.commit()

    login_user(user)

    return user


def authenticate(email, password):

    user = User.query.filter_by(
        email=email.strip().lower()
    ).first()

    if user is None:
        return None

    if check_password_hash(
        user.password_hash,
        password
    ):

        login_user(user)

        return user

    return None


def login_user(user):

    session.clear()

    session["user_id"] = user.id


def logout_user():

    session.clear()