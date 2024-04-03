from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor
import DBConnection
import random


ticket_service = Blueprint('ticket_service', __name__)

@ticket_service.route('/ticket', methods=['POST'])
def addTicket():

    employee_id = request.form.get('employee_id', None)
    issue_id = request.form.get('issue_id', None)
    description = request.form.get('description', None)
    ticket_date = request.form.get('ticket_date', None)
    work_location_id = request.form.get('work_location_id', None)
    status = 'pending'

    try:
        conn1 = DBConnection.get_db_connection()
        cur1 = conn1.cursor(cursor_factory=RealDictCursor)
        cur1.execute("select * from employee_details WHERE work_location_id = %s and profile = 'ADM' and terminate_date is null "
                    , (work_location_id,))
        admins = cur1.fetchall()

        if admins is None:
            return jsonify({
                "success": False,
                "message": "No Admin has been found to assign ticket",
                "employee_list": []
            }), 201

        employee_ids = [admin['employee_id'] for admin in admins]
        assigned_to = random.choice(employee_ids)
        cur1.close()
        conn1.close()

        conn = DBConnection.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("INSERT INTO employee_ticket "
                    " (employee_id, issue_id, description, ticket_date, status, created_by, assigned_to) "
                    " VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                    (employee_id, issue_id, description, ticket_date, status, employee_id, assigned_to))
        new_ticket_row = cur.fetchone()
        new_ticket_id = new_ticket_row['id']
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Ticket created successfully.",
            "new_ticket_id": new_ticket_id
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404



@ticket_service.route('/ticket/<int:ticket_id>', methods=['PUT'])
def updateTicket(ticket_id):
    comments = request.form.get('comments', None)
    status = request.form.get('status', None)
    modified_by = request.form.get('modified_by', None)

    try:
        conn2 = DBConnection.get_db_connection()
        cur2 = conn2.cursor(cursor_factory=RealDictCursor)
        cur2.execute("""
            UPDATE employee_ticket 
            SET status = %s,
                comments = %s,
                modified_by = %s
            WHERE id = %s
        """, (status, comments, modified_by, ticket_id))
        conn2.commit()
        cur2.close()
        conn2.close()

        return jsonify({
            "success": True,
            "message": "Ticket Updated successfully."
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


@ticket_service.route('/ticket/<int:ticket_id>', methods=['GET'])
def getTicketById(ticket_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_ticket WHERE id = %s "
                , (ticket_id,))
    ticket = cur.fetchone()
    cur.close()
    conn.close()

    if ticket is None:
        return jsonify({
            "success": False,
            "message": "No Ticket has been found for the given Id.",
            "ticket": {}
        }), 201

    record_dict = {
        'id': ticket['id'],
        'employee_id': ticket['employee_id'],
        'issue_id': ticket['issue_id'],
        'description': ticket['description'],
        'ticket_date': ticket['ticket_date'],
        'status': ticket['status'],
        'created_by': ticket['created_by'],
        'comments': ticket['comments'],
        'assigned_to': ticket['assigned_to']
    }
    return jsonify({
        "success": True,
        "message": "Success",
        "ticket": record_dict
    }), 201



@ticket_service.route('/ticketByManager/<int:manager_id>/<status>', methods=['GET'])
def getTicketByManager(manager_id, status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select id, employee_id, issue_id, description, ticket_date, status, created_by, modified_by, comments"
                " from employee_ticket WHERE status = %s and employee_id in "
                " (select employee_id from employee_manager_relation where manager_id = %s)"
                , (status,manager_id,))
    tickets = cur.fetchall()
    cur.close()
    conn.close()

    if tickets is None:
        return jsonify({
            "success": True,
            "message": "Success",
            "tickets": {}
        }), 201

    json_array = []
    for ticket in tickets:
        record_dict = {
            'id': ticket['id'],
            'employee_id': ticket['employee_id'],
            'issue_id': ticket['issue_id'],
            'description': ticket['description'],
            'ticket_date': ticket['ticket_date'],
            'status': ticket['status'],
            'created_by': ticket['created_by'],
            'modified_by': ticket['modified_by'],
            'comments': ticket['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "tickets": json_array
    }), 201



@ticket_service.route('/ticketByEmployee/<int:employee_id>/<status>', methods=['GET'])
def getTicketByEmployee(employee_id, status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_ticket WHERE status = %s and employee_id = %s"
                , (status,employee_id,))
    tickets = cur.fetchall()
    cur.close()
    conn.close()

    if tickets is None:
        return jsonify({
            "success": False,
            "message": "No ticket(s) has been found for given inputs.",
            "tickets": {}
        }), 201

    json_array = []
    for ticket in tickets:
        record_dict = {
            'id': ticket['id'],
            'employee_id': ticket['employee_id'],
            'issue_id': ticket['issue_id'],
            'description': ticket['description'],
            'ticket_date': ticket['ticket_date'],
            'status': ticket['status'],
            'created_by': ticket['created_by'],
            'assigned_to': ticket['assigned_to'],
            'comments': ticket['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "tickets": json_array
    }), 201


@ticket_service.route('/allTickets', methods=['GET'])
def getAllTickets():
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_ticket ")
    tickets = cur.fetchall()
    cur.close()
    conn.close()

    if tickets is None:
        return jsonify({
            "success": False,
            "message": "No Ticket(s) has been found.",
            "tickets": []
        }), 201

    json_array = []
    for ticket in tickets:
        record_dict = {
            'id': ticket['id'],
            'employee_id': ticket['employee_id'],
            'issue_id': ticket['issue_id'],
            'description': ticket['description'],
            'ticket_date': ticket['ticket_date'],
            'status': ticket['status'],
            'created_by': ticket['created_by'],
            'assigned_to': ticket['assigned_to'],
            'comments': ticket['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "tickets": json_array
    }), 201


@ticket_service.route('/ticketByStatus/<status>', methods=['GET'])
def getTicketByStatus(status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_ticket WHERE status = %s "
                , (status,))
    tickets = cur.fetchall()
    cur.close()
    conn.close()

    if tickets is None:
        return jsonify({
            "success": False,
            "message": "No ticket(s) has been found for the given status.",
            "tickets": {}
        }), 201

    json_array = []
    for ticket in tickets:
        record_dict = {
            'id': ticket['id'],
            'employee_id': ticket['employee_id'],
            'issue_id': ticket['issue_id'],
            'description': ticket['description'],
            'ticket_date': ticket['ticket_date'],
            'status': ticket['status'],
            'created_by': ticket['created_by'],
            'assigned_to': ticket['assigned_to'],
            'comments': ticket['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "tickets": json_array
    }), 201


@ticket_service.route('/ticket/<int:ticket_id>', methods=['DELETE'])
def deleteEmployee(ticket_id):
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("delete from employee_ticket WHERE id = %s "
                , (ticket_id,))
    affected_rows = cur.rowcount  # Get the number of deleted rows
    conn.commit()  # Commit the transaction to make sure the deletion is saved
    cur.close()
    conn.close()

    if affected_rows > 0:
        return jsonify({
            "success": True,
            "message": "Ticket has been deleted"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Ticket not found or could not be deleted"
        }), 404


@ticket_service.route('/getTicketsByAdmin/<int:admin_id>/<status>', methods=['GET'])
def getTicketsByAdmin(admin_id, status):
    if status is None:
        status = 'pending'
    conn = DBConnection.get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("select * from employee_ticket WHERE status = %s and assigned_to = %s "
                , (status,admin_id,))
    tickets = cur.fetchall()
    cur.close()
    conn.close()

    if tickets is None:
        return jsonify({
            "success": False,
            "message": "No Ticket(s) has been found for the given inputs.",
            "tickets": {}
        }), 201

    json_array = []
    for ticket in tickets:
        record_dict = {
            'id': ticket['id'],
            'employee_id': ticket['employee_id'],
            'issue_id': ticket['issue_id'],
            'description': ticket['description'],
            'ticket_date': ticket['ticket_date'],
            'status': ticket['status'],
            'created_by': ticket['created_by'],
            'assigned_to': ticket['assigned_to'],
            'comments': ticket['comments']
        }
        json_array.append(record_dict)
    return jsonify({
        "success": True,
        "message": "Success",
        "tickets": json_array
    }), 201

