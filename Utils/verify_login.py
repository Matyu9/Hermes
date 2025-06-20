from flask import request, redirect
from pyotp import totp
from werkzeug.exceptions import BadRequestKeyError

# TODO: refactor ce code car utilisation du model User qui n'existe pas dans Hermes (uniquement dispo via API Olympe)
# from Utils.Database.user import User
from Utils.Database.config import Config

def verify_login(database):
    token = request.cookies.get('token')
    try:
        if database.query(User.desactivated).filter(User.token == token).scalar():
            return "desactivated"
    except TypeError:
        return False

    token_validation = database.query(User.id).filter(User.token == token).scalar()
    validation = request.cookies.get('validation')
    validation_from_db = database.query(Config.content).filter(Config.name == "secret_token").scalar()

    return True if token_validation is not None and validation == validation_from_db else False


def verify_A2F(A2F_secret):
    try:
        key = totp.TOTP(A2F_secret)
    except BadRequestKeyError:
        key = totp.TOTP(A2F_secret)

    try: # Utilisation classique via le formulaire
        return key.verify(request.form['a2f-code'].replace(" ", ""))
    except BadRequestKeyError: # Sinon utilisation de l'API
        return key.verify(request.json['dfa_code'].replace(" ", ""))