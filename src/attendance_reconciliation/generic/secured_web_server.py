#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited
import json
import traceback
from functools import wraps
import bcrypt
import jwt
import structlog
from flask_cors import cross_origin
from jwt import ExpiredSignatureError
from attendance_reconciliation.generic.exception import ErrorResponse, RequestNotFulfilledError
from attendance_reconciliation.generic.util import generate_jwt_token

logger = structlog.getLogger(__name__)
from flask import request, jsonify

from attendance_reconciliation.generic.web_server import app, database_obj


app.config['SECRET_KEY'] = 'kwVYKHCvT!eA7yvK'
CONTENT_TYPE_APPLICATION_JSON = "application/json"
# decorator for verifying the JWT


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        bearer_token = None
        if 'Authorization' in request.headers:
            bearer_token = request.headers['Authorization']
        if not bearer_token:
            return jsonify({'message': 'Token is missing !!'}), 401
        if not bearer_token.startswith("Bearer"):
            return jsonify({'message': 'Invalid token !!'}), 401
        try:
            token = bearer_token.replace("Bearer", "").strip()
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = {"userId": data["userId"], "name": data["name"], "role": data["role"]}
        except ExpiredSignatureError:
            return jsonify({
                'message': 'Token expired!!'
            }), 401
        except Exception:
            logger.error("Error while decoding jwt %s", str(traceback.format_exc()))
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/secured/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin()
@token_required
def get_user_details(current_user):
    if request.method == 'GET':
        try:
            users = database_obj.fetch_user_list()
            # logger.info(users)
            response = app.response_class(
                response=json.dumps(users),
                status=200,
                mimetype=CONTENT_TYPE_APPLICATION_JSON
            )
            return response
        except Exception as e:
            logger.error("Error in url /: %s", str(traceback.format_exc()))
            return 'Error while fetching network details', 400
    elif request.method == 'POST':
        try:
            incoming_data = json.loads(request.data)
            database_obj.add_user(incoming_data)
            response = app.response_class(
                response=json.dumps(incoming_data),
                status=200,
                mimetype=CONTENT_TYPE_APPLICATION_JSON
            )
            return response
        except RequestNotFulfilledError as e:
            logger.error("Error in url /: %s", str(traceback.format_exc()))
            return e.get_response(app)
    elif request.method == 'PUT':
        try:
            incoming_data = json.loads(request.data)
            logger.info(incoming_data)
            database_obj.edit_user(incoming_data)
            response = app.response_class(
                response=json.dumps(incoming_data),
                status=200,
                mimetype=CONTENT_TYPE_APPLICATION_JSON
            )
            return response
        except RequestNotFulfilledError as e:
            logger.error("Error in url /: %s", str(traceback.format_exc()))
            return e.get_response(app)
    elif request.method == 'DELETE':
        try:
            incoming_data = json.loads(request.data)
            user_id = incoming_data["userId"]
            database_obj.delete_user(user_id)

            response = app.response_class(
                response=json.dumps(incoming_data),
                status=200,
                mimetype=CONTENT_TYPE_APPLICATION_JSON
            )
            return response
        except Exception as e:
            logger.error("Error in url /: %s", str(traceback.format_exc()))
            return 'Error while fetching network details', 400


@app.route('/secured/users/login', methods=['POST'])
@cross_origin()
def login():
    """Login user."""
    global token
    try:
        incoming_data = json.loads(request.data)
        logger.debug(str(incoming_data))
        login_id = incoming_data["username"]
        user_list = database_obj.attempt_login(login_id)
        if len(user_list) == 1:
            input_password = incoming_data["password"]
            selected_user = user_list[0]
            user_id = selected_user["id"]
            name = selected_user["name"]
            login_id = selected_user["login_id"]
            hashed_password = selected_user["password"]
            role = selected_user["role"]
            is_equal = bcrypt.checkpw(input_password.encode("utf-8"), hashed_password)
            if is_equal:
                user = {"id": user_id, "name": name, "loginId": login_id, "role": role}
                token = generate_jwt_token(user, app.config['SECRET_KEY'])
                body = {"accessToken": token}
                logger.debug("Generated token %s", str(token))
                response = app.response_class(
                    response=json.dumps(body),
                    status=200,
                    mimetype=CONTENT_TYPE_APPLICATION_JSON
                )
                return response
            else:
                return jsonify({
                    'message': 'Invalid credentials'
                }), 401
        else:
            return jsonify({
                'message': 'Invalid credentials'
            }), 401
    except Exception:
        logger.error("Error while logging in %s", str(traceback.format_exc()))
        return jsonify({
            'message': 'Invalid credentials'
        }), 401


