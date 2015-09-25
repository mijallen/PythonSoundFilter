def _generateCoefficients(rootList):
    coefficientList = [complex(0.0) for coefficientIndex in range(0, len(rootList) + 1)]
    coefficientList[0] = complex(1.0)

    for coefficientIndex in range(0, len(rootList)):
        for rippleIndex in range(coefficientIndex + 1, 0, -1):
            coefficientList[rippleIndex] += coefficientList[rippleIndex-1] * -rootList[coefficientIndex]

    return coefficientList

class Filter:
    def __init__(self, zeroList, poleList):
        self.zeroCoefficients = _generateCoefficients(zeroList)
        self.poleCoefficients = _generateCoefficients(poleList)

        self.scaleFactor = 0.0
        for coefficient in self.zeroCoefficients: self.scaleFactor += abs(coefficient)
        for coefficient in self.poleCoefficients: self.scaleFactor += abs(coefficient)
        self.scaleFactor = 1.0 / (self.scaleFactor - 1.0)

        self.previousInputs = [0.0 for zero in zeroList]
        self.previousOutputs = [0.0 for pole in poleList]

   # returns modified copy of dataStream, original unmodified
   # filter's previousInputs and previousOutputs will be modified
    def filterStream(self, dataStream):
        outputStream = [sample for sample in dataStream]

        for sampleIndex in range(0, len(outputStream)):
            currentInput = outputStream[sampleIndex]

            for coefficientIndex in range(1, len(self.zeroCoefficients)):
                sample = self.previousInputs[coefficientIndex-1]
                sample *= +self.zeroCoefficients[coefficientIndex].real
                outputStream[sampleIndex] += sample
            for coefficientIndex in range(1, len(self.poleCoefficients)):
                sample = self.previousOutputs[coefficientIndex-1]
                sample *= -self.poleCoefficients[coefficientIndex].real
                outputStream[sampleIndex] += sample

            outputStream[sampleIndex] *= self.scaleFactor

            for inputIndex in range(len(self.previousInputs)-1, 0, -1):
                self.previousInputs[inputIndex] = self.previousInputs[inputIndex-1]
            if (len(self.previousInputs) > 0):
                self.previousInputs[0] = currentInput

            for outputIndex in range(len(self.previousOutputs)-1, 0, -1):
                self.previousOutputs[outputIndex] = self.previousOutputs[outputIndex-1]
            if (len(self.previousOutputs) > 0):
                self.previousOutputs[0] = outputStream[sampleIndex]

        return outputStream

    def clearMemory(self):
        for inputIndex in range(0, len(self.previousInputs)):
            self.previousInputs[inputIndex] = 0.0

        for outputIndex in range(0, len(self.previousOutputs)):
            self.previousOutputs[outputIndex] = 0.0
