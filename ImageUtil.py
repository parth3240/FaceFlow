from flask import jsonify
import face_recognition


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


def validate_image(file):
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