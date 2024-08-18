import traceback
from sqlite3 import Error

import structlog

from attendance_reconciliation.database_specific.database_generic import GenericDatabase
from attendance_reconciliation.generic.exception import RequestNotFulfilledError

logger = structlog.getLogger(__name__)


class ReadonlyDB(GenericDatabase):

    def __init__(self, master_config, master_constants):
        db_file = master_constants["db_path"]
        super().__init__(db_file)

    def fetch_settings(self, device_id):
        setting_obj = {}
        sql_query = "SELECT id, name, value, edit_access from settings where device_id = ?;"
        try:
            logger.debug(sql_query)
            values = (device_id,)
            settings = self.fetch_execute(sql_query, values)
            for setting in settings:
                setting_obj[setting["name"]] = setting["value"]
            return setting_obj
        except Error as e:
            logger.error("Exception while fetching settings: %s", str(traceback.format_exc()))
            logger.error(e)

    def fetch_daisy_chain_settings(self):
        daisy_chain_device_list = []
        try:
            query = "select * from daisy_chain_settings;"
            values = ()
            devices = self.fetch_execute(query, values)
            for device in devices:
                device_obj = {"id": device["id"], "deviceId": device["device_id"]}
                daisy_chain_device_list.append(device_obj)
            return daisy_chain_device_list
        except Exception:
            logger.error("Could not save session %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not save session")

    def fetch_settings_by_name(self, device_id, name):
        setting_obj = {}
        sql_query = "SELECT id, name, value, edit_access from settings where device_id = ? and name = ?;"
        try:
            logger.debug(sql_query)
            values = (device_id, name,)
            settings = self.fetch_execute(sql_query, values)
            for setting in settings:
                setting_obj[setting["name"]] = setting["value"]

            return setting_obj[name] if name in setting_obj else None
        except Error as e:
            logger.error("Exception in select_all_from_current table: %s", str(traceback.format_exc()))
            logger.error(e)

    def fetch_node_list(self, device_id):
        device_list = []
        sql_query = "SELECT np.id, np.node_id, np.tag, np.param_identifier, np.parameter, " \
                    "np.unit, d.status FROM node_parameter np inner join device d ON np.node_id=d.node_id AND " \
                    "np.device_id=d.device_id where np.device_id=?" \
                    " order by np.node_id;"
        try:

            values = (device_id,)
            device_list = self.fetch_execute(sql_query, values)
        except Error as e:
            logger.error("Exception in select_all_from_current table: %s", str(traceback.format_exc()))
            logger.error(e)
        return device_list

    def insert_node_list(self, device_id, node_list):
        try:
            value_list = []
            sql_query = "insert or ignore INTO node_parameter (device_id, node_id, tag, " \
                        "param_identifier, parameter, unit) VALUES " \
                        "(?,?,?, ?,?,?)"
            for node in node_list:
                node_id = node["id"]
                tag = node["tagName"]
                parameters = node["parameters"]
                for param in parameters:
                    param_identifier = param["identifier"]
                    parameter = param["name"]
                    unit = param["unit"]
                    values = (device_id, node_id, tag, param_identifier.lower(), parameter, unit)
                    value_list.append(values)

            logger.debug("insert_ignore_node query is: %s and parameters %s", sql_query, str(value_list))
            self.bulk_execute(sql_query, value_list)
        except Error as e:
            logger.error("Exception in insert ignore current table: %s", str(traceback.format_exc()))
            logger.error(e)

    def insert_device(self, device_id, node_list):
        try:
            value_list = []
            sql_query = "insert or ignore INTO device (device_id, node_id, name, status) VALUES " \
                        "(?,?,?,?)"
            for node in node_list:
                node_id = node["id"]
                tag = node["tagName"]
                values = (device_id, node_id, tag, "ON")
                value_list.append(values)

            # logger.info("insert_ignore_node query is: %s and parameters %s", sql_query, str(value_list))
            self.bulk_execute(sql_query, value_list)
        except Error as e:
            logger.error("Exception in insert ignore current table: %s", str(traceback.format_exc()))
            logger.error(e)

    def insert_features_settings(self, device_id, pdu_features):
        try:
            value_list = []
            for key, value in pdu_features.items():
                if key == "name" or key == "location":
                    values = (device_id, key, value, "Y")
                else:
                    values = (device_id, key, value, "N")
                value_list.append(values)

            sql_query = "INSERT OR IGNORE INTO settings (device_id, name, value, edit_access) VALUES " \
                        "(?,?,?,?);"
            self.bulk_execute(sql_query, value_list)
        except Exception:
            logger.error("Error while inserting pdu settings %s", str(traceback.format_exc()))

    def insert_pdu_alert_details(self, device_id, device_alert_settings_list):
        try:
            pdu_channel_value_list = []
            for device in device_alert_settings_list:
                if not (device["nodeId"] == 100 or device["nodeId"] == 101 or device["nodeId"] == 102):
                    voltage_obj = device["settings"]["alerts"]["voltage"]
                    current_obj = device["settings"]["alerts"]["current"]
                    pdu_values = (device_id, device["nodeId"], device["name"],
                                  voltage_obj["under"], voltage_obj["over"], voltage_obj["warning"],
                                  current_obj["under"], current_obj["over"], current_obj["warning"])
                    pdu_channel_value_list.append(pdu_values)
            sql_query = "insert or ignore into pdu_channel(device_id, node_id, name, " \
                        "voltage_under, voltage_over, voltage_warning, " \
                        "current_under, current_over, current_warning) VALUES" \
                        "(?,?,?,     ?,?,?,    ?,?,?)"
            logger.info(pdu_channel_value_list)
            self.bulk_execute(sql_query, pdu_channel_value_list)
        except Exception:
            logger.error("Error while inserting pdu details %s", str(traceback.format_exc()))

    def fetch_device_settings_by_device_id(self, device_id):
        device_settings_list = []
        try:
            query = "select * from pdu_channel where device_id=?;"
            values = (device_id,)
            result_list = self.fetch_execute(query, values)
            for result in result_list:
                device_settings_obj = {"deviceId": result["device_id"], "nodeId": result["node_id"],
                                       "name": result["name"]}
                voltage_settings = {"under": result["voltage_under"], "over": result["voltage_over"],
                                    "warning": result["voltage_warning"]}
                current_settings = {"under": result["current_under"], "over": result["current_over"],
                                    "warning": result["current_warning"]}
                alert = {"voltage": voltage_settings, "current": current_settings}
                settings = {"alerts": alert}
                device_settings_obj["settings"] = settings
                device_settings_list.append(device_settings_obj)
        except Exception:
            logger.error("Could not save session %s", str(traceback.format_exc()))
            raise RequestNotFulfilledError(400, "Could not save session")
        return device_settings_list
