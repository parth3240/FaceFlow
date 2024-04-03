from flask import Blueprint, jsonify, request
import face_recognition
from psycopg2.extras import RealDictCursor
import DBConnection
import json
import base64

import ImageUtil

employee_service = Blueprint('employee_service', __name__)


@employee_service.route('/allEmployee', methods=['GET'])
def getAllEmployee():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select employee_id, first_name, last_name, email, address, country, profile, department_id, unit, "
                "qubical, joining_date, created_by, work_location_id, base64_encoding from employee_details where terminate_date is null ")
    employees = cur.fetchall()
    cur.close()
    conn.close()

    if employees is None:
        return jsonify({
            "success": False,
            "message": "No Employee has been found",
            "employee_list": []
        }), 201

    json_array = []

    for employee in employees:
        record_dict = {
            'employee_id': employee['employee_id'],
            'first_name': employee['first_name'],
            'last_name': employee['last_name'],
            'email': employee['email'],
            'address': employee['address'],
            'country': employee['country'],
            'profile': employee['profile'],
            'department_id': employee['department_id'],
            'unit': employee['unit'],
            'qubical': employee['qubical'],
            'joining_date': employee['joining_date'],
            'created_by': employee['created_by'],
            'work_location_id': employee['work_location_id'],
            'base64_encoding': employee['base64_encoding']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "employee_list": json_array
    }), 201


@employee_service.route('/employee/<int:emp_id>', methods=['GET'])
def getEmployee(emp_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select employee_id, first_name, last_name, email, address, country, profile, department_id, unit, "
                "qubical, joining_date, created_by, work_location_id, base64_encoding from employee_details WHERE employee_id = %s "
                , (emp_id,))
    employee = cur.fetchone()
    cur.close()
    conn.close()

    if employee is None:
        return jsonify({
            "success": False,
            "message": "No Employee has been found",
            "employee": {}
        }), 201

    record_dict = {
        'employee_id': employee['employee_id'],
        'first_name': employee['first_name'],
        'last_name': employee['last_name'],
        'email': employee['email'],
        'address': employee['address'],
        'country': employee['country'],
        'profile': employee['profile'],
        'department_id': employee['department_id'],
        'unit': employee['unit'],
        'qubical': employee['qubical'],
        'joining_date': employee['joining_date'],
        'created_by': employee['created_by'],
        'work_location_id': employee['work_location_id'],
        'base64_encoding': employee['base64_encoding']
    }
    return jsonify({
        "success": True,
        "message": "Success",
        "employee": record_dict
    }), 201


@employee_service.route('/employee/admin', methods=['GET'])
def getAdmin():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select employee_id, first_name, last_name, email, address, country, profile, department_id, unit, "
                "qubical, joining_date, created_by, work_location_id, base64_encoding from employee_details WHERE profile = 'ADM' ")
    employee = cur.fetchone()
    cur.close()
    conn.close()

    if employee is None:
        return jsonify({
            "success": False,
            "message": "No Admin found",
            "employee": {}
        }), 201

    record_dict = {
        'employee_id': employee['employee_id'],
        'first_name': employee['first_name'],
        'last_name': employee['last_name'],
        'email': employee['email'],
        'address': employee['address'],
        'country': employee['country'],
        'profile': employee['profile'],
        'department_id': employee['department_id'],
        'unit': employee['unit'],
        'qubical': employee['qubical'],
        'joining_date': employee['joining_date'],
        'created_by': employee['created_by'],
        'work_location_id': employee['work_location_id'],
        'base64_encoding': employee['base64_encoding']
    }
    return jsonify({
        "success": True,
        "message": "Success",
        "employee": record_dict
    }), 201



