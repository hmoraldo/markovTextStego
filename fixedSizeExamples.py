"generates the examples shown in the paper, for fixed size encoding"
import config
import utils
import bigBitField
import fixedSizeCode

def testExample(data, markovChain):
	print "---"
	print "input: "+repr(data)
	miniBF = bigBitField.BigBitField(data, False)
	print "output: "+ repr(fixedSizeCode.encodeBitsToWordList(miniBF, markovChain, config.startSymbol, 1))

mc = [
	[config.startSymbol, [ ["s1", [1, 2]], ["s2", [1, 2]] ]],
	["s1", [ ["s3", [1, 5]], ["s4", [4, 5]] ]],
	["s2", [ ["s4", [1, 4]], ["s5", [3, 4]] ]],
	["s3", [ [config.startSymbol, [1, 1]] ]],
	["s4", [ ["s6", [3, 10]], ["s7", [7, 10]] ]],
	["s5", [ ["s7", [1, 10]], ["s8", [9, 10]] ]],
	["s6", [ [config.startSymbol, [1, 1]] ]],
	["s7", [ [config.startSymbol, [1, 1]] ]],
	["s8", [ [config.startSymbol, [1, 1]] ]]
	]


testExample("0", mc)
testExample("1", mc)
testExample("00", mc)
testExample("01", mc)
testExample("10", mc)
testExample("11", mc)
testExample("000", mc)
testExample("001", mc)
testExample("010", mc)
testExample("011", mc)
testExample("100", mc)
testExample("101", mc)
testExample("110", mc)
testExample("111", mc)
testExample("0000", mc)
testExample("0001", mc)
testExample("0010", mc)
testExample("0011", mc)
testExample("0100", mc)
testExample("0101", mc)
testExample("0110", mc)
testExample("0111", mc)
testExample("1000", mc)
testExample("1001", mc)
testExample("1010", mc)
testExample("1011", mc)
testExample("1100", mc)
testExample("1101", mc)
testExample("1110", mc)
testExample("1111", mc)
testExample("00000", mc)
testExample("11111", mc)

