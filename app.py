from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import mysql.connector
import CNN_Model
import os
import boto3

app = Flask(__name__)

# TO-DO List: Found image 

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

db = mysql.connector.connect(
        host= HOST,
        user= USERNAME_DB,
        password= PASSWORD,
        database= DATABASE
    )

concur = db.cursor()

query = "USE pawpals"
concur.execute(query)
#TO-DO LIST: Create function to upload imagef

def upload(file):
    
    objname = os.path.basename(file.filename)
    
    # Get the file name
    s3.upload_fileobj(file, S3_BUCKET, objname)
    
    # Name file
    file_path = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{objname}"
    print(file_path)
    return file_path

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
    breed = request.form.get("breed")
    description = request.form.get("description")
    fileCat = request.files.get("fileCat")

    filepath = upload(fileCat)
    
    query = "INSERT INTO pets(email, name, lost, description, location, image_path, breed) VALUES (%s,%s,%s,%s,%s,%s,%s);"
    
    concur.execute(query, (email,name, 1, description,location,filepath,breed))
    
    
    return render_template("paw_completed.html", name=name, location=location, email=email)

#======== PAW FOUND =========#
@app.route("/paw_found")
def paw_found():
    return render_template("paw_found.html")

@app.route("/thank_you",methods=["GET", "POST"])
def form_found():
    condition = request.form.get("name")
    location = request.form.get("location")
    email = request.form.get("email")
    breed = request.form.get("breed")
    description = request.form.get("description")
    fileCat = request.files.get("fileCat")
    
    filepath = upload(fileCat)
    
    query = "INSERT INTO pets(email, condition, lost, description, location, image_path, breed) VALUES (%s,%s,%s,%s,%s,%s,%s);"
    
    concur.execute(query, (email,condition,0,description,location,filepath,breed))
        
    return render_template("thank_you.html", name=condition, location=location, email=email)

@app.route("/update")
def update():
    return render_template("update.html")