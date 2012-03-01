"encode and decode to and from variable size"
import config
import utils
import bigBitField
import fixedSizeCode
import fixedSizeDecode
import json

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
	f = open(markovInputFile, 'r')
	jsonData = f.read()
	f.close()
	markovData = json.JSONDecoder().decode(jsonData)

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

# given 2 input files, decode and save to the output file
def decodeDataFromFile(inputFile, outputFile, markovInputFile, textFileFormat, wordsPerState = 1):
	f = open(markovInputFile, 'r')
	jsonData = f.read()
	f.close()
	markovData = json.JSONDecoder().decode(jsonData)

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
	f = open("data/binaryMarkovChain.json", 'r')
	jsonData = f.read()
	f.close()
	bigMarkov = json.JSONDecoder().decode(jsonData)

	code = encodeDataToWordList(data, 1, bigMarkov)
	data2field = decodeWordListToData(code, 1, bigMarkov)
	print data2field.totalFieldLen() == len(data) * 8
	print code == [u'These', u'people', u'at', u'Ulm', u'and', u'you', u'he', u'knew', u'at', u'dinner', u'he', u'had', u'caught', u'it', u'with', u'Dolokhov', u'comes', u'of', u'hunger', u'and', u'the', u'antagonists', u'stood', u'with', u'Sonya', u'<START>', u'what', u'to', u'avoid', u'any', u'moment', u'of', u'how', u'good', u'thing', u'he', u'spoke', u'as', u'well', u'as', u'it', u'there', u'were', u'ill', u'will', u'fight', u'could', u'see', u'whether', u'they', u'<START>', u'experienced', u'almost', u'all', u'his', u'future', u'<START>', u'and', u'reckoned', u'up', u'again', u'I', u"don't", u'you', u'have', u'this', u'<START>', u'and', u'to', u'have', u'doubted', u'it', u'is', u'suffering', u'physically', u'calm', u'I', u'think', u'of', u'the', u'same', u'kind', u'man', u"who's", u'there', u'<START>', u'Pierre', u'than', u'in', u'a', u"man's", u'place', u'and', u'went', u'into', u'the', u'guns', u'of', u'the', u'story', u'What', u'is', u'cut', u'<START>', u'and', u'even', u'if', u'you', u'said', u'Natasha', u'rested', u'on', u'with', u'apparent', u'reason', u'to', u'him', u'away', u'<START>', u'the', u'army', u'as', u'a', u'sorrowful', u'gesture', u'<START>', u'and', u'foreign', u'enemies', u'<START>', u'the', u'hussar', u'came', u'into', u'Prince', u'Bagration', u'bowed', u'his', u'sword', u'<START>', u'not', u'give', u'way', u'in', u'Russia', u'should', u'be', u'more', u'cheerful', u'expression', u'<START>', u'the', u'front', u'and', u'again', u'the', u'lime', u'flower', u'to', u'or', u'to', u'notice', u'that', u'pain', u'of', u'Moscow', u'with', u'alarm']
	print len(code) == 168
	print data2field.getAllBytes() == data
	print "done"

