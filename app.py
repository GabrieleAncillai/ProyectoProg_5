# Integrantes del grupo:
# Rene de Leon 2-713-1724
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

title = "Proyecto Programación 4"

client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
# client = MongoClient("mongodb+srv://GabrieleAncillai:Gabriele25@ancillai-bay7d.mongodb.net/test?retryWrites=true&w=majority")
db = client.ProyectICD  # Select the database

# Collections
Users = db.Users  # collection Usuarios
Events = db.Events  # collection Eventos

# StateTree
CurrentUser = {}


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


@app.route("/acceso")
def render_login():
    return render_template('login.html', incorrect=0)


# ------------------------------- Funciones de Registro y Login -------------------------------
@app.route("/register", methods=['POST'])
def register():
    # Creating a user
    name = request.values.get("name")
    identification = request.values.get("identification")
    password = request.values.get("password")
    mail = request.values.get("mail")
    gender = request.values.get("gender")
    ambit = request.values.get("ambit")
    faculty = request.values.get("faculty")

    # --- dates and ages ---
    birthday = request.values.get("birthday")
    birthmonth = request.values.get("birthmonth")
    birthyear = request.values.get("birthyear")
    date = datetime.datetime.now()
    year = int(date.strftime("%Y"))
    month = int(date.strftime("%m"))
    day = int(date.strftime("%d"))
    if (year > int(birthyear) and month >= int(birthmonth) and day >= int(birthday)) or (
            year > int(birthyear) and month > int(birthmonth) and day < int(birthday)):
        age = year - int(birthyear)
    else:
        age = year - int(birthyear) - 1
    # --- dates and ages ---

    Users.insert({
        "name": name,
        "identification": identification,
        "password": password,
        "mail": mail,
        "gender": gender,
        "age": age,
        "faculty": faculty,
        "ambit": ambit
    })
    return redirect("/acceso")


@app.route("/login", methods=['GET'])
def login():
    ID = request.values.get("ID")
    key = request.values.get("key")

    # Comprobar que existe el usuario
    DATA = Users.find_one({"identification": ID, "password": key})
    if DATA != None:
        session["identification"] = DATA["identification"]
        app.secret_key = DATA["password"]
        MyUser = Users.find({"identification": session['identification'], "password": app.secret_key})
        print(session)
        action = render_template("home.html", MyUser=MyUser, a1="active", title="Inicio")
    else:
        # ERROR
        print("ERROR")
        action = render_template("login.html", errorType="ERROR")
    
    return action

@app.route("/logout")
def logout():

    # Delete current session
    session = None
    app.secret_key = ""
    
    return redirect("/acceso")

# ------------------------------- Componentes de tabla de opciones superior -------------------------------
@app.route("/home")  # Home for Students
def home():
    MyUser = Users.find(
        {"identification": session['identification'], "password": app.secret_key})
    return render_template('home.html', a1="active", title="Inicio", MyUser=MyUser)


@app.route("/home/events")  # Events for Students
def Stud_events():
    MyUser = Users.find({"identification": session['identification'], "password": app.secret_key})
    all_l = Events.find({"state": "avalible"})
    title = "Eventos"
    a2 = "active"
    return render_template('home.html', a2=a2, all=all_l, title=title, Users=MyUser)


@app.route("/home/account")  # Account Settings for Students
def account():
    MyUser = Users.find(
        {"identification": session['identification'], "password": app.secret_key})
    return render_template('home.html', a3="active", title="Configuración", MyUser=MyUser)


@app.route("/menu")  # Home for Administrators
def menu():
    MyUser = Users.find(
        {"identification": session['identification'], "password": app.secret_key})
    return render_template('menu.html', a1="active", title="Administración", MyUser=MyUser)


@app.route("/menu/events")  # Events for Administrators
def Admin_events():
    MyUser = Users.find(
        {"identification": session['identification'], "password": app.secret_key})
    all_l = Events.find()
    title = "Eventos"
    a2 = "active"
    return render_template('menu.html', a2=a2, all=all_l, title=title, MyUser=MyUser)


@app.route("/menu/QRCode", methods=['GET'])  # Events for Administrators
def QRCodeScanner():
    code = request.values.get("code")
    all_l = Events.find()
    ID = request.values.get("ID")
    event_ID = request.values.get("event_ID")
    event_plus_user = str(str(ID) + str(event_ID))
    if code == event_plus_user:
        Users.update({"_id": ObjectId(ID)}, {"$set": {event_ID: "in_event"}})
    MyUser = Users.find(
        {"identification": session['identification'], "password": app.secret_key})
    title = "QRCodeScanner"
    a3 = "active"
    return render_template('menu.html', a3=a3, title=title, all=all_l, MyUser=MyUser)