@app.route('/employees', methods=['POST'])
@cross_origin()
@token_required
def add_employee(current_user):
    """Adding Employee."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            employee_name = data_received["employee_name"]
            rfid = data_received["rfid"]
            erpnext_id = data_received["erpnext_id"]
            tag_name = data_received["tag_name"]
            database_obj.initialize_employee_details(employee_name, rfid, erpnext_id, tag_name)

            return "Employee Added Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees', methods=['GET'])
@cross_origin()
@token_required
def get_employee(current_user):
    """Getting Employee."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_employee_details()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees/<int:id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_employee(current_user,id):
    """Edit Employee."""
    try:
        if request.method == 'PUT':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            employee_name = data_received["employee_name"]
            rfid = data_received["rfid"]
            erpnext_id = data_received["erpnext_id"]
            tag_name = data_received["tag_name"]
            database_obj.edit_employee_details(id, employee_name, rfid, erpnext_id, tag_name)

            return "Employee Updated Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_employee(current_user,id):
    """Edit Employee."""
    try:
        if request.method == 'DELETE':
            database_obj.delete_employee_details(id)
            return "Employee Deleted Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees/<rfid>', methods=['GET'])
@cross_origin()
@token_required
def get_employee_rfid(current_user,rfid):
    """Getting Employee By RFID."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_employee_details_rfid(rfid)
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_slave', methods=['GET'])
@cross_origin()
@token_required
def get_employee_slave(current_user):
    """Getting Employee."""
    try:
        if request.method == 'GET':
            employee_slave=database_obj.fetch_employee_details_slave()
            return employee_slave
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_slave/<int:id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_employee_slave(current_user,id):
    """Getting Employee."""
    try:
        if request.method == 'PUT':
            database_obj.edit_employee_details_slave(id)
            return "Employee Updated"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/device', methods=['POST'])
@cross_origin()
@token_required
def add_device(current_user):
    """Adding Device."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            device_id = data_received["device_id"]
            tag_name = data_received["tag_name"]
            database_obj.initialize_device_details(device_id, tag_name)

            return "Device Added Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/device', methods=['GET'])
@cross_origin()
@token_required
def get_device(current_user):
    """Getting Device."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_device_details()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/device', methods=['PUT'])
@cross_origin()
@token_required
def edit_device(current_user):
    """Edit Device."""
    try:
        if request.method == 'PUT':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            id = data_received["id"]
            device_id = data_received["device_id"]
            tag_name = data_received["tag_name"]
            database_obj.edit_device_details(id, device_id, tag_name)

            return "Device Updated Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/device/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_device(current_user,id):
    """Edit Device."""
    try:
        if request.method == 'DELETE':
            database_obj.delete_device_details(id)
            return "Device Deleted Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/card_punch', methods=['POST'])
@cross_origin()
@token_required
def add_card_punch(current_user):
    """Adding CardPunch."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            device_id = data_received["device_id"]
            rfid = data_received["rfid"]
            tag_name = data_received["tag_name"]
            employee_name = data_received["employee_name"]
            erpnext_id = data_received["erpnext_id"]
            time = data_received["time"]
            punch_type = data_received["punch_type"]
            database_obj.initialize_card_punch_details(device_id, rfid, employee_name, erpnext_id, time, punch_type, tag_name)

            return "Card Punched Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/card_punch', methods=['GET'])
@cross_origin()
@token_required
def get_card_punch(current_user):
    """Getting CardPunch."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_card_punch_details()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/card_punch/<int:id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_card_punch(current_user,id):
    """Edit Card Punch."""
    try:
        if request.method == 'PUT':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            device_id = data_received["device_id"]
            rfid = data_received["rfid"]
            employee_name = data_received["employee_name"]
            erpnext_id = data_received["erpnext_id"]
            time = data_received["time"]
            punch_type = data_received["type"]
            database_obj.edit_card_punch_details(id, device_id, rfid, employee_name, erpnext_id, time, punch_type)

            return "Card Punch Updated Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/card_punch/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_card_punch(current_user,id):
    """Edit Device."""
    try:
        if request.method == 'DELETE':
            database_obj.delete_card_punch_details(id)
            return "Card Punch Deleted Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/unauthorized_access', methods=['POST'])
@cross_origin()
@token_required
def add_unauthorized_access(current_user):
    """Adding UnAuthorized Access."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            device_id = data_received["device_id"]
            tag_name = data_received["tag_name"]
            rfid = data_received["rfid"]
            time = data_received["time"]
            database_obj.initialize_unauthorized_access_details(device_id, rfid, time, tag_name)

            return "Unauthorized Access added Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/unauthorized_access', methods=['GET'])
