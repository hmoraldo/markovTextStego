"functions in this file encode digits of fixed size into text; and decode them from text to digits"
import config
import utils
import bigBitField
import time

"""
encodes a single word

- bits: a bit field object with the data to encode
- bitsRange: the range to encode this from
- startWord: previous word encoded (either 1 or 2 words depending on wordsPerState)
- markovChainDict: dictionary with the chain to use to encode data

returns (word, newRange)
"""
def encodeBitsToWord(bitsField, bitsRange, startWord, markovChainDict):

	# get probabilities for the start word
	wordProbs = markovChainDict[utils.lowerWordOrList(startWord)][1]

	# get the range covered by every word
	wordRanges = utils.computeWordRanges(bitsRange, wordProbs, bitsField.totalFieldLen())

	# look for the right partition for the bits
	precision = len(wordRanges[0][1][0])
	bits = bitsField.getFirstNBits(precision)

	bestWord = filter(
		lambda wr:
			utils.binaryLowerEqualThan(wr[1][0], bits) and utils.binaryLowerEqualThan(bits, wr[1][1]),
		wordRanges)

	return bestWord[0]


"""
encodes all a bit field to a list of words, using a markov chain

- bitsField: a bit field object with the data to encode
- markovChain: chain to use to encode data
- startWord: if it is not the default, what was the previous word before this text

returns wordList
"""
def encodeBitsToWordList(bitsField, markovChain, startWord = config.startSymbol, wordsPerState = 1):

	bitsField = bitsField.copy()
	lastTime = time.time()
	secondsForStatusPrint = 20

	words = []
	nextRange = ["0", "1"]
	markovChainDict = utils.markovChainToDictionary(markovChain)

	while True:
		# encode to one word
		(word, nextRange) = encodeBitsToWord(bitsField, nextRange, startWord, markovChainDict)
		words.append(word)

		# compute previous word (or bigram) for next iteration
		if wordsPerState == 1:
			startWord = word
		elif wordsPerState == 2:
			if word == config.startSymbol:
				startWord = (config.startSymbol, config.startSymbol)
			else:
				startWord = (startWord[1], word)

		# optimization, remove start of range when it is identical in both sides
		nextRange2 = utils.removeCommonBitsInRange(nextRange)
		bitsField.popFirstNBits(len(nextRange[0])-len(nextRange2[0]))
		nextRange = nextRange2

		if time.time()-lastTime > secondsForStatusPrint:
			print " - remaining bits: " + repr(bitsField.totalFieldLen())
			lastTime = time.time()

		# we exit when our range describes only to our number
		if bitsField.totalFieldLen() == 0 or (bitsField.totalFieldLen() == 1 and nextRange[0][0] == nextRange[1][0]):
			break

	return words


