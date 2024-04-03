from flask import Blueprint, request, jsonify
import face_recognition
from psycopg2.extras import RealDictCursor
import json
import DBConnection

auth_service = Blueprint('auth_service', __name__)

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

@auth_service.route('/authenticate', methods=['POST'])
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
        conn = DBConnection.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT employee_id, first_name, last_name, email, address, country, profile, department_id, unit, "
                " qubical, joining_date, created_by, work_location_id, image, base64_encoding FROM employee_details"
                    " where terminate_date is null ")
        users = cur.fetchall()
        cur.close()
        conn.close()

        for user in users:
            user_encoding = json.loads(user['image'])
            match = face_recognition.compare_faces([user_encoding], face_encoding)
            if match[0]:
                return jsonify({
                    "success": True,
                    "message": "Authentication successful",
                    "user": {
                        'employee_id': user['employee_id'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'email': user['email'],
                        'address': user['address'],
                        'country': user['country'],
                        'profile': user['profile'],
                        'department_id': user['department_id'],
                        'unit': user['unit'],
                        'qubical': user['qubical'],
                        'joining_date': user['joining_date'],
                        'created_by': user['created_by'],
                        'work_location_id': user['work_location_id'],
                        'base64_encoding': user['base64_encoding']
                    },
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


