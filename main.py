from flask import Flask, request
import controllers.index as indx
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path="")
app.secret_key = os.getenv("KEY")

@app.after_request
def after_request(response):
    response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/',methods=["GET", "POST"])
def index():
    return indx.inicio(request)

@app.route('/salir',methods=["GET"])
def salir():
    return indx.salir()

@app.route('/principal',methods=["GET"])
def principal():
    return indx.principal()

@app.route('/usuarios',methods=["POST"])
def ver_usuarios():
    return indx.ver_usuarios(request)

@app.route('/save_usuarios',methods=["POST"])
def save_usuarios():
    return indx.save_user(request)

@app.route('/edit_usuarios',methods=["POST"])
def edit_usuarios():
    return indx.edit_user(request)

@app.route('/del_usuarios',methods=["POST"])
def del_usuarios():
    return indx.del_user(request)

if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"))