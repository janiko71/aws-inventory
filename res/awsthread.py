import sys
from threading import Thread
import config

# =======================================================================================================================
#
#   Class created for (simple) multithreading
#
# =======================================================================================================================

class AWSThread(Thread):

    def __init__(self, aws_service, function_name, arg):

        Thread.__init__(self)
        self.function_name = function_name
        self.arg = arg
        self.aws_service = aws_service

    def run(self):
        
        """Code to execute"""
        config.__aws_service__ = self.function_name(self.arg)


