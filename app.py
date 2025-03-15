from flask import Flask, request, jsonify
from dotenv import load_dotenv
import mysql.connector
import os

app = Flask(__name__)

load_dotenv(dotenv_path='aws_login.env')



HOST = os.getenv('HOST', 'aws_login')
USERNAME = os.getenv('USERNAME', 'aws_login')
PASSWORD = os.getenv('PASSWORD', 'aws_login')
DATABASE = os.getenv('DATABASE', 'aws_login')

db = mysql.connector.connect(
        host= HOST,
        user= USERNAME,
        password= PASSWORD,
        database= DATABASE
    )

cursor = db.cursor()
