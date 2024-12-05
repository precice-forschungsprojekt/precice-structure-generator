import logging

class UT_PCErrorLogging(object):
    """
    This is the main class to record all the loggings during the run of the program
    """
    def __init__(self):
        """ empty Ctor """
        pass

    def rep_error(self, msg: str):
        #logging.error(msg)
        logging.info(msg)
        pass

    def rep_info(self,msg: str):
        logging.info(msg)
        pass