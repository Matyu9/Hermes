from flask import Flask
from flask_socketio import SocketIO
from os import path, getcwd
from json import load

## Database Import
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Utils.Database.base import Base, get_db

## Utils Import
from Utils.verify_maintenance import verify_maintenance

file_path = path.abspath(path.join(getcwd(), "config.json"))  # Trouver le chemin complet du fichier config.json

# Lecture du fichier JSON
with open(file_path, 'r') as file:
    config_data = load(file)  # Ouverture du fichier config.json


app = Flask(__name__)
app.config['SECRET_KEY'] = config_data['modules'][0]['secret_key']
socketio = SocketIO(app, cors_allowed_origins="*")  # Lien entre l'application Flaks et le WebSocket
# app.config['UPLOAD_FOLDER'] = path.abspath(path.join(getcwd(), "static/ProfilePicture/"))

engine_sql = create_engine(
    f"mysql+pymysql://{config_data['database'][0]['username']}:{config_data['database'][0]['password']}@{config_data['database'][0]['address']}:{config_data['database'][0]['port']}/{config_data['database'][0]['name']}",
    pool_size=20,        # Max 10 connexions en parallèle
    max_overflow=40,      # 20 connexions supplémentaires si besoin
    pool_timeout=30,     # Temps max d’attente pour une connexion libre
    pool_recycle=1800    # Ferme et recrée une connexion après 30 min
)

Base.metadata.create_all(engine_sql)

Session = sessionmaker(bind=engine_sql)


# Vérifiacation du mode de maintenance
@app.before_request
def before_req():
    return verify_maintenance(get_db(Session), config_data['modules'][0]['maintenance'])

# Destruction des sessions de DB en fin de req
@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()  # Ferme proprement la connexion pour éviter les fuites

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
