from flask import Flask, render_template, request
from threading import Thread
from replit import db

app = Flask('')

@app.route('/')
def home():

  date_time = db["date"]
  percent = db["percent"]
  euro = db["euro"]
  profit = db["profit/loss"]

  return render_template("index.html", date_time = date_time, percent = percent, euro = euro, profit = profit)

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()