@cross_origin()
@token_required
def get_unauthorized_access(current_user):
    """Getting UnAuthorized Access."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_unauthorized_access_details()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/unauthorized_access/<int:id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_unauthorized_access(current_user,id):
    """Edit Unauthorized Access Punch."""
    try:
        if request.method == 'PUT':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            device_id = data_received["device_id"]
            rfid = data_received["rfid"]
            time = data_received["time"]
            database_obj.edit_unauthorized_access_details(id, device_id, rfid, time)

            return "Unauthorized Access Updated Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/unauthorized_access/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_unauthorized_access(current_user,id):
    """Delete Unauthorized Access."""
    try:
        if request.method == 'DELETE':
            database_obj.delete_unauthorized_access_details(id)
            return "Unauthorized Access Deleted Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/attendance', methods=['POST'])
@cross_origin()
@token_required
def add_attendance(current_user):
    """Adding Attendance."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            employee_name = data_received["employee_name"]
            status = data_received["status"]
            date = data_received["date"]
            erpnext_id = data_received["erpnext_id"]
            database_obj.initialize_attendance_details(employee_name, date, status, erpnext_id)

            return "Attendance added Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/attendance', methods=['GET'])
@cross_origin()
@token_required
def get_attendance(current_user):
    """Getting Attendance."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_attendance_details()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/attendance/<int:id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_attendance(current_user,id):
    """Edit Attendance Details."""
    try:
        if request.method == 'PUT':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            employee_name = data_received["employee_name"]
            status = data_received["status"]
            date = data_received["date"]
            erpnext_id = data_received["erpnext_id"]
            database_obj.edit_attendance_details(id, employee_name, date, status, erpnext_id)
            return "Attendance Data Updated Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/attendance/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_attendance(current_user,id):
    """Delete Unauthorized Access."""
    try:
        if request.method == 'DELETE':
            database_obj.delete_attendance_details(id)
            return "Attendance Deleted Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh', methods=['POST'])
@cross_origin()
@token_required
def add_employee_wfh(current_user):
    """Adding Employee."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            employee_name = data_received["employee_name"]
            erpnext_id = data_received["erpnext_id"]
            database_obj.initialize_employee_details_work_from_home(employee_name, erpnext_id)

            return "Employee Added Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh', methods=['GET'])
@cross_origin()
@token_required
def get_employee_wfh(current_user):
    """Getting Employee."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_employee_details_work_from_home()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh/<int:id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_employee_wfh(current_user,id):
    """Edit Employee."""
    try:
        if request.method == 'PUT':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))
            employee_name = data_received["employee_name"]
            erpnext_id = data_received["erpnext_id"]
            database_obj.edit_employee_details_work_from_home(id, employee_name, erpnext_id)

            return "Employee Updated Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh/<int:id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_employee_wfh(current_user,id):
    """Edit Employee."""
    try:
        if request.method == 'DELETE':
            database_obj.delete_employee_details_work_from_home(id)
            return "Employee Deleted Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh_days', methods=['POST'])
@cross_origin()
@token_required
def add_employee_wfh_days(current_user):
    """Adding Employee."""
    try:
        if request.method == 'POST':
            data_received = request.json
            logger.info("Query parameters %s", str(data_received))

            erpnext_id = data_received["erpnext_id"]
            days = data_received["days"]
            database_obj.initialize_employee_details_work_from_home_days(erpnext_id, days)

            return "Employee Added Successfully"
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh_days', methods=['GET'])
@cross_origin()
@token_required
def get_employee_wfh_days(current_user):
    """Getting Employee."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_employee_details_work_from_home_days()
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh_days/<string:erpnext_id>', methods=['GET'])
@cross_origin()
@token_required
def get_employee_wfh_days_erp(current_user,erpnext_id):
    """Getting Employee."""
    try:
        if request.method == 'GET':
            return database_obj.fetch_employee_details_work_from_home_days_erp(erpnext_id)
        else:
            return 'HTTP Method not configured', 404
    except Exception:
        logger.error("Error in url /: %s", str(traceback.format_exc()))
        return 'Hello, world!', 500


@app.route('/employees_wfh_days/<string:erpnext_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_employee_wfh_days_erp(current_user, erpnext_id):
    """Delete work from home days for an employee."""
    try:
        # Extract the 'days' parameter from the request body
        request_data = request.get_json()
        days = request_data.get('days')

        if not days:
            return jsonify({"message": "No 'days' parameter provided"}), 400
        success = database_obj.delete_employee_details_work_from_home_days_erpnext_id(erpnext_id, days)

        if success:
            logger.info(f'Success:{success}')
            return jsonify({"message": "Days deleted successfully"}), 200
        else:
            return jsonify({"message": "Days not found"}), 404
    except Exception:
        logger.error("Error in URL /employees_wfh_days/%s: %s", erpnext_id, str(traceback.format_exc()))
        return jsonify({"message": "Internal server error"}), 500


def initialize_secured_server():
    logger.info("Initializing secured server")
