from abc import ABC, abstractmethod

###########################################
#    class showing ISP principle.         #
###########################################

class CallingDevice(ABC):
    @abstractmethod
    def make_calls(self):
        pass

class MessagingDevice(ABC):
    @abstractmethod
    def send_message(self):
        pass

class InternetDevice(ABC):
    @abstractmethod
    def internet(self):
        pass

class MobileCommunication(CallingDevice, MessagingDevice, InternetDevice):

    def make_calls(self):
        print("This device can make calls.")

    def send_message(self):
        print("This device can send msgs.")

    def internet(self):
        print("This device can browse internet.")


class LandLineCommunicaion(CallingDevice):
    def make_calls(self):
        print("This device can make calls.")

mobile = MobileCommunication()
mobile.internet()

landline = LandLineCommunicaion()
landline.make_calls()


###########################################
#     class violating ISP principle.      #
###########################################

# class CommunicationDevice(ABC):
#     """
#         Software modules or class should have a specific interface that exposes only the method and
#         properties that are relevant to its clients and not more.
#     """
#
#     @abstractmethod
#     def make_calls(self):
#         pass
#
#     def send_msg(self):
#         pass
#
#     def internet(self):
#         pass
#
#
# class MobileCommunication(CommunicationDevice):
#     def make_calls(self):
#         print("This device can make calls.")
#
#
#     def send_msg(self):
#         print("This device can send msgs.")
#
#     def internet(self):
#         print("This device can browse internet.")
#
#
# class LandLineCommunicaiton(CommunicationDevice):
#     def make_calls(self):
#         print("This device can make calls.")
#
#     def send_msg(self):
#         raise "Sorry this device cannnot perform send messages."
#
#     def internet(self):
#         raise "This device cannot browse internet."
#
#
# mobile = MobileCommunication()
# mobile.internet()
#
# landline = LandLineCommunicaiton()
# landline.make_calls()
# landline.internet()
