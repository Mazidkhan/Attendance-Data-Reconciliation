"""
Created on Aug 29, 2019

@author: DELL
"""
from schema import SchemaError
import structlog

from attendance_reconciliation.generic.exception import ValidationError

logger = structlog.getLogger(__name__)


class Validator:

    def __init__(self):
        logger.debug("Initialized validator")

    def __check(self, conf_schema, conf):
        try:
            conf_schema.validate(conf)
            return True
        except SchemaError as ex:
            logger.error("Schema Error", ex)
            return False

    def __validate(self, conf_schema, conf):
        try:
            return conf_schema.validate(conf)
        except SchemaError as ex:
            logger.error(str(ex))
            return False

    def validate_object(self, validation_schema, validation_object):
        if not self.__check(validation_schema, validation_object):
            raise ValidationError(400, "Validation Failed")
        return self.__validate(validation_schema, validation_object)
