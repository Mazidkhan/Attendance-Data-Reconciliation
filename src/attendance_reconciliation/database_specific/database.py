#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited
import traceback
import uuid
from datetime import datetime
from sqlite3 import Error
from flask import jsonify
import bcrypt as bcrypt
import structlog

from attendance_reconciliation.database_specific.database_generic import GenericDatabase
from attendance_reconciliation.generic.exception import RequestNotFulfilledError

logger = structlog.getLogger(__name__)
class LocalDB(GenericDatabase):

    def __init__(self, master_config, master_constants):
        """ create a database connection to a SQLite database """
        db_file = master_constants["db_path"]
        self.config_path = master_constants["config_path"]

        super().__init__(db_file)
        try:
            self.SQL_CREATE_CARD_PUNCH_TABLE = """ CREATE TABLE IF NOT EXISTS card_punch (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                device_id INT,
                                                tag_name TEXT,
                                                rfid VARCHAR(255),
                                                employee_name VARCHAR(255),
                                                erpnext_id TEXT,
                                                time TIMESTAMP,
                                                punch_type string
                                            );
                                        """
            self.SQL_CREATE_EMPLOYEE_DETAILS_TABLE = """CREATE TABLE IF NOT EXISTS employee_details (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        employee_name TEXT,
                                                        tag_name TEXT,
                                                        rfid TEXT UNIQUE,
                                                        erpnext_id TEXT UNIQUE,
                                                        status TEXT DEFAULT 'N'
                                                );
                                                """
            self.SQL_CREATE_UNAUTHORIZED_ACCESS_TABLE = """ CREATE TABLE IF NOT EXISTS unauthorized_access (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                device_id INT,
                                                tag_name TEXT,
                                                rfid TEXT UNIQUE,
                                                time TIMESTAMP
                                            );
                                            """
            self.SQL_CREATE_DEVICE_TABLE = """ CREATE TABLE IF NOT EXISTS device (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                device_id INT,
                                                tag_name VARCHAR(255)
                                            );
                                           """
            self.SQL_CREATE_ATTENDANCE_TABLE = """ CREATE TABLE IF NOT EXISTS attendance (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                employee string,
                                                attendance_date DATE ,
                                                status string,
                                                company TEXT DEFAULT 'VAA Technologies Private Limited',
                                                docstatus TEXT DEFAULT '1',
                                                erpnext_id TEXT,
                                                UNIQUE(erpnext_id, attendance_date)
                                            );
                                           """
            self.SQL_CREATE_USER_TABLE = """ CREATE TABLE IF NOT EXISTS user (
                                               id TEXT PRIMARY KEY, 
                                               name TEXT NOT NULL, 
                                               login_id TEXT NOT NULL,
                                               password TEXT NOT NULL,
                                               role TEXT NOT NULL,
                                               active TEXT DEFAULT 'Y' NOT NULL,                                               
                                               UNIQUE(login_id)
                                           ); """
            self.SQL_CREATE_WORK_FROM_HOME_TABLE = """CREATE TABLE IF NOT EXISTS work_from_home (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        employee_name TEXT,
                                                        erpnext_id TEXT UNIQUE
                                                    );
                                                   """
            self.SQL_CREATE_WORK_FROM_HOME_DAYS_TABLE = """CREATE TABLE IF NOT EXISTS work_from_home_days (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        erpnext_id TEXT,
                                                        days TEXT
                                                    );
                                                   """


        except Error as e:
            logger.error("Exception in creating database object: %s", str(traceback.format_exc()))
            logger.error(e)

    def initialize_tables(self):
        if self.conn is not None:
            self.create_table(self.SQL_CREATE_CARD_PUNCH_TABLE)
            self.create_table(self.SQL_CREATE_EMPLOYEE_DETAILS_TABLE)
            self.create_table(self.SQL_CREATE_UNAUTHORIZED_ACCESS_TABLE)
            self.create_table(self.SQL_CREATE_DEVICE_TABLE)
            self.create_table(self.SQL_CREATE_ATTENDANCE_TABLE)
            self.create_table(self.SQL_CREATE_USER_TABLE)
            self.create_table(self.SQL_CREATE_WORK_FROM_HOME_TABLE)
            self.create_table(self.SQL_CREATE_WORK_FROM_HOME_DAYS_TABLE)
            self.insert_default_user()


    def insert_default_user(self):
        try:
            name="Admin"
            loginId="Admin"
            role="ADMIN"
            active="Y"
            sql_query = "INSERT INTO user (id, name, login_id, password, role, active) VALUES " \
                        "(?, ?, ?, ?, ?, ?);"
            user_id = str(uuid.uuid4())
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw("12345678".encode('utf-8'), salt)
            values = (user_id, name, loginId, hashed_password, role,active)

            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while adding user: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def initialize_employee_details_work_from_home(self,employee_name,erpnext_id):
        logger.info("Initializing employees")
        value_list = []

        values = (employee_name,erpnext_id)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO work_from_home (employee_name, erpnext_id) VALUES " \
                        "(?,?);"
        self.bulk_execute(sql_query, value_list)


    def fetch_employee_details_work_from_home(self):
        try:
            query = "select * from work_from_home;"
            values = ()
            employees = self.fetch_execute(query, values)
            return jsonify(employees)
        except Exception:
            logger.error("Could not fetch employees work from home %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch employees work from home")


    def edit_employee_details_work_from_home(self, id, employee_name, erpnext_id):
        try:
            sql_query = "UPDATE work_from_home SET employee_name = ?, erpnext_id = ? where id = ?;"
            values = (employee_name,erpnext_id,id)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating device table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_employee_details_work_from_home(self, id):
        try:
            sql_query = "DELETE from work_from_home where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from device table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def initialize_employee_details(self, employee_name, rfid, erpnext_id, tag_name):
        logger.info("Initializing employees")
        value_list = []

        values = (employee_name, rfid, erpnext_id, tag_name)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO employee_details (employee_name, rfid, erpnext_id, tag_name) VALUES " \
                        "(?,?,?,?);"
        self.bulk_execute(sql_query, value_list)

    def fetch_employee_details(self):
        try:
            query = "select * from employee_details;"
            values = ()
            employees = self.fetch_execute(query, values)
            return jsonify(employees)
        except Exception:
            logger.error("Could not fetch employees %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch employees")


    def fetch_employee_details_slave(self):
        try:
            query = "select * from employee_details where status = 'N';"
            values = ()
            employees = self.fetch_execute(query, values)
            return jsonify(employees)
        except Exception:
            logger.error("Could not fetch employees %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch employees")


    def edit_employee_details(self, id, employee_name, rfid, erpnext_id, tag_name):
        try:
            sql_query = "UPDATE employee_details SET employee_name = ?, rfid = ?, tag_name = ?, erpnext_id = ? where id = ?;"
            values = (employee_name, rfid, tag_name, erpnext_id, id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating employee table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def edit_employee_details_slave(self,id):
        try:
            sql_query = "UPDATE employee_details SET status='Y' where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating employee table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def initialize_employee_details_work_from_home_days(self, erpnext_id, days):
        logger.info("Initializing employees wfh days")
        value_list = []

        values = (erpnext_id, days)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO work_from_home_days (erpnext_id, days) VALUES " \
                    "(?,?);"
        self.bulk_execute(sql_query, value_list)


    def fetch_employee_details_work_from_home_days(self):
        try:
            query = "select * from work_from_home_days"
            values = ()
            employees = self.fetch_execute(query, values)
            return jsonify(employees)
        except Exception:
            logger.error("Could not fetch employees work from home days %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch employees work from home days")


    def fetch_employee_details_work_from_home_days_erp(self,erpnext_id):
        try:
            query = "select * from work_from_home_days where erpnext_id = ?;"
            values = (erpnext_id,)

            employees = self.fetch_execute(query, values)
            return jsonify(employees)
        except Exception:
            logger.error("Could not fetch employees work from home days by erpnext_id %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch employees work from home days by erp")


    def delete_work_from_home_days_details(self, id):
        try:
            sql_query = "DELETE from work_from_home_days where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from device table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_employee_details_work_from_home_days_erpnext_id(self, erpnext_id,days):
        try:
            sql_query = "DELETE from work_from_home_days where erpnext_id = ? and days= ? ;"
            values = (erpnext_id, days,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from employees work from home days by erp table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_employee_details(self, id):
        try:
            sql_query = "delete from employee_details where id=?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting employee table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def fetch_employee_details_rfid(self, rfid):
        try:
            query = "select * from employee_details where rfid=?;"
            values = (rfid,)
            employees = self.fetch_execute(query, values)
            return jsonify(employees)
        except Exception:
            logger.error("Could not fetch employees by rfid %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch employees by rfid")


    def initialize_device_details(self, device_id, tag_name):
        logger.info("Initializing devices")
        value_list = []

        values = (device_id, tag_name)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO device (device_id, tag_name) VALUES " \
                        "(?,?);"
        self.bulk_execute(sql_query, value_list)


    def fetch_device_details(self):
        try:
            query = "select * from device;"
            values = ()
            devices = self.fetch_execute(query, values)
            return jsonify(devices)
        except Exception:
            logger.error("Could not fetch devices %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch devices")


    def edit_device_details(self, id, device_id, tag_name):
        try:
            sql_query = "UPDATE device SET device_id = ?, tag_name = ? where id = ?;"
            values = (device_id, tag_name, id)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating device table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_device_details(self, id):
        try:
            sql_query = "DELETE from device where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from device table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def initialize_card_punch_details(self, device_id, rfid, employee_name, erpnext_id, time, punch_type, tag_name):
        logger.info("Initializing card punch details")
        value_list = []

        values = (device_id, rfid, employee_name,  erpnext_id, time, punch_type, tag_name)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO card_punch (device_id, rfid, employee_name,  erpnext_id, time, punch_type, tag_name) VALUES " \
                    "(?,?,?,?,?,?,?);"
        self.bulk_execute(sql_query, value_list)


    def fetch_card_punch_details(self):
        try:
            query = "select * from card_punch;"
            values = ()
            card_punch_details = self.fetch_execute(query, values)
            return jsonify(card_punch_details)
        except Exception:
            logger.error("Could not fetch card_punch %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch card_punch")


    def edit_card_punch_details(self, id, device_id, rfid, employee_name, erpnext_id, time, punch_type):
        try:
            sql_query = "UPDATE card_punch SET device_id = ?, rfid = ?, employee_name = ?,  erpnext_id = ?, time = ?, punch_type = ?  where id = ?;"
            values = (device_id, rfid, employee_name, erpnext_id, time, punch_type, id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating card punch table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_card_punch_details(self, id):
        try:
            sql_query = "DELETE from card_punch where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from card punch table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def initialize_unauthorized_access_details(self, device_id, rfid, time, tag_name):
        logger.info("Initializing unauthorized access details")
        value_list = []

        values = (device_id, rfid, time, tag_name)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO unauthorized_access (device_id, rfid, time, tag_name) VALUES " \
                    "(?,?,?,?);"
        self.bulk_execute(sql_query, value_list)


    def fetch_unauthorized_access_details(self):
        try:
            query = "SELECT * FROM unauthorized_access WHERE time >= datetime('now', '-7 days');"

            values = ()
            unauthorized_access_details = self.fetch_execute(query, values)
            return jsonify(unauthorized_access_details)
        except Exception:
            logger.error("Could not fetch unauthorized_access %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch unauthorized_access")


    def edit_unauthorized_access_details(self, id, device_id, rfid, time):
        try:
            sql_query = "UPDATE unauthorized_access SET device_id = ?, rfid = ?, time = ? where id = ?;"
            values = (device_id, rfid, time, id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating unauthorized access table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_unauthorized_access_details(self, id):
        try:
            sql_query = "DELETE from unauthorized_access where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from unauthorized access table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def initialize_attendance_details(self, employee, attendance_date, status, erpnext_id):
        logger.info("Initializing attendance details")
        value_list = []
        values = (employee, attendance_date, status, erpnext_id)
        value_list.append(values)
        sql_query = "INSERT OR IGNORE INTO attendance (employee, attendance_date, status, erpnext_id) VALUES " \
                    "(?,?,?,?);"
        self.bulk_execute(sql_query, value_list)


    def fetch_attendance_details(self):
        try:
            query = "select * from attendance;"
            values = ()
            attendance_details = self.fetch_execute(query, values)
            return jsonify(attendance_details)
        except Exception:
            logger.error("Could not fetch attendance %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch attendance")


    def edit_attendance_details(self, id, employee_name, attendance_date, status, erpnext_id):
        try:
            sql_query = "UPDATE attendance SET employee = ?, status = ?, attendance_date = ?, erpnext_id=? where id = ?;"
            values = (employee_name, status, attendance_date, erpnext_id, id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating attendance table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def delete_attendance_details(self, id):
        try:
            sql_query = "DELETE from attendance where id = ?;"
            values = (id,)
            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting from attendance table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))


    def fetch_daily_attendance_details(self):
        try:
            query = """-- Get employees who have data in card_punch table
                    WITH attendance_status AS (
                        SELECT 
                            employee_name, 
                            CASE 
                                WHEN MIN(TIME(time)) <= '10:05' AND MAX(TIME(time)) >= '17:55' THEN 'Present'
                                ELSE 'Half Day' 
                            END AS status, 
                            DATE(time) AS date, 
                            erpnext_id 
                        FROM 
                            card_punch 
                        GROUP BY 
                            employee_name, 
                            DATE(time), 
                            erpnext_id
                    ),
                    -- Get work-from-home employees based on days
                    work_from_home_status AS (
                        SELECT 
                            ed.employee_name, 
                            'Work From Home' AS status, 
                            DATE('now') AS date, 
                            ed.erpnext_id 
                        FROM 
                            employee_details ed 
                        JOIN 
                            work_from_home_days wfh 
                        ON 
                            ed.erpnext_id = wfh.erpnext_id 
                        WHERE 
                            wfh.days = CAST(strftime('%w', 'now') AS TEXT)
                    )
                    -- Combine both results
                    SELECT 
                        employee_name, 
                        status, 
                        date, 
                        erpnext_id 
                    FROM 
                        attendance_status
                    UNION
                    SELECT 
                        employee_name, 
                        status, 
                        date, 
                        erpnext_id 
                    FROM 
                        work_from_home_status;
                    """
            values = ()
            daily_attendance_details = self.fetch_execute(query, values)
            return daily_attendance_details
        except Exception:
            logger.error("Could not fetch attendance %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch attendance")


    def fetch_attendance_details_api(self):
        try:
            query = """SELECT employee,attendance_date,status,company,docstatus,erpnext_id
                        FROM attendance WHERE attendance_date = CURRENT_DATE;"""
            values = ()
            api_attendance_details = self.fetch_execute(query, values)
            return api_attendance_details
        except Exception:
            logger.error("Could not fetch attendance %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch api attendance")

    def fetch_attendance_details_daily_absent(self):
        try:
            query = """SELECT
                            ed.employee_name AS employee_name,
                            DATE('now') AS date,
                            'Absent' AS status,
                            ed.erpnext_id AS erpnext_id 
                        FROM
                            employee_details ed 
                        LEFT JOIN attendance att 
                            ON ed.employee_name = att.employee 
                            AND att.attendance_date = DATE('now')
                        LEFT JOIN work_from_home_days wfh 
                            ON ed.erpnext_id = wfh.erpnext_id 
                            AND wfh.days = CAST(strftime('%w', 'now') AS TEXT)
                        WHERE
                            att.employee IS NULL 
                            AND NOT (wfh.erpnext_id IS NOT NULL AND wfh.days = CAST(strftime('%w', 'now') AS TEXT));
                    """
            values = ()
            daily_absent_attendance_details = self.fetch_execute(query, values)
            return daily_absent_attendance_details
        except Exception:
            logger.error("Could not fetch attendance %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not fetch attendance")

    def initialize_daily_attendance_details(self):
        employees = self.fetch_daily_attendance_details()
        logger.info("Initializing attendance details")
        value_list = []
        for employee in employees:
            values = (employee['employee_name'], employee['status'], employee['date'], employee['erpnext_id'])
            value_list.append(values)
        sql_query = "INSERT OR REPLACE INTO attendance (employee, status, attendance_date, erpnext_id) VALUES " \
                        "(?,?,?,?);"
        self.bulk_execute(sql_query, value_list)

    def initialize_attendance_details_daily_absent(self, ):
        employee = self.fetch_attendance_details_daily_absent()
        logger.info("Initializing attendance details")
        value_list = []
        for employee in employee:
            values = (employee['employee_name'], employee['status'], employee['date'], employee['erpnext_id'])
            value_list.append(values)
        sql_query = "INSERT OR REPLACE INTO attendance (employee, status, attendance_date, erpnext_id) VALUES " \
                        "(?,?,?,?);"
        self.bulk_execute(sql_query, value_list)

    def attempt_login(self, login_id):
        sql_query = "SELECT id, name, login_id, password, role from user where login_id = ? and active = 'Y';"
        try:
            cur = self.conn.cursor()
            logger.debug(sql_query)
            values = (login_id,)
            cur.execute(sql_query, values)
            rows = cur.fetchall()
            dict_rows = [dict(ix) for ix in rows]
            self.conn.commit()
            cur.close()
            return dict_rows
        except Error as e:
            logger.error("Exception while attempting login: %s", str(traceback.format_exc()))
            logger.error(e)

    def fetch_user_list(self):
        user_list = []
        sql_query = "SELECT id, name, login_id, password, role, active from user;"
        try:
            logger.debug(sql_query)
            values = ()
            users = self.fetch_execute(sql_query, values)
            for user in users:
                user_obj = {"id": user["id"], "name": user["name"],
                            "loginId": user["login_id"], "role": user["role"], "active": user["active"]}
                user_list.append(user_obj)
            return user_list
        except Error:
            logger.error("Exception while fetching user list: %s", str(traceback.format_exc()))

    def add_user(self, user_obj):
        try:
            sql_query = "INSERT INTO user (id, name, login_id, password, role, active) VALUES " \
                        "(?, ?, ?, ?, ?, ?);"
            user_id = str(uuid.uuid4())
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw("12345678".encode('utf-8'), salt)
            values = (user_id, user_obj["name"], user_obj["loginId"], hashed_password, user_obj["role"],
                      user_obj["active"])

            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while adding user: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))

    def edit_user(self, user_obj):
        try:
            sql_query = "UPDATE user SET name = ?, login_id = ?, role = ?, active =? where id = ?;"
            user_id = user_obj["id"]
            values = (user_obj["name"], user_obj["loginId"], user_obj["role"],
                      user_obj["active"], user_id)

            logger.debug(sql_query)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while updating user table: %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, str(traceback.format_exc()))

    def delete_user(self, user_id):

        try:
            sql_query = "delete from user where id = ?;"
            logger.debug(sql_query)
            values = (user_id,)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while deleting user: %s", str(traceback.format_exc()))

    def change_password(self, user_id, new_password):
        try:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            sql_query = "update user set password = ?, active='Y' where id = ?;"
            logger.debug(sql_query)
            values = (hashed_password, user_id,)
            self.query_execute(sql_query, values)
        except Error:
            logger.error("Exception while changing user password: %s", str(traceback.format_exc()))

    def close_connection(self):
        try:
            if self.conn:
                self.conn.close()
        except Error as e:
            logger.error("Exception in closing connection: %s", str(traceback.format_exc()))
            logger.error(e)
