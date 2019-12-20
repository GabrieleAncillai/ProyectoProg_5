# Integrantes del grupo:
# Gabriele Ancillai  YB0415159
# Juan García 093926238

import mimetypes
import smtplib  # import necessary packages for MAILS
import qrcode  # import necessary packages for making QRCodes
import os
import datetime
# For flask implementation
from flask import Flask, render_template, request, redirect, url_for, session
from bson import ObjectId  # For ObjectId to work
from pymongo import MongoClient

app = Flask(__name__)

# title = "Proyecto Programación 5"

client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
# This is still not working
# client = MongoClient("mongodb+srv://GabrieleAncillai:Gabriele25@ancillai-bay7d.mongodb.net/test?retryWrites=true&w=majority")
db = client.Prog_5  # Select the database

# Collections
Users = db.Users  # collection Usuarios
Accounts = db.Accounts  # collection Eventos


def redirect_url():
    return request.args.get('next') or \
        request.referrer or \
        url_for('index')


app.secret_key = 'Kira'


# ------------------------------- Renders -------------------------------
@app.route("/")
@app.route("/registro")
def render_register():
    return render_template('register.html')


@app.route("/login")
def render_login():
    return render_template('login.html', ERROR=False)


# ------------------------------- Funciones de Registro y Login -------------------------------
@app.route("/handleRegister", methods=['POST'])
def register():
    # Creating a user
    username = request.values.get("username")
    password = request.values.get("password")
    mail = request.values.get("mail")

    Users.insert({
        "username": username,
        "password": password,
        "mail": mail
    })
    return redirect("/login")


@app.route("/handleLogin", methods=['GET'])
def login():
    ID = request.values.get("username")
    key = request.values.get("password")

    # Comprobar que existe el usuario
    DATA = Users.find_one({"username": ID, "password": key})
    if DATA != None:
        session["username"] = DATA["username"]
        app.secret_key = DATA["password"]
        print(session)
        action = redirect("/home")
    else:
        # ERROR
        print("ERROR")
        action = render_template("login.html", ERROR=True)

    return action


@app.route("/logout")
def logout():

    # Delete current session
    session = None
    app.secret_key = ""

    return redirect("/acceso")

# ------------------------------- Componentes de tabla de opciones superior -------------------------------
@app.route("/home", methods=['GET'])  # Home
def home():
    MyUser = list(Users.find(
        {"username": session['username'], "password": app.secret_key}))
    for user in MyUser:
        AllAccounts = list(Accounts.find(
            {"UserID": user["username"] + user["password"]}))

    print(AllAccounts)

    return render_template('home.html', AllAccounts=AllAccounts, MyUser=MyUser)


@app.route("/AddAccount")
def AddAccount():
    return render_template('AddAccount.html')


@app.route("/EditAccount")
def EditAccount():
    AccountID = request.values.get("AccountID")
    Item = list(Accounts.find({"_id": ObjectId(AccountID)}))
    print("AccountID: ", AccountID)
    print("item: ", Item)
    return render_template('EditAccount.html', Item=Item, AccountID=AccountID)

# ------------------------------- ACCOUNTS ACTIONS -------------------------------


@app.route("/InsertAccount", methods=['POST'])
def InsertAccount():
    # Inserting an Account
    title = request.values.get("title")
    details = request.values.get("details")
    image = request.values.get("image")
    _type = request.values.get("_type")
    username = request.values.get("username")
    mail = request.values.get("mail")
    password = request.values.get("password")
    UserID = session["username"] + app.secret_key

    Accounts.insert({
        "title": title,
        "details": details,
        "image": image,
        "_type": _type,
        "username": username,
        "mail": mail,
        "password": password,
        "UserID": UserID
    })

    return redirect("/home")


@app.route("/RemoveAccount")
def removeAccount():
    # Deleting a Task with various references
    ID = request.values.get("AccountID")
    Accounts.remove({"_id": ObjectId(ID)})
    return redirect("/home")


@app.route("/UpdateAccount", methods=['POST'])
def UpdateAccount():
    # Updating a Task with various references
    AccountID = request.values.get("AccountID")
    title = request.values.get("title")
    details = request.values.get("details")
    _type = request.values.get("_type")
    image = request.values.get("image")
    username = request.values.get("username")
    mail = request.values.get("mail")
    password = request.values.get("password")
    UserID = session['username'] + app.secret_key
    Accounts.update(
        {"_id": ObjectId(AccountID)},
        {
            "title": title,
            "details": details,
            "image": image,
            "_type": _type,
            "username": username,
            "mail": mail,
            "password": password,
            "UserID": UserID
        }
    )
    return redirect("/home")


@app.route("/SearchAccount", methods=['GET'])
def searchEvent():
    # Searching a Task with various references
    key = request.values.get("key")
    refer = request.values.get("refer")
    AllAccounts = Accounts.find({refer: key})
    return render_template('home.html', AllAccounts=AllAccounts)


if __name__ == "__main__":
    app.run(host='')
