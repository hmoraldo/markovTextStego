# create simple markov chain:
# python commandline.py --wordsPerState 1 createMarkov data/warandpeace.txt data/markovChain.json
# create markov chain with bigrams:
# python commandline.py --wordsPerState 2 createMarkov data/warandpeace.txt data/markovChain2.json

# test any markov chain:
# python commandline.py testMarkov data/markovChain.json any

# generate texts using both markov chains:
# python commandline.py --wordsPerState 1 genTextWithMarkov data/markovChain.json any
# python commandline.py --wordsPerState 2 genTextWithMarkov data/markovChain2.json any

# simple encode decode to json file:
# python commandline.py encode --markovInput data/markovChain.json tests/utils.pyc.orig.1 tests/encoded.json
# python commandline.py decode --markovInput data/markovChain.json tests/encoded.json tests/utils.pyc.1
# test with: diff tests/utils.pyc.orig.1 tests/utils.pyc.1

# encode decode to json file, using bigrams:
# python commandline.py encode --markovInput data/markovChain2.json --wordsPerState 2 tests/utils.pyc.orig.1 tests/encoded2.json
# python commandline.py decode --markovInput data/markovChain2.json --wordsPerState 2 tests/encoded2.json tests/utils.pyc.1

# encode decode to txt file, using bigrams:
# python commandline.py encodeFullText --markovInput data/markovChain2.json --wordsPerState 2 tests/utils.pyc.orig.1 tests/encoded2.txt
# python commandline.py decodeFullText --markovInput data/markovChain2.json --wordsPerState 2 tests/encoded2.txt tests/utils.pyc.1

import argparse
import markov
import utils
import variableSizeCode

# handle args
parser = argparse.ArgumentParser(description='Create markov chain, encode or decode')
parser.add_argument('mode', metavar='mode', type=str, choices=["createMarkov", "testMarkov", "genTextWithMarkov", "encode", "decode", "encodeFullText", "decodeFullText"],
                   help='select mode to use')
parser.add_argument('input', metavar='input', type=str,
                   help='input file to use')
parser.add_argument('output', metavar='output', type=str,
                   help='output file to use')
parser.add_argument('--markovInput', metavar='file', type=str,
                   help='for encode and decode modes, markov chain to use for input')
parser.add_argument('--wordsPerState', metavar='wordsPerState', choices=["1", "2"],
                   help='# of words in the input state for the markov chain')

args = parser.parse_args()


mode = args.mode
inputFile = args.input
outputFile = args.output

wordsPerState = args.wordsPerState
if wordsPerState == "1" or wordsPerState == "2": wordsPerState = int(wordsPerState)
if wordsPerState == None: wordsPerState = 1

if mode == "createMarkov":
	print "creating markov chain"
	print "using wordsPerState = " + repr(wordsPerState)
	markov.createMarkovChainFromFile(inputFile, outputFile, wordsPerState)
	print "done"
elif mode == "testMarkov":
	print "testing markov chain"
	markov.testMarkovChain(inputFile)
	print "done"
elif mode == "genTextWithMarkov":
	print "generating text using markov chain"
	print "using wordsPerState = " + repr(wordsPerState)
	print(utils.wordListToText(markov.generateTextUsingMarkovChain(inputFile, wordsPerState)))
	print "done"
elif mode == "encode":
	markovInputFile = args.markovInput
	print "encoding file (number to text) using markov chain, saving as json"
	variableSizeCode.encodeDataFromFile(inputFile, outputFile, markovInputFile, False, wordsPerState)
	print "done"
elif mode == "decode":
	markovInputFile = args.markovInput
	print "decoding file (json text to number) using markov chain"
	variableSizeCode.decodeDataFromFile(inputFile, outputFile, markovInputFile, False, wordsPerState)
	print "done"
elif mode == "encodeFullText":
	markovInputFile = args.markovInput
	print "encoding file (number to text) using markov chain, saving as txt"
	variableSizeCode.encodeDataFromFile(inputFile, outputFile, markovInputFile, True, wordsPerState)
	print "done"
elif mode == "decodeFullText":
	markovInputFile = args.markovInput
	print "decoding file (text in .txt to number) using markov chain"
	variableSizeCode.decodeDataFromFile(inputFile, outputFile, markovInputFile, True, wordsPerState)
	print "done"


