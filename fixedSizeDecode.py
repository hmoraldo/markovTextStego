"functions in this file decode text to digits"
import config
import utils
import bigBitField
import time

"""
decodes a single word to digits

- word
- previousWord
- markovChainDict: dictionary with the chain to use to encode data
- maxDigits
- bitsRange: the range to encode this from

returns newRange
"""
def decodeWordToBitsRange(word, previousWord, markovChainDict, maxDigits, bitsRange):

	# get probabilities for the start word
	wordProbs = markovChainDict[utils.lowerWordOrList(previousWord)][1]

	# get the range covered by every word
	wordRanges = utils.computeWordRanges(bitsRange, wordProbs, maxDigits)

	bestRange = filter(lambda wr: utils.lowerWord(wr[0]) == utils.lowerWord(word), wordRanges)

	return bestRange[0][1]

"""
decode a list of words, converting it to a number of maxDigits binary digits

- words: list of words to decode
- maxDigits: how many binary digits the number to decode to has
- markovChain: markov chain to use
- previousWord: if this is not the default, another word where to start from

returns a pair: (decoded number, how many words were actually used from the list)
"""
def decodeWordListToBits(words, maxDigits, markovChain, previousWord = config.startSymbol, wordsPerState = 1):

	bitsRange = ["0", "1"]
	bitsField = bigBitField.BigBitField()
	wordsUsed = 0
	markovChainDict = utils.markovChainToDictionary(markovChain)
	lastTime = time.time()
	secondsForStatusPrint = 20

	for word in words:
		bitsRange = decodeWordToBitsRange(word, previousWord, markovChainDict, maxDigits - bitsField.totalFieldLen(), bitsRange)
		wordsUsed = wordsUsed + 1

		# compute previous word (or bigram) for next iteration
		if wordsPerState == 1:
			previousWord = word
		elif wordsPerState == 2:
			if word == config.startSymbol:
				previousWord = (config.startSymbol, config.startSymbol)
			else:
				previousWord = (previousWord[1], word)


		# simplify range, remove bits and add them to the field
		bitsRange2 = utils.removeCommonBitsInRange(bitsRange)
		bitsRemovedLen = len(bitsRange[0]) - len(bitsRange2[0])
		if bitsRemovedLen + bitsField.totalFieldLen() > maxDigits:
			bitsRemovedLen = maxDigits - bitsField.totalFieldLen()
		bitsField.pushQueueNBits(bitsRange[0][0:bitsRemovedLen])
		bitsRange = bitsRange2

		if time.time()-lastTime > secondsForStatusPrint:
			print " - decoded bits so far: " + repr(bitsField.totalFieldLen())
			lastTime = time.time()

		# we exit when our range describes only one number
		if bitsField.totalFieldLen() == maxDigits:
			break
		if bitsField.totalFieldLen() == maxDigits - 1 and bitsRange[0][0] == bitsRange[1][0]:
			bitsField.pushQueueNBits(bitsRange[0][0])
			break

	return (bitsField, wordsUsed)


