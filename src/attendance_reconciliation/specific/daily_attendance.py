import json
import threading
import time
import traceback

import requests
import schedule
import structlog

logger = structlog.getLogger(__name__)


class DailyAttendance:

    def __init__(self, dep_obj):
        try:
            self.database_obj = dep_obj.database_connection
            self.master_config = dep_obj.master_config
            self.flask_config = self.master_config["config"]
            self.api_url = self.flask_config["apiUrl"]
            self.api_token = self.flask_config["apiToken"]
            self.headers = {
                'Authorization': f'token {self.api_token}',
                'Content-Type': 'application/json'
            }
        except AttributeError as e:
            logger.error(f"Error during initialization: {e}")
        except KeyError as e:
            logger.error(f"Missing key in configuration: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")

    def start_background_task(self):
        try:
            thread = threading.Thread(target=self.attendance_generate_function)
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Error starting background task: {e}")

    def attendance_generate_function(self):
        try:
            schedule.every().day.at("20:00").do(self.api_daily_data)
            while True:
                schedule.run_pending()
                logger.info("Executing attendance generation...")
                self.database_obj.initialize_daily_attendance_details()
                logger.info("Attendance updated successfully")
                time.sleep(5)
        except Exception as e:
            logger.error(f"Error during attendance generation: {e}")

    def api_daily_data(self):
        try:
            self.database_obj.initialize_attendance_details_daily_absent()
            employees = self.database_obj.fetch_attendance_details_api()

            for employee in employees:
                try:
                    data = {
                        "employee": employee['employee'],
                        "attendance_date": employee['attendance_date'],
                        "status": employee['status'],
                        "company": employee['company'],
                        "docstatus": employee['docstatus']
                    }
                    # Send the data via POST request
                    if employee['employee'] in ['Akshay Anil Sathe', 'Anand Rajesh Vartak']:
                        requests.post(self.api_url, headers=self.headers, json=data)
                        logger.info(f'Employee:{employee} Data sent successfully!')

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error while sending data for employee {employee['employee']}: {e}")
                except KeyError as e:
                    logger.error(f"Missing key in employee data: {e}")
                except Exception as e:
                    logger.debug(f"Unexpected error processing employee data: "
                                 f"{json.dumps(employee)} {str(traceback.format_exc())}")
                    logger.debug("Unexpected error processing employee data: %s %s", json.dumps(employee),
                                 str(traceback.format_exc()))
        except Exception as e:
            logger.error(f"Error in api_daily_data method: {e}")
