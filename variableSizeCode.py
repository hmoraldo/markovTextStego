"encode and decode to and from variable size"
import config
import utils
import bigBitField
import fixedSizeCode
import fixedSizeDecode
import json
import time

"""
encodes variable sized data to text

- data: data to be encoded (a list of integers, every one is a byte)
- bitsForSize: how many bits will be used to encode the size
- markovChain: markov chainto use

returns the encoded text
"""
def encodeDataToWordList(data, bytesForSize, markovChain, wordsPerState = 1):

	# encode the data length first
	lenData = utils.convertNumberToByteList(len(data), bytesForSize)
	bitsField = bigBitField.BigBitField(lenData)

	if wordsPerState == 1:
		lastWord = config.startSymbol
	elif wordsPerState == 2:
		lastWord = (config.startSymbol, config.startSymbol)

	lenDataCode = fixedSizeCode.encodeBitsToWordList(bitsField, markovChain, lastWord, wordsPerState)

	# compute last word (or bigram)
	if wordsPerState == 1:
		lastWord = lenDataCode[-1]
	elif wordsPerState == 2:
		if len(lenDataCode) <= 1:
			lastWord = (config.startSymbol, lenDataCode[-1])
		else:
			lastWord = (lenDataCode[-2], lenDataCode[-1])

		if lastWord[1] == config.startSymbol:
			lastWord = (config.startSymbol, config.startSymbol)

	# encode the actual message
	bitsField = bigBitField.BigBitField(data)
	mainDataCode = fixedSizeCode.encodeBitsToWordList(bitsField, markovChain, lastWord, wordsPerState)

	return lenDataCode + mainDataCode

"""
decodes a text to data (variable sized data)

- wordList: encoded data in a text
- bitsForSize: how many bits will be used to encode the size
- markovChain: markov chainto use

returns the decoded data (in a bigBitField object)
"""
def decodeWordListToData(wordList, bytesForSize, markovChain, wordsPerState = 1):

	if wordsPerState == 1:
		lastWord = config.startSymbol
	elif wordsPerState == 2:
		lastWord = (config.startSymbol, config.startSymbol)

	# decode the message length
	(lenRawData, wordsUsed) = fixedSizeDecode.decodeWordListToBits(wordList, bytesForSize * 8, markovChain, lastWord, wordsPerState)
	lenRawData = lenRawData.getAllBytes()
	lenData = utils.convertByteListToNumber(lenRawData)

	# compute last word (or bigram)
	if wordsPerState == 1:
		lastWord = wordList[wordsUsed - 1]
	elif wordsPerState == 2:
		if wordsUsed == 1:
			lastWord = (config.startSymbol, wordList[wordsUsed - 1])
		elif wordsUsed == 0:
			raise RuntimeError("only 0 words used in decode word list to data")
		else:
			lastWord = (wordList[wordsUsed - 2], wordList[wordsUsed - 1])

		if lastWord[1] == config.startSymbol:
			lastWord = (config.startSymbol, config.startSymbol)

	# decode the actual message
	wordList = wordList[wordsUsed:]
	(decodedData, wordsUsed) = fixedSizeDecode.decodeWordListToBits(wordList, lenData * 8, markovChain, lastWord, wordsPerState)

	return decodedData


# given 2 input files, encode and save to the output file
def encodeDataFromFile(inputFile, outputFile, markovInputFile, textFileFormat, wordsPerState = 1):
	initTime = time.time()

	f = open(markovInputFile, 'r')
	jsonData = f.read()
	f.close()
	markovData = json.JSONDecoder().decode(jsonData)

	if (wordsPerState == 1 and type(markovData[0][0]) != str) or (wordsPerState == 2 and type(markovData[0][0]) != list):
		raise RuntimeError("error; markov chain structure doesn't match wordsPerState value")

	inputData = []
	f = open(inputFile, 'rb')
	char = None
	while char != "":
		char = f.read(1)
		if char != "": inputData.append(ord(char))
	f.close()

	encodedData = encodeDataToWordList(inputData, 4, markovData, wordsPerState)

	# save
	if textFileFormat:
		outputData = utils.wordListToText(encodedData)
	else:
		outputData = json.JSONEncoder().encode(encodedData)

	f = open(outputFile, 'w')
	f.write(outputData)
	f.close()

	print "wrote " + repr(len(inputData) * 8) + " bits"
	print "elapsed time: " + repr(time.time() - initTime) + " seconds"

