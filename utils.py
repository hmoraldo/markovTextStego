import config
import math
import re

def wordListToText(strl):
	text = ""
	lastWord = config.startSymbol

	for word in strl:
		if lastWord == config.startSymbol and word != config.startSymbol:
			word = word[0].capitalize() + word[1:]

		if word != config.startSymbol and text != "":
			text = text + " "

		if not(text == "" and word == config.startSymbol):
			if word == config.startSymbol:
				text = text + "."
			else:
				text = text + word

		lastWord = word


	return text.rstrip("")

def textToWordList(text):
	words = re.findall(r"(?:\w[\w']*)|\.", text)

	def convert(w):
		if w == ".":
			return config.startSymbol
		else:
			return w.lower()

	words = [convert(w) for w in words]

	return words

def fromBinary(numberStr):
	return int(numberStr, 2)

def toBinary(number, minDigits):
	binary = bin(number)[2:]

	if len(binary) < minDigits:
		binary = "".join(["0" for x in range(minDigits - len(binary))]) + binary

	return binary

def binaryLowerThan(a, b):
	if len(a) != len(b):
		raise RuntimeError("can't compare two binary numbers of different size")
	else:
		return a < b

def binaryLowerEqualThan(a, b):
	return (a == b or binaryLowerThan(a, b))

"""
this function expands digitRanges to make them cover at least as many values as those in desiredRangeLen

- digitRanges: the actual range of digits
- rangeNums: the ranges already converted to integers
- desiredRangeLen: length goal; how many numbers must contain the range (eg. if this value is 256, the range needs 8 bits)
- maxDigits: max length allowed for the range, in bits
"""
def addDigitsToRange(digitRanges, rangeNums, desiredRangeLen, maxDigits):

	rangePossibleValues = 1 + rangeNums[1] - rangeNums[0]

	if desiredRangeLen <= rangePossibleValues:
		return digitRanges

	extraDigitsCount = int(math.ceil(math.log(1.0 * desiredRangeLen / rangePossibleValues, 2)))
	if len(digitRanges[0]) + extraDigitsCount > maxDigits:
		extraDigitsCount = maxDigits - len(digitRanges[0])

	digitRanges = (
		digitRanges[0] + "".join(["0" for x in range(extraDigitsCount)]),
		digitRanges[1] + "".join(["1" for x in range(extraDigitsCount)])
		)

	return digitRanges

"""
- digitRanges: a pair of binary numbers (strings), telling what the range to subdivide is
- wordProbabilities: a list of elements in this format: (word, (numerator, denominator))
- maxDigits: maximum digits possible in the digit ranges

returns a list of elements in this format: (word, range)
"""
def computeWordRanges(digitRanges, wordProbabilities, maxDigits):

	denominator = wordProbabilities[0][1][1]
	rangeNums = (fromBinary(digitRanges[0]), fromBinary(digitRanges[1]))

	# add more binary digits to range, if needed
	digitRanges = addDigitsToRange(digitRanges, rangeNums, denominator, maxDigits)

	rangeNums = (fromBinary(digitRanges[0]), fromBinary(digitRanges[1]))

	totalDigits = len(digitRanges[0])

	# typical double is 53 bits long; we limit range to some lower amount of bits
	if math.log(max(1, abs(rangeNums[1] - rangeNums[0])), 2) > 45:
		raise RuntimeError("error; range too long")

	# compute word ranges
	# first we compute float ranges, then we distribute the actual integer ranges as well as possible
	step = (1.0 * (rangeNums[1] - rangeNums[0])) / denominator

	base = rangeNums[0]
	start = 0

	wordRanges = []
	for wordP in wordProbabilities:
		end = start + wordP[1][0] * step

		wordRanges.append([wordP[0], [start, end]])
		start = end

	# the last element could be wrong because of float precision problems, force it
	# it is very important that we force this change in wordRanges and not in wordRanges2; otherwise the list could lose extra elements
	wordRanges[-1][1][1] = rangeNums[1] - base

	start = 0

	wordRanges2 = []
	for wordR in wordRanges:
		if wordR[1][1] >= start:
			wordR2 = [wordR[0], [start, int(math.floor(wordR[1][1]))]]
			wordR3 = [wordR2[0], [wordR2[1][0]+base, wordR2[1][1]+base]]
			wordRanges2.append(wordR3)

			start = wordR2[1][1] + 1

	# convert to binary before returning
	return [
		(wordP[0], (toBinary(wordP[1][0], totalDigits), toBinary(wordP[1][1], totalDigits)))
		for wordP in wordRanges2]

