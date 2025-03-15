from flask import Flask, request, render_template, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import mysql.connector
import CNN_Model
import os
import boto3

app = Flask(__name__)

load_dotenv(dotenv_path='email_login.env')

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/missing-paw")
def missing_paw():
    return render_template("missing-paw.html")

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
s3.upload_file("CNN_Model/Imgae_testing/meo_tam_the/cat_1.jpg", S3_BUCKET, "cat_1.jpg")
image_url = f"https://my-images-bucket.s3.YOUR_REGION.amazonaws.com/cat_1.jpg"
print("Uploaded Image URL:", image_url)
db = mysql.connector.connect(
        host= HOST,
        user= USERNAME_DB,
        password= PASSWORD,
        database= DATABASE
    )

concur = db.cursor()

@app.teardown_appcontext
def close_db_connection(exception=None):
    if db.is_connected():
        concur.close()
        db.close()
        print("MySQL connection is closed")

#@app.route("/calculate-similarity")
# def calculate_similarity(found_img_path):
#     query= """
#         SELECT p.id, p.file_path
#         FROM pet p
#         WHERE p.lost = 1 AND p.file_path IS NOT NULL
#     """
#     concur.execute(query)

#     pet_images = concur.fetchall()
#     results = []

#     query = "SELECT pet_id FROM images WHERE file_path = %s"
#     concur.execute(query, (found_img_path))
#     found_image = concur.fetchone()
#     found_pet_id = found_image[0] if found_image else None
    
#     if found_pet_id:
#         print("found image not found")
#         return
    
#     for pet_image in pet_images:
#         pet_id = pet_image[0]
#         pet_img_path = pet_image[1]

#         if pet_id == found_pet_id:
#             continue

#         similarity_score = CNN_Model.compare_image(found_img_path, pet_img_path)

#         if found_pet_id:
#             query = """
#                 INSERT INTO image_similarities
#                 (image_id1, image_id2, similarity_score)
#                 VALUES (%s, %s, %s)
#                 ON DUPLICATE KEY UPDATE similarity_score = %s
#             """
#             concur.execute(query, (found_pet_id, pet_id, similarity_score, similarity_score))

#         results.append({
#             'pet_id': pet_id,
#             'similarity_score': similarity_score
#         })

#     results.sort(key=lambda x: x['similarity_score'], reverse=True)
#     return results

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
    
