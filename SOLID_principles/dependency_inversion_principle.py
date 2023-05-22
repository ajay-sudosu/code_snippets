from abc import ABC, abstractmethod

class Switchable(ABC):
    """
    High-level modules should not depend on low-level modules, but both should depend on abstractions.
    """
    @abstractmethod
    def turn_on(self, amount):
        pass

    @abstractmethod
    def turn_off(self, amount):
        pass


class LightBulb(Switchable):
    def turn_on(self):
        print("Bulb is on")


    def turn_off(self):
        print("Bulb is off")


class PowerSwitch:
    def __init__(self, switch: Switchable):
        self.switch = switch
        self.on = False

    def press(self):
        if self.on:
            self.switch.turn_off()

        else:
            self.switch.turn_on()
            self.on = True


surya_bulb = LightBulb()
switch = PowerSwitch(surya_bulb)
switch.press()
switch.press()


class Fan(Switchable):
    def turn_off(self,):
        print("Fan is off")

    def turn_on(self,):
        print("Fan is on")

fan = Fan()
switch = PowerSwitch(fan)
switch.press()
switch.press()


#########################################
#    class that violates the DIP        #
#########################################

class LightBulb:

    def turn_on(self):
        print("Bulb is on.")

    def turn_off(self):
        print("bulb is off")


class PowerSwitch:

    def __init__(self, lightbulb: LightBulb):
        self.lightbulb = lightbulb
        self.on = False

    def press(self):
        if self.on:
            self.lightbulb.turn_off()

        else:
            self.lightbulb.turn_on()
            self.on = True


bulb = LightBulb()
switch = PowerSwitch(bulb)
switch.press()

