## Text steganography

Code for *"An Approach for Text Steganography Based on Markov Chains"*, JAIIO / WSegI 2012
http://www.41jaiio.org.ar/sites/default/files/3_WSegI_2012.pdf

Abstract: *A text steganography method based on Markov chains is introduced, together with a reference implementation. This method allows for information hiding in texts that are automatically generated following a given Markov model. Other Markov - based systems of this kind rely on big simplifications of the language model to work, which produces less natural looking and more easily detectable texts. The method described here is designed to generate texts within a good approximation of the original language model provided.*

By Hernan Moraldo
http://linkedin.com/in/hmoraldo
http://www.hernan.moraldo.com.ar


### Online demo

This Github repository contains the Python prototype that was presented together with the paper. Recently, **Jackson Thuraisamy** implemented a text steganography library in JavaScript that is adapted from the paper linked above.

Please refer to the following project to see an online demo of this method:

- Jackson Thuraisamy's JavaScript code: https://github.com/jthuraisamy/markovTextStego.js
- Jackson's online demo: http://jthuraisamy.github.io/markovTextStego.js/


## Usage:


There are two possible modes for encoding and decoding data into stego texts:

1- unigram mode (every state in the Markov chain is a single word)
2- bigram mode (every state in the Markov chain is a bigram)

These two modes are incompatible with each other. A message encoded in the bigram mode,
can't be decoded with the unigram mode.

### Commands for unigram mode:

To create a Markov chain:

`python commandline.py --wordsPerState 1 createMarkov data/warandpeace.txt data/markovChain.json`

to test the Markov chain:

`python commandline.py testMarkov data/markovChain.json any`

to generate a text out of some input file input.data:

`python commandline.py encodeFullText --markovInput data/markovChain.json --wordsPerState 1 input.data encoded.txt`

to decode a text file encoded.txt to the original input data:

`python commandline.py decodeFullText --markovInput data/markovChain.json --wordsPerState 1 encoded.txt output.data`

Other commands are described in the top comments at commandline.py.



### Commands for bigram mode:

To create a Markov chain:

`python commandline.py --wordsPerState 2 createMarkov data/warandpeace.txt data/markovChain2.json`

to test the Markov chain:

`python commandline.py testMarkov data/markovChain2.json any`

to generate a text out of some input file input2.data:

`python commandline.py encodeFullText --markovInput data/markovChain2.json --wordsPerState 2 input2.data encoded2.txt`

to decode a text file encoded2.txt to the original input data:

python commandline.py decodeFullText --markovInput data/markovChain2.json --wordsPerState 2 encoded2.txt output2.data`

Other commands are described in the top comments at commandline.py.