@employee_service.route('/employee', methods=['POST'])
def addEmployee():

    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    email = request.form.get('email', None)
    address = request.form.get('address', None)
    country = request.form.get('country', 'Canada')
    profile = request.form.get('profile', None)
    department_id = request.form.get('department_id', None)
    unit = request.form.get('unit', None)
    qubical = request.form.get('qubical', None)
    image = request.files['image']
    joining_date = request.form.get('joining_date', None)
    created_by = request.form.get('created_by', None)
    work_location_id = request.form.get('work_location_id', None)
    manager_id = request.form.get('manager_id', None)

    base64_encoding = base64.b64encode(image.read()).decode('utf-8')

    validation_response = ImageUtil.validate_image(image)
    if validation_response is not None:
        return validation_response

    face = face_recognition.load_image_file(image)
    face_encoding, error = ImageUtil.load_image_and_detect_face(face)

    if face_encoding is None:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    face_encoding_as_text = json.dumps(face_encoding.tolist())

    try:
        conn = DBConnection.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("INSERT INTO employee_details "
                    " (first_name, last_name, email, address, country, profile, department_id, unit, qubical, image, joining_date, created_by, work_location_id, base64_encoding) "
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                    (first_name, last_name, email, address, country, profile, department_id, unit, qubical, face_encoding_as_text, joining_date, created_by, work_location_id, base64_encoding))
        new_employee_row = cur.fetchone()
        new_employee_id = new_employee_row['employee_id']
        conn.commit()
        conn.close()

        conn2 = DBConnection.get_db_connection()
        cur2 = conn2.cursor()
        cur2.execute("INSERT INTO employee_manager_relation "
                    " (employee_id, manager_id) "
                    " VALUES (%s, %s) ",
                    (new_employee_id, manager_id))
        conn2.commit()
        cur2.close()
        conn2.close()

        return jsonify({
            "success": True,
            "message": "Employee registered successfully.",
            "new_employee_id": new_employee_id
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


@employee_service.route('/employee/<int:employee_id>', methods=['PUT'])
def updateEmployee(employee_id):

    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    email = request.form.get('email', None)
    address = request.form.get('address', None)
    country = request.form.get('country', None)
    profile = request.form.get('profile', None)
    department_id = request.form.get('department_id', None)
    unit = request.form.get('unit', None)
    qubical = request.form.get('qubical', None)
    image = request.files.get('image', None)
    joining_date = request.form.get('joining_date', None)
    modified_by = request.form.get('modified_by', None)
    work_location_id = request.form.get('work_location_id', None)
    manager_id = request.form.get('manager_id', None)
    termination_date = request.form.get('termination_date', None)



    if image is not None:
        base64_encoding = base64.b64encode(image.read()).decode('utf-8')
        validation_response = ImageUtil.validate_image(image)
        if validation_response is not None:
            return validation_response

        face = face_recognition.load_image_file(image)
        face_encoding, error = ImageUtil.load_image_and_detect_face(face)

        if face_encoding is None:
            return jsonify({
                "success": False,
                "message": error
            }), 400

        face_encoding_as_text = json.dumps(face_encoding.tolist())

        try:
            conn = DBConnection.get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("select id, employee_id, manager_id from employee_manager_relation WHERE employee_id = %s "
                        , (employee_id,))
            employee_manager = cur.fetchone()
            cur.close()
            conn.close()

            emp_mgr_id = 0;
            if employee_manager is not None:
                emp_mgr_id = employee_manager['id']

            conn2 = DBConnection.get_db_connection()
            cur2 = conn2.cursor(cursor_factory=RealDictCursor)
            cur2.execute("""
                    UPDATE employee_details 
                    SET first_name = %s, 
                        last_name = %s, 
                        email = %s, 
                        address = %s, 
                        country = %s, 
                        profile = %s, 
                        department_id = %s, 
                        unit = %s, 
                        qubical = %s, 
                        image = %s,  
                        joining_date = %s, 
                        modified_by = %s, 
                        work_location_id = %s,
                        terminate_date = %s,
                        base64_encoding = %s
                    WHERE employee_id = %s
                """, (
                first_name, last_name, email, address, country, profile, department_id, unit, qubical,
                face_encoding_as_text,
                joining_date, modified_by, work_location_id, termination_date, base64_encoding, employee_id))
            conn2.commit()
            cur2.close()
            conn2.close()

            conn3 = DBConnection.get_db_connection()
            cur3 = conn3.cursor()
            cur3.execute("UPDATE employee_manager_relation "
                         " set employee_id = %s, manager_id = %s where id = %s",
                         (employee_id, manager_id, emp_mgr_id))
            conn3.commit()
            cur3.close()
            conn3.close()

            return jsonify({
                "success": True,
                "message": "Employee Updated successfully."
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 404

    elif image is None:

        try:
            conn = DBConnection.get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("select id, employee_id, manager_id from employee_manager_relation WHERE employee_id = %s "
                        , (employee_id,))
            employee_manager = cur.fetchone()
            cur.close()
            conn.close()

            emp_mgr_id = 0;
            if employee_manager is not None:
                emp_mgr_id = employee_manager['id']

            conn2 = DBConnection.get_db_connection()
            cur2 = conn2.cursor(cursor_factory=RealDictCursor)
            cur2.execute("""
                    UPDATE employee_details 
                    SET first_name = %s, 
                        last_name = %s, 
                        email = %s, 
                        address = %s, 
                        country = %s, 
                        profile = %s, 
                        department_id = %s, 
                        unit = %s, 
                        qubical = %s, 
                        joining_date = %s, 
                        modified_by = %s, 
                        work_location_id = %s,
                        terminate_date = %s
                    WHERE employee_id = %s
                """, (
                first_name, last_name, email, address, country, profile, department_id, unit, qubical,
                joining_date, modified_by, work_location_id, termination_date, employee_id))
            conn2.commit()
            cur2.close()
            conn2.close()

            conn3 = DBConnection.get_db_connection()
            cur3 = conn3.cursor()
            cur3.execute("UPDATE employee_manager_relation "
                         " set employee_id = %s, manager_id = %s where id = %s",
                         (employee_id, manager_id, emp_mgr_id))
            conn3.commit()
            cur3.close()
            conn3.close()

            return jsonify({
                "success": True,
                "message": "Employee Updated successfully."
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 404


@employee_service.route('/employee/<int:emp_id>', methods=['DELETE'])
def deleteEmployee(emp_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("delete from employee_details WHERE employee_id = %s "
                , (emp_id,))
    affected_rows = cur.rowcount  # Get the number of deleted rows
    conn.commit()  # Commit the transaction to make sure the deletion is saved
    cur.close()
    conn.close()

    if affected_rows > 0:
        return jsonify({
            "success": True,
            "message": "Employee has been deleted"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Employee not found or could not be deleted"
        }), 404






@employee_service.route('/manager/<int:location_id>', methods=['GET'])
def getManagerByLocation(location_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select employee_id, first_name, last_name, email, address, country, profile, department_id, unit, "
                "qubical, joining_date, created_by, work_location_id, base64_encoding from employee_details WHERE profile = 'MGR' and work_location_id = %s "
                , (location_id,))
    employees = cur.fetchall()
    cur.close()
    conn.close()

    if employees is None:
        return jsonify({
            "success": False,
            "message": "No Manager has been found for given location id",
            "managers": []
        }), 201

    json_array = []
    for employee in employees:
        record_dict = {
            'employee_id': employee['employee_id'],
            'first_name': employee['first_name'],
            'last_name': employee['last_name'],
            'email': employee['email'],
            'address': employee['address'],
            'country': employee['country'],
            'profile': employee['profile'],
            'department_id': employee['department_id'],
            'unit': employee['unit'],
            'qubical': employee['qubical'],
            'joining_date': employee['joining_date'],
            'created_by': employee['created_by'],
            'work_location_id': employee['work_location_id'],
            'base64_encoding': employee['base64_encoding']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "managers": json_array
    }), 201


@employee_service.route('/employeeByManager/<int:manager_id>', methods=['GET'])
def getEmployeeByManager(manager_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select employee_id, first_name, last_name, email, address, country, profile, department_id, unit, "
                "qubical, joining_date, created_by, work_location_id, base64_encoding from employee_details "
                " WHERE terminate_date is null and "
                " employee_id in (select employee_id from employee_manager_relation where manager_id = %s) "
                , (manager_id,))
    employees = cur.fetchall()
    cur.close()
    conn.close()

    if employees is None:
        return jsonify({
            "success": False,
            "message": "No employee has been found for given manager id.",
            "employees": []
        }), 201

    json_array = []
    for employee in employees:
        record_dict = {
            'employee_id': employee['employee_id'],
            'first_name': employee['first_name'],
            'last_name': employee['last_name'],
            'email': employee['email'],
            'address': employee['address'],
            'country': employee['country'],
            'profile': employee['profile'],
            'department_id': employee['department_id'],
            'unit': employee['unit'],
            'qubical': employee['qubical'],
            'joining_date': employee['joining_date'],
            'created_by': employee['created_by'],
            'work_location_id': employee['work_location_id'],
            'base64_encoding': employee['base64_encoding']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "employees": json_array
    }), 201


@employee_service.route('/adminByLocationAndDepartment/<int:location_id>/<int:department_id>', methods=['GET'])
def getAdminByLocationAndDepartment(location_id, department_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_details WHERE profile = 'ADM' and work_location_id = %s and department_id = %s "
                , (location_id, department_id,))
    employees = cur.fetchall()
    cur.close()
    conn.close()

    if employees is None:
        return jsonify({
            "success": False,
            "message": "No Admin found for given location and department",
            "managers": []
        }), 201

    json_array = []
    for employee in employees:
        record_dict = {
            'employee_id': employee['employee_id'],
            'first_name': employee['first_name'],
            'last_name': employee['last_name'],
            'email': employee['email'],
            'address': employee['address'],
            'country': employee['country'],
            'profile': employee['profile'],
            'department_id': employee['department_id'],
            'unit': employee['unit'],
            'qubical': employee['qubical'],
            'joining_date': employee['joining_date'],
            'created_by': employee['created_by'],
            'work_location_id': employee['work_location_id'],
            'base64_encoding': employee['base64_encoding']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "managers": json_array
    }), 201
