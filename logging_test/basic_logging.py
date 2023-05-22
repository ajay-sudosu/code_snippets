import logging
import time
import module_test
import os

basic_logger = logging.getLogger(__name__)
basic_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s: Line no-%(lineno)d')



file_handler = logging.FileHandler('log/basic_logging.log')
file_handler.setFormatter(formatter)
basic_logger.addHandler(file_handler)


# logging.basicConfig(filename='log/function.log', level=logging.DEBUG,
#                     format='%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s: Line no-%(lineno)d')

def adding(a, b):
    basic_logger.debug(f'the sum is {a+b}')
    return a+b

adding(2, 4)
