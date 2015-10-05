# Base class for roots of the complex transfer function (roots of numerator or denominator)

class Root:
    def __init__(self):
        raise NotImplementedError("cannot instantiate abstract class Root")

    def addToList(self):
        if (self.pair):
            self.putInSpecifiedList(self.position)
            self.putInSpecifiedList(self.position.conjugate())
        else:
            self.putInSpecifiedList(self.position)

    def putInSpecifiedList(self):
        raise NotImplementedError("cannot call abstract method putInSpecifiedList from Root class")

    def setPosition(self, position):
        self.position = position
        if (self.pair == False):
            self.position = self.position.real
        self.restrictPosition()

    def getPosition(self):
        return self.position

    def restrictPosition(self):
        raise NotImplementedError("cannot call abstract method restrictPosition from Root class")

# inheriting Zero class has its own list, not restricted within unit circle
# still need to make pair and position "private" variables, add getter/setter for pair

class Zero(Root):
    list = []
    minimumRadius = 0.2
    maximumRadius = 2.0

    def __init__(self, position):
        self.pair = False
        self.setPosition(position)

    def putInSpecifiedList(self, position):
        Zero.list.append(position)

    def restrictPosition(self):
        length = abs(self.position)
        if (length < Zero.minimumRadius):
            self.position *= Zero.minimumRadius / length
        if (length > Zero.maximumRadius):
            self.position *= Zero.maximumRadius / length

# inherting Pole class has its own list, must stay within unit circle

class Pole(Root):
    list = []
    minimumRadius = 0.2
    maximumRadius = 1.0

    def __init__(self, position):
        self.pair = False
        self.setPosition(position)

    def putInSpecifiedList(self, position):
        Pole.list.append(position)

    def restrictPosition(self):
        length = abs(self.position)
        if (length < Pole.minimumRadius):
            self.position *= Pole.minimumRadius / length
        if (length > Pole.maximumRadius):
            self.position *= Pole.maximumRadius / length
