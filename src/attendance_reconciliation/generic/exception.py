'''
Created on Aug 29, 2019

@author: DELL
'''
import json

APPLICATION_JSON = 'application/json'


class ValidationError(Exception):
    """Exception raised while errors in modbus transaction.
 
    Attributes:
        response_code -- 
        message -- explanation of the error
    """

    def __init__(self, response_code, message):
        self.response_code = response_code
        self.message = message


class RequestNotFulfilledError(Exception):
    """Exception raised while errors in modbus transaction.

    Attributes:
        response_code --
        message -- explanation of the error
    """

    def __init__(self, response_code, message):
        self.response_code = response_code
        self.message = message

    def get_response(self, app):
        return app.response_class(
            response=json.dumps(self.__dict__),
            status=self.response_code,
            mimetype=APPLICATION_JSON
        )


class DataNotSentError(Exception):
    """Exception raised while errors in modbus transaction.

    Attributes:
        response_code --
        message -- explanation of the error
    """

    def __init__(self, response_code, message):
        self.response_code = response_code
        self.message = message

    def get_response(self, app):
        return app.response_class(
            response=json.dumps(self.__dict__),
            status=self.response_code,
            mimetype=APPLICATION_JSON
        )


class NoAlertFound(Exception):
    """Exception raised while errors in modbus transaction.

    Attributes:
        response_code --
        message -- explanation of the error
    """

    def __init__(self, response_code, message):
        self.response_code = response_code
        self.message = message


class ErrorResponse:
    def __init__(self, response_code, message, exception_message=""):
        self.response_code = response_code
        self.message = message + '\n' + exception_message

    def get_response(self, app):
        return app.response_class(
            response=json.dumps(self.__dict__),
            status=self.response_code,
            mimetype=APPLICATION_JSON
        )
