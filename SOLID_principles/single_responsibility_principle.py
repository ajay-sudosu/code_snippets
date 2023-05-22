class User:
    """
    Class should do only one thing and it should have only single reason to change.
    Class must only be changed when its primary responsibiliy needs to be changed.
    Class should not be changed for adding additional functionality.
    """

    def __init__(self, username, email):
        self.username = username
        self.email = email


    def get_username(self):
        return self.username

    def get_email(self):
        return self.email


class RegisterUser:

    def add_user(self, username, email):
        user = User(username, email)
        self.save_user(user)
        self.users.append(user)

    def save_user(self, user):
        print(f"This user is saved {user.username} and {user.email}")

u = UserManager()
print(u.add_user(username="ajay", email="023helloi@gmail.com"))
print([name.username for name in u.users])


###########################################################
# Class violation the SLP example                        #
###########################################################

class Employee:
    def __init__(self, name, address, salary):
        self.name = name
        self.address = address
        self.salary = salary

    def calculate_payroll(self):
        # Calculate the payroll for the employee
        payroll = self.salary * 0.9

        # Print the payroll for the employee
        print(f"Payroll for {self.name} is {payroll}")


###########################################################
# Correcting the above violation                          #
###########################################################

#  Corrected the two different responsibility in a single class into a 2 different classes that handles the User in one
# class and payroll in another class.

class CorrectEmployee:
    def __init__(self, name, address, salary):
        self.name = name
        self.address = address
        self.salary = salary


class PayrollCalculator:
    def calculate_payroll(self, employee):
        # Calculate the payroll for the employee
        payroll = employee.salary * 0.9

        # Return the payroll for the employee
        return payroll
