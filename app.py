from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import mysql.connector
import CNN_Model
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


load_dotenv(dotenv_path='aws_login.env')


HOST = os.getenv('HOST', 'aws_login')
USERNAME_DB = os.getenv('USERNAME_DB', 'aws_login')
PASSWORD = os.getenv('PASSWORD', 'aws_login')
DATABASE = os.getenv('DATABASE', 'aws_login')

db = mysql.connector.connect(
        host= HOST,
        user= USERNAME_DB,
        password= PASSWORD,
        database= DATABASE
    )

cursor = db.cursor()
