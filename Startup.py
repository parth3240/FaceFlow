from flask import Flask
from MasterDataServices import master_data_service
from EmployeeServices import employee_service
from TicketServices import ticket_service
from AuthenticationService import auth_service
from LeaveServices import leave_service


app = Flask(__name__)

# Register each Blueprint
app.register_blueprint(master_data_service)
app.register_blueprint(employee_service)
app.register_blueprint(ticket_service)
app.register_blueprint(auth_service)
app.register_blueprint(leave_service)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

