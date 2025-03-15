from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

db = mysql.connector.connect(
        host="pawpals.cfyqi6y224wb.ap-southeast-2.rds.amazonaws.com",
        user="admin",
        password="123456789",
        database=""
    )
cursor = db.cursor()

