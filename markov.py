import json
import math
import re
import random

import utils
import config

# CONFIG
minLineLen = 4


def countRepeatedWords(words):
	# given a list of words, count how many times each one is listed; case insensitive
	count = {}

	for word in words:
		w = word.lower()

		if w in count:
			count[w] = (word, count[w][1] + 1)
		else:
			count[w] = (word, 1)

	return count.values()


def computeProbabilities(words):
	# given a list of words, compute the probability (in a fraction) for each word
	count = countRepeatedWords(words)

	total = sum([c[1] for c in count])
	return [(c[0], (c[1], total)) for c in count]

# wordsPerState is either 1 (the chain keeps probabilities per bigram; 1 input word to 1 output word) or 2
# (the chain keeps probabilities for each 2 input words that go to 1 output word)
def createMarkovChain(inputData, wordsPerState):
	# split sentences, get bigrams
	lines = [re.findall(r"\w[\w']*", line) for line
		in re.split(r"\r\n\r\n|\n\n|\,|\.|\!", inputData)]
	lines = [[config.startSymbol] + line + [config.startSymbol] for line
		in lines if len(line) >= minLineLen]

	if wordsPerState == 1:
		bigrams = [[(line[word], line[word+1]) for word in range(len(line)-1)] for line in lines]
	elif wordsPerState == 2:
		bigrams1 = [[(line[word], line[word+1], line[word+2]) for word in range(len(line)-2)] for line in lines]
		# add special (start, start) -> out cases
		bigrams2 = [[(line[0], line[0], line[1])] for line in lines]
		bigrams = bigrams1 + bigrams2
	else:
		raise RuntimeError("wordsPerState should be either 1 or 2 only")

	# compute markov chain
	# in this context, we call bigrams the pairs (input state, output state); not the best name
	# when the input state has more than 1 word unfortunately
	bigramsDict = {}

	def addBigramToDict(word1, word2):
		word1b = utils.lowerWordOrList(word1)

		if word1b in bigramsDict:
			(w1, w2) = bigramsDict[word1b]
			w2.append(word2)
		else:
			bigramsDict[word1b] = (word1, [word2])

	for line in bigrams:
		for bigram in line:
			if wordsPerState == 1:
				addBigramToDict(bigram[0], bigram[1])
			elif wordsPerState == 2:
				addBigramToDict((bigram[0], bigram[1]), bigram[2])

	fullBigrams = bigramsDict.values()

	fullBigrams = [(bigram[0], computeProbabilities(bigram[1])) for bigram in fullBigrams]
	# at this point, fullBigrams contains the markovChain with probabilities in fractions

	return fullBigrams


# wordsPerState is either 1 (the chain keeps probabilities per bigram; 1 input word to 1 output word) or 2
# (the chain keeps probabilities for each 2 input words that go to 1 output word)
def createMarkovChainFromFile(inputFile, outputFile, wordsPerState):
	f = open(inputFile, 'r')
	inputData = f.read()
	f.close()

	bigrams = createMarkovChain(inputData, wordsPerState)

	# save
	jsonData = json.JSONEncoder().encode(bigrams)
	f = open(outputFile, 'w')
	f.write(jsonData)
	f.close()



# check markov file
def testMarkovChain(inputMarkov):
	f = open(inputMarkov, 'r')
	jsonData = f.read()
	f.close()

	data = json.JSONDecoder().decode(jsonData)

	errors = 0

	for bigram in data:
		(wordFrom, wordsTo) = bigram
		total = wordsTo[0][1][1]
		total2 = 0

		for word in wordsTo:
			total2 = total2 + word[1][0]

		if total != total2:
			print "error, denominator and total numerators are different!"


	if errors == 0:
		print "OK: no errors found in markov file"	
	else:
		print "ERROR: " + repr(errors) + " errors found in markov file"


# input is a markov chain
# see createMarkovChain for a description of the parameter wordsPerState
def generateTextUsingMarkovChain(inputMarkov, wordsPerState):
	f = open(inputMarkov, 'r')
	jsonData = f.read()
	f.close()

	data = json.JSONDecoder().decode(jsonData)

	words = []
	if wordsPerState == 1:
		prev = config.startSymbol
	elif wordsPerState == 2:
		prev = (config.startSymbol, config.startSymbol)

	markovDict = {}
	for bigram in data:
		markovDict[utils.lowerWordOrList(utils.listToTuple(bigram[0]))] = bigram[1]

	while True:
		m = markovDict[utils.lowerWordOrList(prev)]
		denominator = m[0][1][1]
		rnd = random.randint(1, denominator)
		total = 0
		nextWord = None

		for word in m:
			total = total + word[1][0]
			if total >= rnd:
				nextWord = word[0]
				break

		if nextWord == config.startSymbol:
			break

		words.append(nextWord)

		if wordsPerState == 1:
			prev = nextWord
		elif wordsPerState == 2:
			prev = (prev[1], nextWord)

	return words



