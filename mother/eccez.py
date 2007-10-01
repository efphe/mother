"""
Mother Exceptions.
"""

class MotherException(Exception):

    def __init__(self, value):
        self.value= value

    def __str__(self):
        return self.value

class QueryError(MotherException):
    def __init__(self, value= ''):
        MotherException.__init__(self,
                    "Query error - %s" % value)

class ConnectionError(MotherException):
    def __init__(self, value= ''):
        MotherException.__init__(self,
                "Db connection re-established: old session is lost.")

class BrokenConnection(MotherException):
    def __init__(self, value= ''):
        MotherException.__init__(self,
                    "Broken Connection :(")

class InsertError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot insert - %s" % value)

class SelectError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot select - %s" % value)

class UpdateError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot update - %s " % value)

class DeleteError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot delete - %s" % value)

class InternalError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Internal error - %s" % value)

class WrongTypeError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self, str(value))
        
class InvalidFilter(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self, str(value))
        
