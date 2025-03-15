from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_mail import Mail, Message
from dotenv import load_dotenv
import mysql.connector
from CNN_model import compare_image
import os
import boto3
from email_validator import validate_email, EmailNotValidError

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

db.autocommit = True

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
    calculate_similarity(filepath)
    
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
        
    return render_template("thank_you.html", name=pet_condition, location=location, email=email), calculate_similarity(filepath)

@app.route("/update")
def update():
    return render_template("update.html")

@app.route("/missing_paw_results", methods=["POST"])
def missing_paw_results():
    email = request.form.get("email")

    # Step 1: Fetch the pet_id from email
    concur.execute("SELECT id FROM pets WHERE email = %s", (email,))
    result = concur.fetchone()

    if not result:
        print(f"❌ No pet found for email: {email}")
        return render_template("missing_paw_results.html", email=email, similarity=[])

    pet_id1 = result[0]  
    print(f"🔎 Searching for matches for Pet ID: {pet_id1}")

    # Ensure all previous results are fetched before executing the next query
    concur.fetchall()

    # Step 2: Fetch similar pets
    query = """
        SELECT 
            CASE 
                WHEN i.pet_id1 = %s THEN i.pet_id2
                ELSE i.pet_id1
            END AS matched_pet_id,
            p2.image_path AS image_path,
            p2.location AS location,
            p2.breed AS breed,
            i.similarity_score AS similarity_score
        FROM image_similarities i
        JOIN pets p2 ON (i.pet_id1 = p2.id OR i.pet_id2 = p2.id)
        WHERE (%s IN (i.pet_id1, i.pet_id2)) 
        AND i.similarity_score > 0.4
        ORDER BY i.similarity_score DESC;
    """
    
    concur.execute(query, (pet_id1, pet_id1))
    results = concur.fetchall()

    # ✅ Convert results into a list of dictionaries
    similarity = []
    for row in results:
        similarity.append({
            "image_path": row[1],  # Image path
            "location": row[2],  # Location
            "breed": row[3],  # Breed
            "similarity_score": row[4]  # Similarity score
        })

    if not similarity:
        print(f"❌ No matches found for Pet ID: {pet_id1}")
    else:
        print(f"✅ Found {len(similarity)} matches: {similarity}")

    return render_template("missing_paw_results.html", email=email, similarity=similarity)




# def calculate_similarity(found_img_path):
#     query = """
#     SELECT p.id, p.image_path
#     FROM pets p
#     WHERE p.lost = 1;
#     """
#     concur.execute(query)
#     pet_images = concur.fetchall()
#     results = []

#     query = "SELECT id FROM pets WHERE image_path = %s"
#     concur.execute(query, (found_img_path,))
#     found_image = concur.fetchone()
#     found_pet_id = found_image[0] if found_image else None
    
#     if not found_pet_id:
#         print("found image not found")
#         return
    
#     for pet_image in pet_images:
#         pet_id = pet_image[0]
#         pet_img_path = pet_image[1]

#         if pet_id == found_pet_id:
#             continue

#         similarity_score = compare_image(found_img_path, pet_img_path)

#         if found_pet_id:
#             query = """
#                     INSERT INTO image_similarities (pet_id1, pet_id2, similarity_score)
#                     VALUES (%s, %s, %s)
#                     ON DUPLICATE KEY UPDATE similarity_score = VALUES(similarity_score)
#                 """
#             concur.execute(query, (pet_id, found_pet_id, similarity_score))


#         results.append({
#             'pet_id': pet_id,
#             'similarity_score': similarity_score
#         })

#     results.sort(key=lambda x: x['similarity_score'], reverse=True)
#     print(results)
#     return email_similar_from_results(results)
def calculate_similarity(img_path):
    """
    Compare a given pet (lost or found) with all opposite category pets in the database.
    Ensures lost pets are always stored in pet_id1 and found pets in pet_id2.
    """

    # Step 1: Get the pet ID and its lost status based on the image path
    query = "SELECT id, lost FROM pets WHERE image_path = %s"
    concur.execute(query, (img_path,))
    pet_info = concur.fetchone()

    if not pet_info:
        print("❌ Pet with this image path not found in the database.")
        return None  # ✅ Exit if pet does not exist

    pet_id, is_lost = pet_info  # ✅ Extract pet ID and lost status
    print(f"🔎 Processing pet {pet_id} (lost = {is_lost})")

    # ✅ FIX: Fetch all remaining results to prevent "Unread result found" error
    concur.fetchall()

    # Step 2: Determine the opposite category to compare against
    opposite_lost_status = 1 if is_lost == 0 else 0  # ✅ If lost, compare with found. If found, compare with lost.

    query2 = """
        SELECT id, image_path
        FROM pets
        WHERE lost = %s;
    """
    concur.execute(query2, (opposite_lost_status,))
    opposite_pets = concur.fetchall()  # ✅ Fetch all opposite category pets

    if not opposite_pets:
        print("❌ No matching pets found to compare against.")
        return None  # ✅ Exit if there are no matches

    results = []

    # Step 3: Compare the given pet with all opposite pets
    for opposite_pet_id, opposite_pet_img_path in opposite_pets:
        if opposite_pet_id == pet_id:
            continue  # ✅ Skip self-comparison

        similarity_score = compare_image(img_path, opposite_pet_img_path)

        # ✅ Always store lost pets in pet_id1 and found pets in pet_id2
        pet_id1, pet_id2 = (pet_id, opposite_pet_id) if is_lost == 1 else (opposite_pet_id, pet_id)

        query3 = """
            INSERT INTO image_similarities (pet_id1, pet_id2, similarity_score)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE similarity_score = VALUES(similarity_score);
        """
        concur.execute(query3, (pet_id1, pet_id2, similarity_score))

        results.append({
            'pet_id1': pet_id1,  # ✅ Correct Key
            'pet_id2': pet_id2,  # ✅ Correct Key
            'similarity_score': similarity_score
        })

    # Step 4: Sort results by similarity score
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    print("✅ Similar pets found:", results)

    # Step 5: Return only if results exist
    return email_similar_from_results(results) if results else None

def email_similar_from_results(results):
    pet_ids = [result['pet_id1'] for result in results]  # ✅ Fixed key name

    if not pet_ids:
        emails = []  # Avoid executing an invalid SQL query
    else:
        query = "SELECT email FROM pets WHERE id IN ({})".format(','.join(['%s'] * len(pet_ids)))
        concur.execute(query, tuple(pet_ids))
        emails = [row[0] for row in concur.fetchall()]  # Extract only the emails

    for email_address in emails:
        try:
            valid = validate_email(email_address)
            normalized_email = valid.email
            
            msg = Message(subject="PawPals | Could This Be Your Missing Buddy?", 
                        recipients=[normalized_email])
            msg.html = render_template('email/found.html')
            mail.send(msg)
            
        except EmailNotValidError as e:
            print(f"Warning: Invalid email address: {email_address}, Error: {str(e)}")
            continue
        except Exception as e:
            print(f"Error sending to {email_address}: {str(e)}")
            continue
