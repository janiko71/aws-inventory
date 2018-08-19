import sys
from threading import Thread
import config

# =======================================================================================================================
#
#   Class created for (simple) multithreading
#
# =======================================================================================================================

class AWSThread(Thread):

    def __init__(self, aws_service, fonction, arg):
        Thread.__init__(self)
        self.fonction = fonction
        self.arg = arg
        self.aws_service = aws_service

    def run(self):
        """Code à exécuter"""
        config.__aws_service__ = self.fonction(self.arg)


