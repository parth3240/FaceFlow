from flask import Flask, request, jsonify
import face_recognition
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = Flask(__name__)

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "facedetection"
DB_USER = "facedetect"
DB_PASS = "admin"

def count_face_from_image(image):
    face_locations = face_recognition.face_locations(image)
    num_faces = len(face_locations)
    return num_faces

def load_image_and_detect_face(image):
    # Detect faces
    face_locations = face_recognition.face_locations(image)
    # Assuming the first face is the person's face
    face_encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
    return face_encoding, None

def compare_faces(face_encoding1, face_encoding2):
    # Compare the faces
    results = face_recognition.compare_faces([face_encoding1], face_encoding2)
    return results[0]

def allowed_file(file):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in file.filename and \
           file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

@app.route('/register-user', methods=['POST'])
def register_user():
    if 'name' not in request.form or 'email' not in request.form or 'image' not in request.files:
        return jsonify({
            "success": False,
            "message": "Name, email, and image file are required."
        }), 400

    name = request.form['name']
    email = request.form['email']
    file = request.files['image']

    if not file or not allowed_file(file):
        return jsonify({
            "success": False,
            "error": "Invalid file type. Only image files are allowed."
        }), 400

    image = face_recognition.load_image_file(file)

    face_count = count_face_from_image(image)
    if face_count > 1:
        return jsonify({
            "success": False,
            "message": "More then one face(s) are found from the images",
            "face_count": face_count
        }), 400
    elif face_count == 0:
        return jsonify({
            "success": False,
            "message": "No face is found from the images",
            "face_count": face_count
        }), 400

    face_encoding, error = load_image_and_detect_face(image)

    if face_encoding is None:
        return jsonify({
            "success": False,
            "message": error
        }), 400



    face_encoding_as_text = json.dumps(face_encoding.tolist())

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_info (name, email, face_encoding) VALUES (%s, %s, %s)",
                    (name, email, face_encoding_as_text))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "message": "User registered successfully."
        }), 201
    except psycopg2.IntegrityError as e:
        print(str(e))
        return jsonify({
            "success": False,
            "message": "This email is already registered."
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/authenticate', methods=['POST'])
def authenticate():
    if 'image' not in request.files:
        return jsonify({
            "success": False,
            "message": "Image file is required."
        }), 400

    file = request.files['image']

    if not file or not allowed_file(file):
        return jsonify({
            "success": False,
            "message": "Invalid file format. Only image files are allowed."
        }), 400

    image = face_recognition.load_image_file(file)

    face_count = count_face_from_image(image)
    if face_count > 1:
        return jsonify({
            "success": False,
            "message": "More then one face(s) are found from the images",
            "face_count": face_count
        }), 400
    elif face_count == 0:
        return jsonify({
            "success": False,
            "message": "No face are found from the images",
            "face_count": face_count
        }), 400

    face_encoding, error = load_image_and_detect_face(image)

    if face_encoding is None:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, name, email, face_encoding FROM user_info")
        users = cur.fetchall()
        cur.close()
        conn.close()

        for user in users:
            user_encoding = json.loads(user['face_encoding'])
            match = face_recognition.compare_faces([user_encoding], face_encoding)
            if match[0]:
                return jsonify({
                    "success": True,
                    "message": "Authentication successful",
                    "user": {"id": user['id'], "name": user['name'], "email": user['email']},
                    "face_count": face_count
                }), 200

        return jsonify({
            "success": False,
            "message": "No matching user found.",
            "face_count": face_count
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