# given a range, removes its common digits (excepting the last one); doesn't modify the original range object
def removeCommonBitsInRange(rangeDigits):
	while len(rangeDigits[0]) > 1 and rangeDigits[0][0] == rangeDigits[1][0]:
		rangeDigits = (rangeDigits[0][1:], rangeDigits[1][1:])

	return rangeDigits

# converts an integer to a list of bytesCount bytes
def convertNumberToByteList(number, bytesCount):
	bytes = []

	for i in range(bytesCount):
		b = number % 256
		number = (number - b) / 256
		bytes.insert(0, b)

	bytes.reverse()
	return bytes

# converts an integer to a list of bytesCount bytes
def convertByteListToNumber(bytes):
	number = 0

	for b in reversed(bytes):
		number = number * 256 + b

	return number

# set all words to lower case, except the start symbol
def lowerWord(w):
	if w != config.startSymbol:
		return w.lower()
	else:
		return w


def lowerWordOrList(word):
	if type(word) is list:
		return [lowerWord(w) for w in word]
	elif type(word) is tuple:
		return tuple([lowerWord(w) for w in word])
	else:
		return lowerWord(word)

def listToTuple(t):
	if type(t) == list:
		return tuple(t)
	else:
		return t

def markovChainToDictionary(markovChain):
	dictionary = {}

	for wp in markovChain:
		dictionary[lowerWordOrList(listToTuple(wp[0]))] = wp

	return dictionary

if __name__ == '__main__':
	print "testing utils.py"
	print "TEST 1"
	print (computeWordRanges(["0", "1"], [("casa", (1, 4)), ("bosque", (2, 4)), ("selva", (1, 4))], 3) ==
		[('casa', ('00', '00')), ('bosque', ('01', '10')), ('selva', ('11', '11'))])
	print "TEST 2"
	print (computeWordRanges(["0", "1"], [("casa", (1, 5)), ("bosque", (2, 5)), ("selva", (2, 5))], 1) ==
		[('casa', ('0', '0')), ('selva', ('1', '1'))])
	print "TEST 3"
	print (computeWordRanges(["0", "0"], [("casa", (1, 5)), ("bosque", (2, 5)), ("selva", (2, 5))], 5) ==
		[('casa', ('0000', '0001')), ('bosque', ('0010', '0100')), ('selva', ('0101', '0111'))])
	print "TEST 4"
	print (computeWordRanges(["0", "0"], [("casa", (1, 5)), ("bosque", (2, 5)), ("selva", (2, 5))], 3) ==
		[('casa', ('000', '000')), ('bosque', ('001', '001')), ('selva', ('010', '011'))])
	print "TEST 5"
	print (computeWordRanges(["0", "1"], [("casa", (1, 3)), ("bosque", (1, 3)), ("selva", (1, 3))], 30) ==
		[('casa', ('00', '01')), ('bosque', ('10', '10')), ('selva', ('11', '11'))])
	print "TEST 6"
	bytes = convertNumberToByteList(342432, 3)
	print bytes == [160, 57, 5]
	print convertByteListToNumber(bytes) == 342432
	print "TEST 7"
	bytes = convertNumberToByteList(127, 1)
	print bytes == [127]
	print convertByteListToNumber(bytes) == 127
	print "TEST 8"
	bytes = convertNumberToByteList(123456, 3)
	print bytes == [64, 226, 1]
	print convertByteListToNumber(bytes) == 123456
	print "TEST 9"
	print wordListToText(["word1","word2","word3","<START>","word4","<START>","word5"]) == "Word1 word2 word3. Word4. Word5"
	print "TEST 10"
	print textToWordList("Word1 word2 word3. Word4. Word5") == ["word1","word2","word3","<START>","word4","<START>","word5"]
	print "done"


