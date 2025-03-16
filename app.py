from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_mail import Mail, Message
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling
from CNN_model import compare_image
import os
import boto3
from email_validator import validate_email, EmailNotValidError
import time

app = Flask(__name__)

# TO-DO List: Found image 
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

HOST_DB = os.getenv('HOST_DB')
USERNAME_DB = os.getenv('USERNAME_DB') 
PASSWORD = os.getenv('PASSWORD')
DATABASE = "pawpals"
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# Database connection pool
db_pool = None

def create_db_pool():
    global db_pool
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="pawpals_pool",
            pool_size=5,
            host=HOST_DB,
            user=USERNAME_DB,
            password=PASSWORD,
            database=DATABASE,
            connect_timeout=60,
            use_pure=True,
            autocommit=True
        )
        print("Database connection pool created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating connection pool: {err}")
        return False

# Create pool on startup
create_db_pool()

def get_db_connection():
    global db_pool
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            if db_pool is None:
                create_db_pool()
                
            connection = db_pool.get_connection()
            return connection
        except mysql.connector.Error as err:
            print(f"Database connection failed (attempt {attempt+1}/{max_retries}): {err}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            
    raise Exception("Failed to connect to database after multiple attempts")

def execute_query(query, params=None, fetch=None):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if fetch == 'one':
            result = cursor.fetchone()
            # Consume any remaining results to avoid "Unread result found"
            cursor.fetchall()
            return result
        elif fetch == 'all':
            return cursor.fetchall()
        else:
            # For non-SELECT queries, we still need to consume any possible results
            cursor.fetchall()
        return None
    except mysql.connector.Error as err:
        print(f"Database query error: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)

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
    
    execute_query(query, (email, name, 1, description, location, filepath, breed))
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
    execute_query(query, (email, pet_condition, 0, description, location, filepath, breed))
        
    return render_template("thank_you.html", name=pet_condition, location=location, email=email), calculate_similarity(filepath)

@app.route("/update")
def update():
    return render_template("update.html")

@app.route("/missing_paw_results", methods=["POST"])
def missing_paw_results():
    email = request.form.get("email")

    # Step 1: Fetch the pet_id from email
    result = execute_query("SELECT id FROM pets WHERE email = %s", (email,), fetch='one')

    if not result:
        print(f"❌ No pet found for email: {email}")
        return render_template("missing_paw_results.html", email=email, similarity=[])

    pet_id1 = result[0]  
    print(f"🔎 Searching for matches for Pet ID: {pet_id1}")

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
    
    results = execute_query(query, (pet_id1, pet_id1), fetch='all')

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

def calculate_similarity(img_path):
    """
    Compare a given pet (lost or found) with all opposite category pets in the database.
    Ensures lost pets are always stored in pet_id1 and found pets in pet_id2.
    """

    # Step 1: Get the pet ID and its lost status based on the image path
    pet_info = execute_query("SELECT id, lost FROM pets WHERE image_path = %s", (img_path,), fetch='one')

    if not pet_info:
        print("❌ Pet with this image path not found in the database.")
        return None  # ✅ Exit if pet does not exist

    pet_id, is_lost = pet_info  # ✅ Extract pet ID and lost status
    print(f"🔎 Processing pet {pet_id} (lost = {is_lost})")

    # Step 2: Determine the opposite category to compare against
    opposite_lost_status = 1 if is_lost == 0 else 0  # ✅ If lost, compare with found. If found, compare with lost.

    opposite_pets = execute_query(
        "SELECT id, image_path FROM pets WHERE lost = %s",
        (opposite_lost_status,),
        fetch='all'
    )

    if not opposite_pets:
        print("❌ No matching pets found to compare against.")
        return None  # ✅ Exit if there are no matches

    results = []

    # Step 3: Compare the given pet with all opposite pets
    for opposite_pet_id, opposite_pet_img_path in opposite_pets:
        if opposite_pet_id == pet_id:
            continue  # ✅ Skip self-comparison
        
        try:
            similarity_score = compare_image(img_path, opposite_pet_img_path)
        except Exception as e:
            print("error invalid image path(s), continuing to next comparison")
            continue

        # ✅ Always store lost pets in pet_id1 and found pets in pet_id2
        pet_id1, pet_id2 = (pet_id, opposite_pet_id) if is_lost == 1 else (opposite_pet_id, pet_id)

        execute_query(
            """
            INSERT INTO image_similarities (pet_id1, pet_id2, similarity_score)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE similarity_score = VALUES(similarity_score);
            """,
            (pet_id1, pet_id2, similarity_score)
        )

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

def email_similar_from_results(results, min_similarity=0.5):
    # Process each similarity result
    for result in results:
        if result['similarity_score'] >= min_similarity:
            pet_id1, pet_id2 = result['pet_id1'], result['pet_id2']
            
            # Get details for both pets - now including image_path
            pets_data = {}
            found_pets = execute_query(
                """
                SELECT id, email, name, description, location, image_path, lost
                FROM pets 
                WHERE id IN (%s, %s)
                """,
                (pet_id1, pet_id2),
                fetch='all'
            )
            
            for row in found_pets:
                pets_data[row[0]] = {
                    'email': row[1], 
                    'name': row[2], 
                    'description': row[3],
                    'location': row[4],
                    'image_path': row[5],
                    'lost': row[6]
                }
            
            # Determine which pet is lost and which might be the found match
            if pet_id1 in pets_data and pets_data[pet_id1]['lost'] == 1:
                lost_pet_id, found_pet_id = pet_id1, pet_id2
            elif pet_id2 in pets_data and pets_data[pet_id2]['lost'] == 1:
                lost_pet_id, found_pet_id = pet_id2, pet_id1
            else:
                continue  # Skip if neither pet is marked as lost
            
            # Get the owner's email
            email_address = pets_data[lost_pet_id]['email']
            
            try:
                valid = validate_email(email_address)
                normalized_email = valid.email
                
                # Extract username from email (or use pet name if preferred)
                username = normalized_email.split('@')[0]
                
                # Send the email
                msg = Message(
                    subject="PawPals | Could This Be Your Missing Buddy?", 
                    recipients=[normalized_email]
                )
                
                msg.html = render_template(
                    'email/found.html',
                    username=username,
                    location=pets_data[found_pet_id]['location'],
                    description=pets_data[found_pet_id]['description'],
                    contact="Contact us to connect with the finder",
                    link="",  # Left blank as requested
                    image_url=pets_data[found_pet_id]['image_path']  # Pass the image URL to the template
                )
                
                mail.send(msg)
                print(f"Sent match notification to {normalized_email} for pet {pets_data[lost_pet_id]['name']}")
                
            except EmailNotValidError as e:
                print(f"Warning: Invalid email address: {email_address}, Error: {str(e)}")
            except Exception as e:
                print(f"Error sending to {email_address}: {str(e)}")
                continue

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)