#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited
import sys
import traceback
import structlog
from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'website', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'website', 'static'))

CONTENT_TYPE_APPLICATION_JSON = "application/json"
cors = CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})  # Compliant
app.config['CORS_HEADERS'] = 'Content-Type'

logger = structlog.getLogger(__name__)
internal_endpoints = ["/data", "/test"]
database_obj=''


def __flask_thread(port):
    try:
        app.run(host="0.0.0.0", port=port, threaded=True)
    except Exception:
        logger.error("Error in starting webserver: %s", str(traceback.format_exc()))


def start_web_server(dep_obj):
    global database_obj
    database_obj = dep_obj.database_connection
    master_config = dep_obj.master_config
    flask_config = master_config["config"]

    try:
        logger.info("Starting web server")

        if flask_config["securedServer"] == "Y":
            from attendance_reconciliation.generic.secured_web_server import initialize_secured_server
            from attendance_reconciliation.website.app import initialize_website_server
            initialize_secured_server()
            initialize_website_server(flask_config["baseUrl"])
        logger.info("Starting web server")
        __flask_thread(flask_config["port"])

    except Exception:
        logger.error("Error in starting web server: %s", str(traceback.format_exc()))
        sys.exit()