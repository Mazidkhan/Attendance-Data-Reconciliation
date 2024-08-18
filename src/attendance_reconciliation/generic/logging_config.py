#  Copyright (C) VAA Technologies Private Limited - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by VAA Technologies Private Limited


import datetime
import logging.config
import os

from structlog import configure, processors, stdlib, threadlocal


def unixtime_processor(_, __, event_dict):
    now = datetime.datetime.now()
    header_time_format_string = str(now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3])
    event_dict['date_time'] = header_time_format_string
    return event_dict


def service_name_processor(_, __, event_dict):
    event_dict['service'] = name_of_service
    return event_dict


# noinspection PyTypeChecker,PyGlobalUndefined
def configure_logger(level, service_name, log_path):
    global name_of_service
    name_of_service = service_name
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] [%(levelname)s]  %(name)s %(lineno)d: %(message)s'
            }
        },
        'handlers': {
            'console': {
                '()': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'level_file': {
                'level': level,
                '()': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_path, name_of_service + "-" + level + ".log"),
                'backupCount': 10,
                'when': 'midnight',
                'interval': 1,
                'formatter': 'default'
            },
            'error_file': {
                'level': 'ERROR',
                '()': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_path, name_of_service + "-error.log"),
                'backupCount': 10,
                'when': 'midnight',
                'interval': 1,
                'formatter': 'default'
            },

        },
        'loggers': {
            '': {
                'level': level,
                'handlers': ['level_file', 'error_file', 'console']
            }
        }
    })

    configure(
        context_class=threadlocal.wrap_dict(dict),
        logger_factory=stdlib.LoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        processors=[
            stdlib.filter_by_level,
            stdlib.add_logger_name,
            stdlib.add_log_level,
            stdlib.PositionalArgumentsFormatter(),
            processors.TimeStamper(),
            processors.StackInfoRenderer(),
            unixtime_processor,
            service_name_processor,
            processors.format_exc_info,
            processors.UnicodeDecoder(),
            stdlib.render_to_log_kwargs
        ]
    )
