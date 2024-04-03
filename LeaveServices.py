from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
from datetime import datetime
import DBConnection


leave_service = Blueprint('leave_service', __name__)

@leave_service.route('/empLeave', methods=['POST'])
def addEmpLeave():

    employee_id = request.form.get('employee_id', None)
    leave_type_id = request.form.get('leave_type_id', None)
    description = request.form.get('description', None)
    from_date = request.form.get('from_date', None)
    to_date = request.form.get('to_date', None)
    created_by = request.form.get('created_by', None)
    status = 'pending'
    created_date = datetime.now()

    try:
        conn = DBConnection.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("INSERT INTO employee_leave "
                    " (employee_id, leave_type_id, description, from_date, to_date, status, created_by, "
                    " created_date) "
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                    (employee_id, leave_type_id, description, from_date, to_date, status, created_by,
                     created_date))
        new_leave_row = cur.fetchone()
        new_leave_id = new_leave_row['id']
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Leave created successfully.",
            "new_leave_id": new_leave_id
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


@leave_service.route('/empLeave/<int:leave_id>', methods=['PUT'])
def updateTicket(leave_id):
    comments = request.form.get('comments', None)
    status = request.form.get('status', None)
    modified_by = request.form.get('modified_by', None)
    modified_date = datetime.now()

    try:
        conn2 = DBConnection.get_db_connection()
        cur2 = conn2.cursor(cursor_factory=RealDictCursor)
        cur2.execute("""
            UPDATE employee_leave 
            SET status = %s,
                comments = %s,
                modified_by = %s,
                modified_date = %s
            WHERE id = %s
        """, (status, comments, modified_by, modified_date, leave_id))
        conn2.commit()
        cur2.close()
        conn2.close()

        return jsonify({
            "success": True,
            "message": "Leave Updated successfully."
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404



@leave_service.route('/empLeave/<int:leave_id>', methods=['GET'])
def getTicketById(leave_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_leave WHERE id = %s "
                , (leave_id,))
    leave = cur.fetchone()
    cur.close()
    conn.close()

    if leave is None:
        return jsonify({
            "success": True,
            "message": "Success",
            "leave": {}
        }), 201

    record_dict = {
        'id': leave['id'],
        'employee_id': leave['employee_id'],
        'leave_type_id': leave['leave_type_id'],
        'description': leave['description'],
        'from_date': leave['from_date'],
        'to_date': leave['to_date'],
        'status': leave['status'],
        'created_by': leave['created_by'],
        'modified_by': leave['modified_by'],
        'created_date': leave['created_date'],
        'modified_date': leave['modified_date'],
        'comments': leave['comments']
    }
    return jsonify({
        "success": True,
        "message": "Success",
        "leave": record_dict
    }), 201


@leave_service.route('/leaveByManager/<int:manager_id>/<status>', methods=['GET'])
def getLeaveByManager(manager_id, status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_leave WHERE status = %s and employee_id in "
                " (select employee_id from employee_manager_relation where manager_id = %s)"
                , (status,manager_id,))
    leaves = cur.fetchall()
    cur.close()
    conn.close()

    if leaves is None:
        return jsonify({
            "success": True,
            "message": "Success",
            "leaves": {}
        }), 201

    json_array = []
    for leave in leaves:
        record_dict = {
            'id': leave['id'],
            'employee_id': leave['employee_id'],
            'leave_type_id': leave['leave_type_id'],
            'description': leave['description'],
            'from_date': leave['from_date'],
            'to_date': leave['to_date'],
            'status': leave['status'],
            'created_by': leave['created_by'],
            'modified_by': leave['modified_by'],
            'created_date': leave['created_date'],
            'modified_date': leave['modified_date'],
            'comments': leave['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "tickets": json_array
    }), 201


@leave_service.route('/leaveByEmployee/<int:employee_id>/<status>', methods=['GET'])
def getLeaveByEmployee(employee_id, status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_leave WHERE status = %s and employee_id = %s"
                , (status,employee_id,))
    leaves = cur.fetchall()
    cur.close()
    conn.close()

    if leaves is None:
        return jsonify({
            "success": True,
            "message": "Success",
            "leaves": {}
        }), 201

    json_array = []
    for leave in leaves:
        record_dict = {
            'id': leave['id'],
            'employee_id': leave['employee_id'],
            'leave_type_id': leave['leave_type_id'],
            'description': leave['description'],
            'from_date': leave['from_date'],
            'to_date': leave['to_date'],
            'status': leave['status'],
            'created_by': leave['created_by'],
            'modified_by': leave['modified_by'],
            'created_date': leave['created_date'],
            'modified_date': leave['modified_date'],
            'comments': leave['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "leaves": json_array
    }), 201


@leave_service.route('/allLeaves', methods=['GET'])
def getAllLeaves():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_leave ")
    leaves = cur.fetchall()
    cur.close()
    conn.close()

    if leaves is None:
        return jsonify({
            "success": True,
            "message": "Success",
            "leaves": []
        }), 201

    json_array = []
    for leave in leaves:
        record_dict = {
            'id': leave['id'],
            'employee_id': leave['employee_id'],
            'leave_type_id': leave['leave_type_id'],
            'description': leave['description'],
            'from_date': leave['from_date'],
            'to_date': leave['to_date'],
            'status': leave['status'],
            'created_by': leave['created_by'],
            'modified_by': leave['modified_by'],
            'created_date': leave['created_date'],
            'modified_date': leave['modified_date'],
            'comments': leave['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "leaves": json_array
    }), 201

@leave_service.route('/leaveByStatus/<status>', methods=['GET'])
def getLeaveByStatus(status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_leave WHERE status = %s "
                , (status,))
    leaves = cur.fetchall()
    cur.close()
    conn.close()

    if leaves is None:
        return jsonify({
            "success": True,
            "message": "Success",
            "leaves": {}
        }), 201

    json_array = []
    for leave in leaves:
        record_dict = {
            'id': leave['id'],
            'employee_id': leave['employee_id'],
            'leave_type_id': leave['leave_type_id'],
            'description': leave['description'],
            'from_date': leave['from_date'],
            'to_date': leave['to_date'],
            'status': leave['status'],
            'created_by': leave['created_by'],
            'modified_by': leave['modified_by'],
            'created_date': leave['created_date'],
            'modified_date': leave['modified_date'],
            'comments': leave['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "leaves": json_array
    }), 201

@leave_service.route('/empLeave/<int:leave_id>', methods=['DELETE'])
def deleteEmployeeLeave(leave_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("delete from employee_leave WHERE id = %s "
                , (leave_id,))
    affected_rows = cur.rowcount  # Get the number of deleted rows
    conn.commit()  # Commit the transaction to make sure the deletion is saved
    cur.close()
    conn.close()

    if affected_rows > 0:
        return jsonify({
            "success": True,
            "message": "Leave has been deleted"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Leave not found or could not be deleted"
        }), 404