# given 2 input files, decode and save to the output file
def decodeDataFromFile(inputFile, outputFile, markovInputFile, textFileFormat, wordsPerState = 1):
	initTime = time.time()

	f = open(markovInputFile, 'r')
	jsonData = f.read()
	f.close()
	markovData = json.JSONDecoder().decode(jsonData)

	if (wordsPerState == 1 and type(markovData[0][0]) != str) or (wordsPerState == 2 and type(markovData[0][0]) != list):
		raise RuntimeError("error; markov chain structure doesn't match wordsPerState value")

	f = open(inputFile, 'r')
	inputData = f.read()
	f.close()
	if textFileFormat:
		inputData = utils.textToWordList(inputData)
	else:
		inputData = json.JSONDecoder().decode(inputData)

	decodedData = decodeWordListToData(inputData, 4, markovData, wordsPerState)
	print "read " + repr(decodedData.totalFieldLen()) + " bits"
	decodedData = decodedData.getAllBytes()

	# save
	f = open(outputFile, 'wb')
	for b in decodedData:
		f.write(chr(b))
	f.close()

	print "elapsed time: " + repr(time.time() - initTime) + " seconds"


if __name__ == '__main__':
	print "testing variableSizeCode.py"
	print "A:"
	testMarkov = config.testMarkov
	data = [70, 90, 255, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 22, 211, 32, 89, 32, 89, 32, 89, 90,221, 111, 231, 89, 3, 3, 2, 1, 34, 55, 255, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 22, 211, 32, 89, 32, 89, 32, 89, 90,221, 111, 231, 89, 3, 3, 2, 1, 34, 55, 255, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 22, 211, 32, 89, 32, 89, 32, 89, 90,221, 111, 231, 89, 3, 3, 2, 1, 34, 55]
	code = encodeDataToWordList(data, 1, testMarkov)
	data2field = decodeWordListToData(code, 1, testMarkov)
	print data2field.totalFieldLen() == 125 * 8
	print code == ['A', '<START>', 'C', 'C', '<START>', 'A', 'C', 'A', '<START>', 'A', 'B', 'B', 'C', 'C', '<START>', 'C', '<START>', 'C', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', 'C', '<START>', 'A', 'C', 'B', 'C', 'B', 'A', 'A', 'A', 'C', '<START>', 'A', 'B', 'A', 'C', 'A', 'A', 'B', 'B', 'C', 'B', 'A', 'C', 'A', 'A', 'B', 'B', 'C', 'B', 'B', 'B', 'C', 'C', '<START>', 'A', '<START>', 'B', 'C', '<START>', 'A', '<START>', 'C', '<START>', 'B', 'B', '<START>', 'A', 'C', '<START>', 'A', 'B', 'A', 'A', 'A', '<START>', 'A', 'A', 'A', 'B', 'C', 'A', 'A', 'B', 'A', 'A', 'A', 'A', 'C', 'B', 'A', 'B', 'A', 'B', 'C', '<START>', 'C', '<START>', 'C', '<START>', 'B', 'A', 'C', '<START>', 'B', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', 'C', '<START>', 'A', 'C', 'B', 'C', 'B', 'A', 'A', 'A', 'C', '<START>', 'A', 'B', 'A', 'C', 'A', 'A', 'B', 'B', 'C', 'B', 'A', 'C', 'A', 'A', 'B', 'B', 'C', 'B', 'B', 'B', 'C', 'C', '<START>', 'A', '<START>', 'B', 'C', '<START>', 'A', '<START>', 'C', '<START>', 'B', 'B', '<START>', 'A', 'C', '<START>', 'A', 'B', 'A', 'A', 'A', '<START>', 'A', 'A', 'A', 'B', 'C', 'A', 'A', 'B', 'A', 'A', 'A', 'A', 'C', 'B', 'A', 'B', 'A', 'B', 'C', '<START>', 'C', '<START>', 'C', '<START>', 'B', 'A', 'C', '<START>', 'B', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', '<START>', 'A', '<START>', 'C', 'B', 'B', '<START>', 'A', 'C', 'A', 'A', 'B', 'B', 'C', '<START>', 'A', 'C', 'B', 'C', 'B', 'A', 'A', 'A', 'C', '<START>', 'A', 'B', 'A', 'C', 'A', 'A', 'B', 'B', 'C', 'B', 'A', 'C', 'A', 'A', 'B', 'B', 'C', 'B', 'B', 'B', 'C', 'C', '<START>', 'A', '<START>', 'B', 'C', '<START>', 'A', '<START>', 'C', '<START>', 'B', 'B', '<START>', 'A', 'C', '<START>', 'A', 'B', 'A', 'A', 'A', '<START>', 'A', 'A', 'A', 'B', 'C', 'A', 'A', 'B', 'A', 'A', 'A', 'A', 'C', 'B', 'A', 'B', 'A', 'B', 'C', '<START>', 'C']
	print len(code) == 537
	print data2field.getAllBytes() == data


	print "B:"
	data = [70, 90, 255, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 22, 211, 32, 89, 32, 89, 32, 89, 90,221, 111, 231, 89, 3, 3, 2, 1, 34, 55, 255, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 22, 211, 32, 89, 32, 89, 32, 89, 90,221, 111, 231, 89, 3, 3, 2, 1, 34, 55, 255, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 23, 122, 232, 22, 211, 32, 89, 32, 89, 32, 89, 90,221, 111, 231, 89, 3, 3, 2, 1, 34, 55]
	f = open("data/markovChain.json", 'r')
	jsonData = f.read()
	f.close()
	bigMarkov = json.JSONDecoder().decode(jsonData)

	code = encodeDataToWordList(data, 1, bigMarkov)
	data2field = decodeWordListToData(code, 1, bigMarkov)
	print data2field.totalFieldLen() == len(data) * 8
	print code == [u'running', u'away', u'from', u'my', u'friend', u'as', u'before', u'us', u'<START>', u'the', u'French', u'followed', u'behind', u'<START>', u'and', u'to', u'conclude', u'will', u'not', u'only', u'a', u'printed', u'matter', u'of', u'freedom', u'and', u'solemn', u'hymn', u'<START>', u'and', u'the', u'luring', u'Napoleon', u'<START>', u'middle', u'of', u'sick', u'father', u'<START>', u'replied', u'Nicholas', u'ran', u'into', u'tears', u'<START>', u'I', u"don't", u'know', u'they', u'describe', u'an', u'active', u'and', u'second', u'autocrat', u'<START>', u'though', u'she', u'needed', u'he', u'ought', u'not', u'worth', u'while', u'still', u'stouter', u'<START>', u'rapidly', u'<START>', u'he', u'excused', u'himself', u'to', u'escape', u'as', u'heralds', u'of', u'so', u'God', u'<START>', u'and', u'ingratiating', u'the', u'generals', u'<START>', u'and', u'having', u'made', u'a', u'moment', u'he', u'was', u'going', u'to', u'go', u'after', u'by', u'any', u'orders', u'Or', u'the', u'middle', u'of', u'it', u'anticipated', u'his', u'wife', u'is', u'all', u'this', u'excess', u'of', u'that', u'he', u'reached', u'the', u'history', u'remains', u'of', u'the', u'room', u'next', u'day', u'<START>', u'being', u'said', u'Princess', u'Mary', u'also', u'by', u'the', u'dressing', u'jacket', u'laced', u'with', u'greedy', u'expectation', u'<START>', u'the', u'end', u'to', u'wash', u'That', u'the', u'immediate', u'answer', u'<START>', u'un', u'moment', u'<START>', u'and', u'zeal', u'than', u'all', u'<START>', u'How', u'strange', u'<START>', u'though', u'what', u'might', u'endanger', u'the', u'snowflakes', u'fluttering', u'dressing', u'gown', u'of', u'the', u'action', u'to', u'pardon']
	print len(code) == 172
	print data2field.getAllBytes() == data
	print "done"

