#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited

import os
import sys
import traceback
import structlog


from attendance_reconciliation.database_specific.database import LocalDB
from attendance_reconciliation.generic.constants import get_constants, CONFIG_FILE_NAME, SERVICE_NAME
from attendance_reconciliation.generic.default_settings import create_final_config_dict
from attendance_reconciliation.generic.dependent_object import DependentObject
from attendance_reconciliation.generic.logging_config import configure_logger
from attendance_reconciliation.generic.util import read_json_from_file
from attendance_reconciliation.generic.web_server import start_web_server
from attendance_reconciliation.specific.daily_attendance import DailyAttendance



def start_attendance_reconciliation(status):
    try:
        LOG_PATH, CONFIG_PATH, DB_PATH = get_constants(status.upper())
        config_file_data = os.path.join(CONFIG_PATH, CONFIG_FILE_NAME)
        full_config = read_json_from_file(config_file_data)
        configure_logger(full_config["logLevel"], SERVICE_NAME, LOG_PATH)
        logger = structlog.getLogger(__name__)
        final_config = create_final_config_dict(full_config)
        logger.info("Final config dict is: %s", str(final_config))

        master_config = {
            "config": final_config,
        }
        master_constants = {
            "log_path": LOG_PATH,
            "config_path": CONFIG_PATH,
            "db_path": DB_PATH,
        }

        db = LocalDB(master_config, master_constants)
        db.initialize_tables()
        dep_obj = DependentObject(db, master_config, master_constants)
        
        daily_attendance_details = DailyAttendance(dep_obj)
        dep_obj.daily_attendance_details = daily_attendance_details

        daily_attendance_details.start_background_task()
        start_web_server(dep_obj)

    except Exception:
        print("Error in starting main: %s", str(traceback.format_exc()))
        sys.exit()