@app.route("/menu/stats", methods=['GET'])
def stats():
    #event_ID = request.values.get("event_ID")
    FindMale = Users.find({"gender": "Male"})
    FindFemale = Users.find({"gender": "Female"})
    FindOther = Users.find({"gender": "Other"})
    FindProf = Users.find({"ambit": "teacher"})
    FindStudent = Users.find({"ambit": "student"})
    FindCS = Users.find({"faculty": "Ciencias de la Salud"})
    FindING = Users.find({"faculty": "Ingeniería, Arquitectura y Diseño"})
    FindCA = Users.find(
        {"faculty": "Ciencias Administrativas, Marítima y Portuaria"})
    FindHT = Users.find({"faculty": "Hotelería Gastronomía y Turismo"})
    all = Users.find()
    m = 0
    f = 0
    o = 0
    t = 0
    s = 0
    cs = 0
    ing = 0
    ca = 0
    ht = 0
    for all in FindMale:
        if all['gender'] == 'Male':
            m = m+1
    for all in FindFemale:
        if all['gender'] == 'Female':
            f = f+1
    for all in FindOther:
        if all['gender'] == 'Other':
            o = o+1
    for all in FindProf:
        if all['ambit'] == 'teacher':
            t = t+1
    for all in FindStudent:
        if all['ambit'] == 'student':
            s = s+1
    for all in FindCS:
        if all['faculty'] == 'Ciencias de la Salud':
            cs = cs+1
    for all in FindING:
        if all['faculty'] == 'Ingeniería, Arquitectura y Diseño':
            ing = ing+1
    for all in FindCA:
        if all['faculty'] == 'Ciencias Administrativas, Marítima y Portuaria':
            ca = ca+1
    for all in FindHT:
        if all['faculty'] == 'Hotelería Gastronomía y Turismo':
            ht = ht+1
    return render_template('reportes.html', m=m, f=f, o=o, t=t, s=s, cs=cs, ing=ing, ca=ca, ht=ht, all=all)


# ------------------------------- Condition Done or Undone -------------------------------
@app.route("/eventAvalible")
def eventAvalible():
    # Avalible or not
    ID = request.values.get("ID")
    task = Events.find({"_id": ObjectId(ID)})
    if task[0]['state'] == "avalible":
        Events.update({"_id": ObjectId(ID)}, {"$set": {"state": "unavalible"}})
    else:
        Events.update({"_id": ObjectId(ID)}, {"$set": {"state": "avalible"}})
    return redirect(redirect_url())


# ------------------------------- EVENTS -------------------------------
@app.route("/assistEvent", methods=['GET', 'POST'])
def assistEvent():
    # Assisting an Event
    ID = request.values.get("ID")
    event_ID = request.values.get("event_ID")
    Users.update({"_id": ObjectId(ID)}, {"$set": {event_ID: "signed"}})
    event_plus_user = str(str(ID) + str(event_ID))
    imgFile = event_plus_user + '.png'

    # Makes QRCode with ID parameters
    qr = qrcode.make(event_plus_user)
    qr.save(imgFile)

    return redirect("/home/events")


@app.route("/addEvent", methods=['POST'])
def addEvent():
    # Adding an Event
    name = request.values.get("name")
    details = request.values.get("details")
    date = request.values.get("date")

    Events.insert(
        {"name": name,
         "details": details,
         "date": date,
         "state": "unavalible",
         "students_in": 0,
         "students_went": 0,
         "students_faculty": "",
         "students_gender": "",
         "students_age": 0})
    return redirect("/menu/events")


@app.route("/removeEvent")
def removeEvent():
    # Deleting a Task with various references
    ID = request.values.get("ID")
    Events.remove({"_id": ObjectId(ID)})
    return redirect("/menu/events")


@app.route("/updateEvent")
def updateEvent():
    ID = request.values.get("ID")
    task = Events.find({"_id": ObjectId(ID)})
    title = "Actualizar"
    return render_template('updateEvent.html', tasks=task, title=title)


@app.route("/updateTaskEvent", methods=['POST'])
def updateTaskEvent():
    # Updating a Task with various references
    name = request.values.get("name")
    details = request.values.get("details")
    date = request.values.get("date")
    state = request.values.get("state")
    ID = request.values.get("ID")
    Events.update({"_id": ObjectId(ID)},
                  {"name": name,
                   "details": details,
                   "date": date,
                   "state": state,
                   "students_in": 0,
                   "students_went": 0,
                   "students_faculty": "",
                   "students_gender": "",
                   "students_age": 0})
    return redirect("/menu/events")


@app.route("/searchEvent", methods=['GET'])
def searchEvent():
    # Searching a Task with various references
    key = request.values.get("key")
    refer = request.values.get("refer")
    if key == "_id":
        all_l = Events.find({refer: ObjectId(key)})
    else:
        all_l = Events.find({refer: key})
    return render_template('searchlist.html', all=all_l, title=title)


if __name__ == "__main__":
    app.run(host='192.168.139.2')