import sys
from threading import Thread
import config

# =======================================================================================================================
#
#   Class created for (simple) multithreading
#
# =======================================================================================================================

class AWSThread(Thread):

    """
        Class used for threading inventories. It's a very simple class where a thread is created (__init__) with the function
        to call (with its arguments), and instead of executing all inventories in sequence, we create a thread for each of them.

        Inventories are the kind of tasks you can easily parallelize!

    """    

    def __init__(self, aws_service, function_name, arg):

        """
            Thread Class initialization.  

            :param aws_service: name of AWS service
            :type aws_service: string
            :param function_name: function to call (AWS SDK)
            :type function_name: function object
            :param arg: arguments for function name
            :type arg: any kind

            :return: nothing
        """ 

        Thread.__init__(self)
        self.function_name = function_name
        self.arg = arg
        self.aws_service = aws_service


    def run(self):
        
        """
            Code to execute => the AWS function, in its own thread
        """
        
        config.global_inventory[self.aws_service] = self.function_name(self.arg)


