class Payment:
    """
    Class should be open for extension and closed to modification.
    Achieved mostly using abstract method.
    """

    def process_payment(self):
        pass


class CreditCardPayment(Payment):
    def process_payment(self):
        # Implementation for credit card payments
        pass


class PayPalPayment(Payment):
    def process_payment(self):
        # Implementation for PayPal payments
        pass


class PaymentProcessor:
    def __init__(self, payment_method):
        self.payment_method = payment_method

    def process_payment(self):
        self.payment_method.process_payment()


# Usage
credit_card_payment = CreditCardPayment()
paypal_payment = PayPalPayment()

processor = PaymentProcessor(credit_card_payment)
processor.process_payment()

processor = PaymentProcessor(paypal_payment)
processor.process_payment()


###########################################################
# Class violation the OCP example                        #
###########################################################

class Payment:
    def process_payment(self):
        pass


class PaymentProcessor:
    """
    If we want to add support for PayPal payments, we would have to modify the PaymentProcessor class to check which
    payment method was being used.
    """
    def __init__(self, payment_method):
        if payment_method == 'credit_card':
            self.payment = CreditCardPayment()
        elif payment_method == 'paypal':
            self.payment = PayPalPayment()

    def process_payment(self):
        self.payment.process_payment()


# Usage
processor = PaymentProcessor('credit_card')
processor.process_payment()

processor = PaymentProcessor('paypal')
processor.process_payment()