if __name__ == '__main__':
	print "testing fixedSizeCode.py"

	testMarkov = config.testMarkov
	testMarkovDict = utils.markovChainToDictionary(testMarkov)

	testMarkov2 = config.testMarkov2
	testMarkovDict2 = utils.markovChainToDictionary(testMarkov2)

	# this is "01000110 01011010 11111111"
	testBitField = bigBitField.BigBitField([70, 90, 255])

	print "A:"
	print encodeBitsToWord(testBitField, ["0", "1"], config.startSymbol, testMarkovDict) == ('A', ('00', '01'))
	print "A2:"
	print encodeBitsToWord(testBitField, ["0", "1"], (config.startSymbol, config.startSymbol), testMarkovDict2) == ('A', ('00', '01'))
	print "B:"
	print encodeBitsToWord(testBitField, ["0", "1"], "A", testMarkovDict) == ('B', ('01', '01'))
	print "B2:"
	print encodeBitsToWord(testBitField, ["0", "1"], (config.startSymbol, "A"), testMarkovDict2) == ('B', ('01', '01'))
	print "C:"
	miniBF = bigBitField.BigBitField("0", False)
	print encodeBitsToWord(miniBF, ["0", "1"], "A", testMarkovDict) == ('A', ('0', '0'))
	print "C2:"
	print encodeBitsToWord(miniBF, ["0", "1"], (config.startSymbol, "A"), testMarkovDict2) == ('A', ('0', '0'))

	print "SIZE 1"
	print "testWordList 1:"
	miniBF = bigBitField.BigBitField("0", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A']
	print "testWordList 1b:"
	print encodeBitsToWordList(miniBF, testMarkov2, (config.startSymbol, config.startSymbol), 2) == ['A']
	print "testWordList 2:"
	miniBF = bigBitField.BigBitField("1", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['C']
	print "SIZE 2"
	print "testWordList 3:"
	miniBF = bigBitField.BigBitField("00", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'A']
	print "testWordList 4:"
	miniBF = bigBitField.BigBitField("01", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', '<START>']
	print "testWordList 5:"
	miniBF = bigBitField.BigBitField("10", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['B']
	print "testWordList 6:"
	miniBF = bigBitField.BigBitField("11", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['C']
	print "SIZE 3"
	print "testWordList 7:"
	miniBF = bigBitField.BigBitField("000", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'A']
	print "testWordList 8:"
	miniBF = bigBitField.BigBitField("001", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'B']
	print "testWordList 9:"
	miniBF = bigBitField.BigBitField("010", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'C']
	print "testWordList 10:"
	miniBF = bigBitField.BigBitField("011", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', '<START>']
	print "testWordList 11:"
	miniBF = bigBitField.BigBitField("100", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['B', 'A']
	print "testWordList 12:"
	miniBF = bigBitField.BigBitField("101", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['B', '<START>']
	print "testWordList 13:"
	miniBF = bigBitField.BigBitField("110", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['C', 'A']
	print "testWordList 14:"
	miniBF = bigBitField.BigBitField("111", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['C', '<START>']
	print "SIZE 4"
	print "testWordList 15:"
	miniBF = bigBitField.BigBitField("0000", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'A', 'A']
	print "testWordList 16:"
	miniBF = bigBitField.BigBitField("0001", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'A', '<START>']
	print "testWordList 16b:"
	miniBF = bigBitField.BigBitField("0001", False)
	print encodeBitsToWordList(miniBF, testMarkov2, (config.startSymbol, config.startSymbol), 2) == ['A', 'A', '<START>']
	print "testWordList 17:"
	miniBF = bigBitField.BigBitField(
		"0010101010000101010101110010101011011010101000111010101010010011101101010110101010101010001110101010", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['A', 'B', 'B', 'B', 'B', 'A', 'A', 'C', 'C', 'C', 'C', '<START>', 'B', 'B', 'B', 'B', 'B', 'C', '<START>', 'A', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C', 'C', 'B', 'A', '<START>', 'B', '<START>', 'A', 'C', 'C', '<START>', 'A', 'C', 'C', 'C', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C']
	print "testWordList 17b:"
	print encodeBitsToWordList(miniBF, testMarkov2, (config.startSymbol, config.startSymbol), 2) == ['A', 'B', 'B', 'B', 'B', 'A', 'A', 'C', 'C', 'C', 'C', '<START>', 'B', 'B', 'B', 'B', 'B', 'C', '<START>', 'A', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C', 'C', 'B', 'A', '<START>', 'B', '<START>', 'A', 'C', 'C', '<START>', 'A', 'C', 'C', 'C', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C']
	print "testWordList 18:"
	miniBF = bigBitField.BigBitField(
		"101011101011110101101011111010100101010100101111010111", False)
	print encodeBitsToWordList(miniBF, testMarkov) == ['B', 'C', '<START>', 'B', 'C', '<START>', 'C', 'B', 'B', 'C', 'C', '<START>', 'C', 'C', 'C', 'C', 'B', 'B', 'B', 'B', 'A', 'C', '<START>', 'C', 'B', 'B', '<START>']
	print "done"

