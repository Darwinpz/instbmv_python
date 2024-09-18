from flask import render_template,abort,session, redirect, url_for, jsonify
from database.mongodb import MongoDb
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os, json
from models.user import User

import controllers.ctl_encrypt as ctl_encrypt

load_dotenv()

db = MongoDb().db()

def inicio(request):

    try:

        alertas = {"tipo":"","message":""}

        if request.method == "GET":
            if "id" in session:
                return redirect(url_for("principal"))
            else:
                return render_template("/views/index.html")
        else:
            usuario = request.form["usuario"]
            clave = request.form["clave"]

            if usuario != "" and clave !="":

                if usuario == os.getenv("USER_ADMIN") and clave == os.getenv("USER_PASSWORD"):
                    session["id"] = ObjectId().__str__()
                    session["rol"] = "Administrador"
                    session["usuario"] = "admin"    
                    return redirect(url_for("principal"))
                else:
                    
                    existe = db.users.find_one({"$and":[{"usuario":usuario}]})

                    if existe:
                        if ctl_encrypt.decrypt(existe["clave"]) == clave:
                            session["id"] = str(existe["_id"])
                            session["rol"] = existe["rol"]
                            session["usuario"] = existe["usuario"]
                            return redirect(url_for("principal"))
                    
                    alertas["tipo"] = "danger"
                    alertas["message"] = "Usuario o Clave incorrecto"
            else:
                alertas["tipo"] = "warning"
                alertas["message"] = "Campos incompletos"
            return render_template("/views/index.html", alertas=alertas)
    except Exception as e:
        abort(500)

def principal():
    if "id" in session:
        return render_template("/views/principal.html")
    else:
        return redirect(url_for("index"))
    
def ver_usuarios(request):
    if request.method == 'POST':
        usuarios = db.users.find({ "usuario": { "$nin": [session["usuario"]] } })
        datos_usuarios = list(usuarios)
        for users in datos_usuarios:
            users["clave"] = ctl_encrypt.decrypt(users["clave"])

        datos = {"data":datos_usuarios}
        return json.dumps(datos, default=str), 200
    else:
        return jsonify({"message":"Petición Incorrecta"}), 500
    
def save_user(request):
    if request.method == 'POST':

        cedula = request.form["u_cedula"]
        nombre = request.form["u_nombre"]
        usuario = request.form["u_usuario"]
        clave = request.form["u_clave"]
        rol = request.form["u_rol"]

        existe = db.users.find_one({"$or":[{"cedula":cedula},{"usuario":usuario}]})

        if existe:
            return jsonify({"message":"Usuario Existente"}), 404
        else:
            clave = ctl_encrypt.encrypt(clave)
            usuario = User(cedula,nombre,usuario,clave,rol)
            usuario.crear_usuario()
            db.users.insert_one(usuario.obtener_user())
            return jsonify({"message":"Usuario creado correctamente"}), 200

    else:
        return jsonify({"message":"Petición Incorrecta"}), 500
    

def edit_user(request):
    if request.method == 'POST':

        cedula = request.form["u_cedula"]
        nombre = request.form["u_nombre"]
        usuario = request.form["u_usuario"]
        clave = request.form["u_clave"]
        rol = request.form["u_rol"]

        existe = db.users.find_one({"$or":[{"cedula":cedula},{"usuario":usuario}]})

        if existe:
            clave = ctl_encrypt.encrypt(clave)
            usuario = User(cedula,nombre,usuario,clave,rol)
            usuario.update_usuario()
            db.users.update_one({"_id":ObjectId(existe["_id"])},
                                {"$set":usuario.obtener_user()})
            return jsonify({"message":"Usuario Actualizado correctamente"}), 200
        else:
            return jsonify({"message":"Usuario No Existente"}), 404
            
    else:
        return jsonify({"message":"Petición Incorrecta"}), 500
    

def del_user(request):
    if request.method == 'POST':
        
        try:
            if "id" in session:
                cedula = request.form["u_cedula"]
                existe = db.users.find_one({"cedula":cedula})

                if existe:
                    db.users.delete_one({"cedula":cedula})
                    return jsonify({"message":"Usuario Eliminado correctamente"}), 200
                else:
                    return jsonify({"message":"Usuario No Existente"}), 404
            else:
                return jsonify({"message":"Usuario Sin Permiso"}), 500  
        except Exception as e:
            return jsonify({"message":"Error: " + str(e)}), 500  
    else:
        return jsonify({"message":"Petición Incorrecta"}), 500
    

def salir():
    if "id" in session:
        session.pop("id", None)
        session.pop("rol", None)
        session.pop("usuario",None)
        return redirect(url_for("index"))
    else:
        abort(403)