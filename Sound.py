import wave
#import pymedia.audio.sound as sound

class SoundInfo:
   # listing of common sampling rates in a wave file
    SampleRate8000Hz = 8000
    SampleRate11025Hz = 11025
    SampleRate16000Hz = 16000
    SampleRate22050Hz = 22050
    SampleRate32000Hz = 32000
    SampleRate44100Hz = 44100
    SampleRate48000Hz = 48000
    SampleRate88200Hz = 88200
    SampleRate96000Hz = 96000

   # listing of common bit depths in a wave file (in terms of byte depth)
    BitDepth8 = 1
    BitDepth16 = 2
    BitDepth24 = 3
    BitDepth32 = 4

    def __init__(self):
        self.sampleRate = SoundInfo.SampleRate44100Hz
        self.channelCount = 1
        self.sampleByteDepth = SoundInfo.BitDepth16

    def findByteRate(self):
        return (self.sampleRate * self.channelCount * self.sampleByteDepth)

    def findBitRate(self):
        return (8.0 * self.findByteRate())

    def findLengthInSeconds(self, sampleArray):
        return (1.0 * len(sampleArray) / self.sampleRate)

# private subroutine for extracting samples as floats from wave file byte data

def _convertByteDataToFloats(arrayOfBytes, bytesPerFloat):
   # create new array of floats of correct length
    sampleCount = len(arrayOfBytes) / bytesPerFloat
    sampleFloats = [0.0 for sampleIndex in range(0, sampleCount)]

   # for each sample, join its bytes into a single float
    for sampleIndex in range(0, sampleCount):
        for sampleByte in range(0, bytesPerFloat):
            byteIndex = bytesPerFloat * sampleIndex + bytesPerFloat - sampleByte - 1
            sampleByteAsFloat = float(ord(arrayOfBytes[byteIndex]))
            sampleFloats[sampleIndex] = 256.0 * sampleFloats[sampleIndex] + sampleByteAsFloat

   # normalize samples to range [0,1]
    normalizingFactor = 1.0 / (256.0 ** bytesPerFloat - 1.0)
    normalizedSampleFloats = [(sample * normalizingFactor) for sample in sampleFloats]

   # correct sample range to [-1,+1]
    for sampleIndex in range(0, sampleCount):
        normalizedSampleFloats[sampleIndex] *= 2.0
        if (bytesPerFloat == SoundInfo.BitDepth8):
            normalizedSampleFloats[sampleIndex] = 2.0 * normalizedSampleFloats[sampleIndex] - 1.0
        else:
            if normalizedSampleFloats[sampleIndex] > 1.0:
                normalizedSampleFloats[sampleIndex] -= 2.0

    return normalizedSampleFloats

# private subroutine for obtaining corresponding byte data of a sound

def _convertFloatsToByteData(arrayOfFloats, bytesPerFloat):
   # place samples back into range [0,1]
    renormalizedFloats = [sample for sample in arrayOfFloats]
    for sampleIndex in range(0, len(renormalizedFloats)):
        if (bytesPerFloat == SoundInfo.BitDepth8):
            renormalizedFloats[sampleIndex] = 0.5 * renormalizedFloats[sampleIndex] + 0.5
        else:
            if renormalizedFloats[sampleIndex] < 0.0:
                renormalizedFloats[sampleIndex] += 2.0
            renormalizedFloats[sampleIndex] *= 0.5

   # denormalized sound floats
    denormalizingFactor = 256.0 ** bytesPerFloat - 1.0
    denormalizedFloats = [(sample * denormalizingFactor) for sample in renormalizedFloats]

   # extract byte values from denormalized floats
    byteCount = len(arrayOfFloats) * bytesPerFloat
    finalBytes = bytearray(byteCount)
    for sampleIndex in range(0, len(arrayOfFloats)):
        value = denormalizedFloats[sampleIndex]
        for sampleByte in range(0, bytesPerFloat):
            byteIndex = bytesPerFloat * sampleIndex + sampleByte
            finalBytes[byteIndex] = int(value % 256)
            value = value // 256

   # convert bytearray back into immutable bytes
    return bytes(finalBytes)

# public subroutine for getting sound data from wave file

def loadSoundFromFile(fileName):
    loadedSoundInfo = SoundInfo()

    waveFile = wave.open(fileName, 'rb')
    loadedSoundInfo.sampleRate = waveFile.getframerate()
    loadedSoundInfo.channelCount = waveFile.getnchannels()
    loadedSoundInfo.sampleByteDepth = waveFile.getsampwidth()

    waveBytes = waveFile.readframes(waveFile.getnframes())
    waveFile.close()

    loadedSoundSamples = _convertByteDataToFloats(waveBytes, loadedSoundInfo.sampleByteDepth)

    return loadedSoundInfo, loadedSoundSamples

# public subroutine for writing a sound out to a wave file

def saveSoundToFile(soundToSaveInfo, soundSamples, fileName):
    waveFile = wave.open(fileName, 'wb')
    waveFile.setframerate(soundToSaveInfo.sampleRate)
    waveFile.setnchannels(soundToSaveInfo.channelCount)
    waveFile.setsampwidth(soundToSaveInfo.sampleByteDepth)

    waveBytes = _convertFloatsToByteData(soundSamples, soundToSaveInfo.sampleByteDepth)

    waveFile.writeframes(waveBytes)
    waveFile.close()

# public subroutine to return byte representation of sound (pymedia cannot be encapsulated here?)

def getWaveBytes(inputSoundInfo, soundSamples):
    return _convertFloatsToByteData(soundSamples, inputSoundInfo.sampleByteDepth)
