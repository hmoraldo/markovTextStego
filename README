Text steganography by Hernan Moraldo
http://www.hernan.moraldo.com.ar

Code for "An Approach for Text Steganography Based on Markov Chains", JAIIO / WSegI 2012
http://www.41jaiio.org.ar/sites/default/files/3_WSegI_2012.pdf


Usage:
======


There are two possible modes for encoding and decoding data into stego texts:

1- unigram mode (every state in the Markov chain is a single word)
2- bigram mode (every state in the Markov chain is a bigram)

These two modes are incompatible with each other. A message encoded in the bigram mode,
can't be decoded with the unigram mode.

Commands for unigram mode:
==========================

To create a Markov chain:

# python commandline.py --wordsPerState 1 createMarkov data/warandpeace.txt data/markovChain.json

to test the Markov chain:

# python commandline.py testMarkov data/markovChain.json any

to generate a text out of some input file input.data:

# python commandline.py encodeFullText --markovInput data/markovChain.json --wordsPerState 1 input.data encoded.txt

to decode a text file encoded.txt to the original input data:

# python commandline.py decodeFullText --markovInput data/markovChain.json --wordsPerState 1 encoded.txt output.data

Other commands are described in the top comments at commandline.py.



Commands for bigram mode:
==========================

To create a Markov chain:

# python commandline.py --wordsPerState 2 createMarkov data/warandpeace.txt data/markovChain2.json

to test the Markov chain:

# python commandline.py testMarkov data/markovChain2.json any

to generate a text out of some input file input2.data:

# python commandline.py encodeFullText --markovInput data/markovChain2.json --wordsPerState 2 input2.data encoded2.txt

to decode a text file encoded2.txt to the original input data:

# python commandline.py decodeFullText --markovInput data/markovChain2.json --wordsPerState 2 encoded2.txt output2.data

Other commands are described in the top comments at commandline.py.