if __name__ == '__main__':
	print "testing fixedSizeDecode.py"

	testMarkov = config.testMarkov
	testMarkovDict = utils.markovChainToDictionary(testMarkov)

	testMarkov2 = config.testMarkov2
	testMarkovDict2 = utils.markovChainToDictionary(testMarkov2)

	print "A:"
	print decodeWordToBitsRange("A", config.startSymbol, testMarkovDict, 1, ["0", "1"]) == ('0', '0')
	print "A2:"
	print decodeWordToBitsRange("A", (config.startSymbol, config.startSymbol), testMarkovDict2, 1, ["0", "1"]) == ('0', '0')
	print "B:"
	print decodeWordToBitsRange("A", config.startSymbol, testMarkovDict, 3, ["0", "1"]) == ('00', '01')
	print "B2:"
	print decodeWordToBitsRange("A", (config.startSymbol, config.startSymbol), testMarkovDict2, 3, ["0", "1"]) == ('00', '01')
	print "===="
	print "C:"
	val = decodeWordListToBits(["A"], 1, testMarkov)
	print val[0].totalFieldLen() == 1
	print val[0].popFirstNBits(1) == "0"
	print val[1] == 1
	print "D:"
	val = decodeWordListToBits(['A', 'A', '<START>'], 4, testMarkov)
	print val[0].totalFieldLen() == 4
	print val[0].popFirstNBits(4) == "0001"
	print val[1] == 3
	print "D2:"
	val = decodeWordListToBits(['A', 'A', '<START>'], 4, testMarkov2, (config.startSymbol, config.startSymbol), 2)
	print val[0].totalFieldLen() == 4
	print val[0].popFirstNBits(4) == "0001"
	print val[1] == 3
	print "E:"
	val = decodeWordListToBits(['A', 'A', 'A'], 4, testMarkov)
	print val[0].totalFieldLen() == 4
	print val[0].popFirstNBits(4) == "0000"
	print val[1] == 3
	print "F:"
	val = decodeWordListToBits(['C', 'A'], 3, testMarkov)
	print val[0].totalFieldLen() == 3
	print val[0].popFirstNBits(3) == "110"
	print val[1] == 2
	print "G:"
	val = decodeWordListToBits(['A', 'B', 'B', 'B', 'B', 'A', 'A', 'C', 'C', 'C', 'C', '<START>', 'B', 'B', 'B', 'B', 'B', 'C', '<START>', 'A', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C', 'C', 'B', 'A', '<START>', 'B', '<START>', 'A', 'C', 'C', '<START>', 'A', 'C', 'C', 'C', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C'], 100, testMarkov)
	print val[0].totalFieldLen() == 100
	print val[0].popFirstNBits(100) == "0010101010000101010101110010101011011010101000111010101010010011101101010110101010101010001110101010"
	print val[1] == 52
	print "H:"
	# like G, but adding more words, to see how it detects where to finish
	val = decodeWordListToBits(['A', 'B', 'B', 'B', 'B', 'A', 'A', 'C', 'C', 'C', 'C', '<START>', 'B', 'B', 'B', 'B', 'B', 'C', '<START>', 'A', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C', 'C', 'B', 'A', '<START>', 'B', '<START>', 'A', 'C', 'C', '<START>', 'A', 'C', 'C', 'C', 'C', 'C', 'C', 'A', '<START>', 'B', 'C', 'C', 'C', 'A', 'A', 'B', 'A'], 100, testMarkov)
	print val[0].totalFieldLen() == 100
	print val[0].popFirstNBits(100) == "0010101010000101010101110010101011011010101000111010101010010011101101010110101010101010001110101010"
	print val[1] == 52
	print "I:"
	val = decodeWordListToBits(['B', 'C', '<START>', 'B', 'C', '<START>', 'C', 'B', 'B', 'C', 'C', '<START>', 'C', 'C', 'C', 'C', 'B', 'B', 'B', 'B', 'A', 'C', '<START>', 'C', 'B', 'B', '<START>'], 54, testMarkov)
	print val[0].totalFieldLen() == 54
	print val[0].popFirstNBits(54) == "101011101011110101101011111010100101010100101111010111"
	print val[1] == 27
	print "J:"
	# like I, but adding more words, to see how it detects where to finish
	val = decodeWordListToBits(['B', 'C', '<START>', 'B', 'C', '<START>', 'C', 'B', 'B', 'C', 'C', '<START>', 'C', 'C', 'C', 'C', 'B', 'B', 'B', 'B', 'A', 'C', '<START>', 'C', 'B', 'B', '<START>', 'B', 'C', '<START>', 'C', 'B', 'B', 'C', 'C'], 54, testMarkov)
	print val[0].totalFieldLen() == 54
	print val[0].popFirstNBits(54) == "101011101011110101101011111010100101010100101111010111"
	print val[1] == 27
	print "J2:"
	# like I, but adding more words, to see how it detects where to finish
	val = decodeWordListToBits(['B', 'C', '<START>', 'B', 'C', '<START>', 'C', 'B', 'B', 'C', 'C', '<START>', 'C', 'C', 'C', 'C', 'B', 'B', 'B', 'B', 'A', 'C', '<START>', 'C', 'B', 'B', '<START>', 'B', 'C', '<START>', 'C', 'B', 'B', 'C', 'C'], 54,
	testMarkov2, (config.startSymbol, config.startSymbol), 2)
	print val[0].totalFieldLen() == 54
	print val[0].popFirstNBits(54) == "101011101011110101101011111010100101010100101111010111"
	print val[1] == 27

	print "done"

