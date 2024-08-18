#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited

default_config = {
    "logLevel": "DEBUG",
    "port": 2011,
    "allowedInternalIP": ["127.0.0.1"],
    "acquisitionInterval": 60000,
    "securedServer": "Y",
    "localhostEnabled": "N",
    "baseUrl":'',
    "apiUrl":'',
    "apiToken":'',
    "deviceId": "1"
}


def create_final_config_dict(config):
    final_config = default_config.copy()
    for key, value in final_config.items():
        if key in config.keys():
            final_config[key] = config[key]
    return final_config
