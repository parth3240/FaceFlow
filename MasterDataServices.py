from flask import Blueprint, jsonify
from psycopg2.extras import RealDictCursor
import DBConnection

master_data_service = Blueprint('master_data_service', __name__)

@master_data_service.route('/locations', methods=['GET'])
def getAllLocations():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT location_id, name FROM locations")
    locations = cur.fetchall()
    cur.close()
    conn.close()

    json_array = []

    for location in locations:
        record_dict = {
            'location_id': location['location_id'],
            'name': location['name']
        }
        json_array.append(record_dict)
    return jsonify(json_array)

@master_data_service.route('/departments', methods=['GET'])
def getAllDepartments():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT department_id, name FROM departments")
    locations = cur.fetchall()
    cur.close()
    conn.close()

    json_array = []

    for location in locations:
        record_dict = {
            'department_id': location['department_id'],
            'name': location['name']
        }
        json_array.append(record_dict)
    return jsonify(json_array)


@master_data_service.route('/issues', methods=['GET'])
def getAllIssues():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT issue_id, name FROM issues")
    locations = cur.fetchall()
    cur.close()
    conn.close()

    json_array = []

    for location in locations:
        record_dict = {
            'issue_id': location['issue_id'],
            'name': location['name']
        }
        json_array.append(record_dict)
    return jsonify(json_array)


@master_data_service.route('/leaveTypes', methods=['GET'])
def getAllLeaveTypes():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, leave_type, abbreviation FROM leave_types")
    leaves = cur.fetchall()
    cur.close()
    conn.close()

    if leaves is None:
        return jsonify({
            "success": True,
            "message": "No records for leave in DB",
            "managers": []
        }), 201

    json_array = []

    for leave in leaves:
        record_dict = {
            'leave_id': leave['id'],
            'leave_type': leave['leave_type'],
            'abbreviation': leave['abbreviation']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "leaves": json_array
    }), 201
