from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_mail import Mail, Message
from dotenv import load_dotenv
import mysql.connector
import CNN_Model
import os
import boto3

app = Flask(__name__)

# TO-DO List: Found image 
load_dotenv(dotenv_path='email_login.env')

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

load_dotenv(dotenv_path='aws_login.env')


HOST = os.getenv('HOST')
USERNAME_DB = os.getenv('USERNAME_DB') 
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')


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
    pet_condition = request.form.get("pet_condition")
    location = request.form.get("location")
    email = request.form.get("email")
    breed = request.form.get("breed")
    description = request.form.get("description")
    fileCat = request.files.get("fileCat")
    
    filepath = upload(fileCat)
    
    query = "INSERT INTO pets(email, pet_condition, lost, description, location, image_path, breed) VALUES (%s,%s,%s,%s,%s,%s,%s);"
    
    concur.execute(query, (email,pet_condition,0,description,location,filepath,breed))
        
    return render_template("thank_you.html", name=pet_condition, location=location, email=email)

@app.route("/update")
def update():
    return render_template("update.html")
@app.teardown_appcontext
def close_db_connection(exception=None):
    if db.is_connected():
        concur.close()
        db.close()
        print("MySQL connection is closed")

def calculate_similarity(found_img_path):
    query= """
        SELECT p.id, p.file_path
        FROM pet p
        WHERE p.lost = 1 AND p.file_path IS NOT NULL
    """
    concur.execute(query)

    pet_images = concur.fetchall()
    results = []

    query = "SELECT pet_id FROM images WHERE file_path = %s"
    concur.execute(query, (found_img_path))
    found_image = concur.fetchone()
    found_pet_id = found_image[0] if found_image else None
    
    if found_pet_id:
        print("found image not found")
        return
    
    for pet_image in pet_images:
        pet_id = pet_image[0]
        pet_img_path = pet_image[1]

        if pet_id == found_pet_id:
            continue

        similarity_score = CNN_Model.compare_image(found_img_path, pet_img_path)

        if found_pet_id:
            query = """
                INSERT INTO image_similarities
                (image_id1, image_id2, similarity_score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE similarity_score = %s
            """
            concur.execute(query, (found_pet_id, pet_id, similarity_score, similarity_score))

        results.append({
            'pet_id': pet_id,
            'similarity_score': similarity_score
        })

    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    return results

# def email_similar_from_results(results: list) -> None:
#     matches = [match for match in results if match['similarity_score'] > 0.6]
#     placeholders = ', '.join(['%s'] * len(matches))
#     query = f"""
#         SELECT p.email
#         FROM pet p
#         WHERE i.pet_id IN ({placeholders})
#     """

#     concur.execute(query, tuple(matches))

#     for email in concur.fetchall():
#         msg = Message(subject="PawPals | Could This Be Your Missing Buddy?", recipients=[email])
#         msg.html = render_template('email/found.html')
#         mail.send(msg)
    
concur.close()  # Close cursor