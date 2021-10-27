from re import X
from ssl import SSLContext
from flask import Flask, render_template, make_response, request
from database import *

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

import email, smtplib, ssl
import speech_recognition as SpeechR
import random as rand
import soundfile as sf
import wave

recogn = SpeechR.Recognizer()
app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html", items=getAllProducts())

@app.route("/upload", methods=["PUT"])
def upload():
    data = request.data
    path = "static/voice/" + str(rand.randint(0, 10000)) + ".wav"
    file = open(path, "x")
    file = open(path, "wb")
    try:
        file.write(data)
        response = make_response("/search/sent")
        response.set_cookie("path", path)
        return response
    except :
        path = "static/voice/" + str(rand.randint(0, 10000 )) + ".wav"
        file = open(path, "x")
        file = open(path, "wb")
        file.write(data)
        response = make_response("/search/sent")
        response.set_cookie("path", path)
        return response

@app.route("/search/")
def send():
    return render_template("search.html")

@app.route("/search")
def senda():
    return render_template("search.html")

@app.route("/search/sent")
def search():
    if request.cookies["path"] != None:
        with SpeechR.AudioFile("./" + request.cookies["path"]) as audio:
            data = recogn.record(audio)
        try :
            voice_data = recogn.recognize_google(data)
        except :
            voice_data = ""
        return render_template("search.html", search = voice_data)
    else:
        return render_template("search.html")

@app.route("/search/<string:search>")
def check(search:str):
    words = search.split(" ")
    items = []
    for i in words:
        for j in getAllProducts():
            if (i.lower() in j.name.lower() or i.lower() in j.description.lower()) and j not in items:
                items.append(j)
    return render_template("search.html", search = search, items = items)

@app.route('/product/<int:id>')
def productPage(id):
    return render_template('product.html', product= getProductById(id))

@app.route('/cart')
def cartPage():
    if request.cookies.get('cartId'):
        return render_template('cart.html', items = getAllItems(request.cookies.get('cartId')))
    else :
        return render_template('cart.html')

@app.route('/add_to_cart/<int:id>' )
def addToCart(id):
    if request.cookies.get('cartId') == None:
        response = make_response(render_template('index.html', items = getAllProducts()))
        response.set_cookie('cartId', str(addItem(-1, id)))
        return response
    else :
        addItem(request.cookies.get('cartId'), id)
        return render_template('index.html', items = getAllProducts())

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'GET' and request.cookies.get('cartId'):
        return render_template('submit.html')
    elif request.method == 'POST' and request.cookies.get('cartId'):
        context = ssl.create_default_context()
        sendMail(request.form['name'], request.form['email'], getAllItems(request.cookies.get('cartId')))
        response = make_response(render_template('index.html', products = getAllProducts(), popup = True))
        response.set_cookie('cartId', '', expires=0)
        return response


def sendMail(name, to, cart):
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login("ofekarcom@gmail.com", "arikinna03")
    msg = MIMEMultipart('alterantive')
    msg['Subject'] = "Ordering"
    msg['From'] = "ofekarcom@gmail.com"
    msg['To'] = to
    html = MIMEText(render_template("email.html", items=cart, name=name), 'html')
    msg.attach(html)
    smtp_server.sendmail("ofekarcom@gmail.com", to, msg.as_string())
    smtp_server.quit()
