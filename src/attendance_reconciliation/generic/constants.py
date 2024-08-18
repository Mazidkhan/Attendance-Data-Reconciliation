#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited

import os

from attendance_reconciliation.default.dev import DEV_LOG_PATH, DEV_CONFIG_PATH, DEV_DB_PATH
from attendance_reconciliation.default.prod import PROD_LOG_PATH, PROD_CONFIG_PATH, PROD_DB_PATH

SERVICE_NAME = "attendance_reconciliation"
PORT = 2007
CONFIG_FILE_NAME = "config.json"

def get_constants(name):
    if name.upper() == "DEV":
        LOG_PATH = DEV_LOG_PATH
        CONFIG_PATH = DEV_CONFIG_PATH
        DB_PATH = os.path.join(DEV_DB_PATH, "{}.db".format(SERVICE_NAME))
    else:
        LOG_PATH = PROD_LOG_PATH
        CONFIG_PATH = PROD_CONFIG_PATH
        DB_PATH = os.path.join(PROD_DB_PATH, "{}.db".format(SERVICE_NAME))
    return LOG_PATH, CONFIG_PATH, DB_PATH
