"defines a big bit field object"
import utils
import math

"""
a class for managing big amounts of bits (these bits are internally stored as bytes, except in the left and right extremes)
"""
class BigBitField:

	def __init__(self, data = None, dataIsBytes = True):
		if data is None:
			data = []

		self.lastBitsCache = ""

		if dataIsBytes:
			self.firstBitsCache = ""
			self.remainingBytes = data
		else:
			self.firstBitsCache = data
			self.remainingBytes = []


	def copy(self):
		bitField = BigBitField()
		bitField.firstBitsCache = self.firstBitsCache
		bitField.lastBitsCache = self.lastBitsCache
		bitField.remainingBytes = list(self.remainingBytes)
		return bitField

	"""
	internal; we store data as bytes and as a string with the explicit bits... this function extracts n bytes into the
	string, and converts them to ascii 1 and 0 that is easy to operate with
	"""
	def popBytesToBitsCache(self, bytesToPop):
		if len(self.remainingBytes) < bytesToPop:
			raise RuntimeError("not enough bytes for popToBits operation")

		for x in range(bytesToPop):
			byte = self.remainingBytes.pop(0)
			bits = utils.toBinary(byte, 8)
			self.firstBitsCache = self.firstBitsCache + bits

	def totalFieldLen(self):
		return len(self.firstBitsCache) + len(self.remainingBytes) * 8 + len(self.lastBitsCache)


	"internal: gets at least n bits extra ready in firstBitsCache"
	def getNBitsReady(self, bitsCount):
		if self.totalFieldLen() < bitsCount:
			raise RuntimeError("not enough bits for getNBitsReady")
		else:
			while len(self.firstBitsCache) < bitsCount:
				# push bytes to bits
				bytesToGet = int(math.ceil((bitsCount - len(self.firstBitsCache)) / 8.0))
				bytesToGet = min(len(self.remainingBytes), bytesToGet)
				self.popBytesToBitsCache(bytesToGet)

				# if no more bytes, move all bits from one extreme to the other
				# (even if this means getting more bits ready than what the user asked for)
				if self.remainingBytes == []:
					self.firstBitsCache = self.firstBitsCache + self.lastBitsCache
					self.lastBitsCache = ""

	"get n bits from the field, but don't change the field"
	def getFirstNBits(self, bitsCount):
		self.getNBitsReady(bitsCount)

		return self.firstBitsCache[0:bitsCount]

	"pop the first n bits from the field"
	def popFirstNBits(self, bitsCount):
		self.getNBitsReady(bitsCount)
		firstNBits = self.firstBitsCache[0:bitsCount]
		self.firstBitsCache = self.firstBitsCache[bitsCount:]

		return firstNBits

	"push a number of bits, as in a stack (from the top or first bits)"
	def pushNBits(self, bits):
		self.firstBitsCache = bits + self.firstBitsCache
		while len(self.firstBitsCache) >= 8:
			idx = len(self.firstBitsCache) - 8
			self.remainingBytes.insert(0, utils.fromBinary(self.firstBitsCache[idx:]))
			self.firstBitsCache = self.firstBitsCache[0:idx]

	"push a number of bits, as in a queue (from the bottom or last bits)"
	def pushQueueNBits(self, bits):
		self.lastBitsCache = self.lastBitsCache + bits
		while len(self.lastBitsCache) >= 8:
			idx = 8
			self.remainingBytes.append(utils.fromBinary(self.lastBitsCache[0:idx]))
			self.lastBitsCache = self.lastBitsCache[idx:]

	# returns all bytes if the data stored can be returned as bytes
	def getAllBytes(self):
		if self.firstBitsCache != "" or self.lastBitsCache != "":
			raise RuntimeError("can't getAllBytes from bitField; not all data stored in bytes now")
		else:
			return self.remainingBytes


if __name__ == '__main__':
	print "testing bigBitField.py"
	# this is "01000110 01011010 11111111"
	bits = BigBitField([70, 90, 255])
	print "A:"
	print bits.totalFieldLen() == 24
	print "B:"
	print bits.getFirstNBits(8) == "01000110"
	print "B2:"
	print bits.popFirstNBits(0) == ""
	print "B3:"
	print bits.getFirstNBits(0) == ""
	print "C:"
	print bits.popFirstNBits(3) == "010"
	print "D:"
	print bits.getFirstNBits(6) == "001100"
	print "E:"
	print bits.popFirstNBits(8) == "00110010"
	print "F:"
	print bits.totalFieldLen() == 13
	print "G:"
	print bits.getFirstNBits(6) == "110101"
	print "H:"
	print bits.popFirstNBits(4) == "1101"
	print "I:"
	print bits.popFirstNBits(7) == "0111111"
	print "J:"
	print bits.totalFieldLen() == 2
	print "K:"
	print bits.popFirstNBits(2) == "11"
	print "L:"
	print bits.totalFieldLen() == 0
	print "M:"
	bits.pushNBits("010")
	bits.pushNBits("1110111111")
	print bits.totalFieldLen() == 13
	print bits.firstBitsCache == "11101"
	print bits.popFirstNBits(13) == "1110111111010"
	print bits.totalFieldLen() == 0
	print "N:"
	bits.pushQueueNBits("11111")
	bits.pushQueueNBits("1010")
	bits.pushQueueNBits("001100")
	bits.pushQueueNBits("1100")
	bits.pushNBits("1100")
	bits.pushNBits("111111100111")
	# bits should be "111111100111 1100 11111 1010 001100 1100"
	print bits.totalFieldLen() == 35
	print bits.popFirstNBits(10) == "1111111001"
	print bits.popFirstNBits(4) == "1111"
	print bits.popFirstNBits(7) == "0011111"
	print bits.popFirstNBits(7) == "1010001"
	print bits.popFirstNBits(7) == "1001100"
	print "done"

