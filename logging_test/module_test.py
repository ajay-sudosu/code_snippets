import logging

module_test_logger = logging.getLogger(__name__)
module_test_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s: Line no-%(lineno)d')

file_handler = logging.FileHandler('log/employee.log')
file_handler.setFormatter(formatter)
module_test_logger.addHandler(file_handler)

# logging.basicConfig(filename='log/employee.log', level=logging.DEBUG,
#                     format='%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s: Line no-%(lineno)d')

class Employee:
    def __init__(self, first, last):
        self.first = first
        self.last = last
        module_test_logger.info(f"Employee created {first} {last}")
        # logging.info(f"Employee created {first} {last}")


emp_1 = Employee('hello', 'singh')
emp_2 = Employee('test', 'world')
