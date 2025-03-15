from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import mysql.connector
import CNN_Model
import os
import boto3

app = Flask(__name__)

load_dotenv(dotenv_path='aws_login.env')


HOST = os.getenv('HOST', 'aws_login')
USERNAME_DB = os.getenv('USERNAME_DB', 'aws_login')
PASSWORD = os.getenv('PASSWORD', 'aws_login')
DATABASE = os.getenv('DATABASE', 'aws_login')

S3_BUCKET = os.getenv('S3_BUCKET', 'aws_login')
S3_REGION = os.getenv('S3_REGION', 'aws_login')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', 'aws_login')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', 'aws_login')


s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)

#TO-DO LIST: Create function to upload imagef

#======== INITIALS =========#
@app.route("/")
def index():
    return render_template("index.html")


#======== PAW MISSING =========#
@app.route("/missing-paw")
def missing_paw():
    return render_template("missing-paw.html")

@app.route("/paw_completed",methods=["GET", "POST"])
def form_missing():
    name = request.form.get("name")
    location = request.form.get("location")
    email = request.form.get("email")
    fileCat = request.files.get("fileCat")
    # filepath = upload(name, file)
    # query = "SELECT...."
    # db.execute(querry)
    if not name or not email or not location or not fileCat:
        return render_template("missing-paw.html")
    return render_template("paw_completed.html", name=name, location=location, email=email)

# def upload(name, file )
#     s3.upload()
#     return file_path
#======== PAW FOUND =========#
@app.route("/paw_found")
def paw_found():
    return render_template("paw_found.html")

@app.route("/thank_you",methods=["GET", "POST"])
def form_found():
    name = request.form.get("name")
    location = request.form.get("location")
    email = request.form.get("email")
    fileCat = request.files.get("fileCat")
    
    if not name or not email or not location or not fileCat:
        return render_template("paw_found.html")
    return render_template("thank_you.html", name=name, location=location, email=email)
    



s3.upload_file("CNN_Model/Imgae_testing/meo_tam_the/cat_1.jpg", S3_BUCKET, "cat_1.jpg")
image_url = f"https://my-images-bucket.s3.YOUR_REGION.amazonaws.com/cat_1.jpg"
print("Uploaded Image URL:", image_url)
db = mysql.connector.connect(
        host= HOST,
        user= USERNAME_DB,
        password= PASSWORD,
        database= DATABASE
    )

cursor = db.cursor()