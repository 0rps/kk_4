from _ast import operator

__author__ = 'orps'

import re

varsResult = []

class Parser:
	def __init__(self, parseFunction=None):
		if parseFunction is not None:
			self.parse = parseFunction
		else:
			self.parse = lambda expr: [expr[:1], expr[1:]] if expr != [] else 'OK'

		self.isvar = False

	def __rshift__(self, other):

		def internalParse(expr):
			res = self.parse(expr)

			if res is not None:
				otherRes = other.parse(res[1])

				if otherRes is None:
					return None

				res[0].extend(otherRes[0])
				res[1] = otherRes[1]

				if other.isvar:
					varsResult.append(reduce(lambda x, y: "{0} {1}".format(x, y), res[0], ''))

				return res

			return None

		return Parser(internalParse)

	def __or__(self, other):

		def internalParse(expr):
			res = self.parse(expr)
			if res is not None:
				return res

			return other.parse(expr)

		return Parser(internalParse)


def baseParser(condition):
	parser = Parser()

	def internalParse(expr):
		res = parser.parse(expr)
		if condition(res[0][-1]):
			return res
		else:
			return None

	return Parser(internalParse)


def wordParser(letter):
	return baseParser(lambda c: c == letter)


def regexParser(regex):
	cregex = re.compile('^{0}$'.format(regex))
	parser = baseParser(lambda expr: cregex.match(expr) is not None)

	return parser

def manyWordParser(*args):
	res = wordParser(args[0])
	for arg in args[1:]:
		res = res | wordParser(arg)

	return res

def saveVarParser():
	def internalParse(expr):
		return [[], expr]

	parser = Parser(internalParse)
	parser.isvar = True

	return parser


if __name__ == '__main__':

	relationOperation = manyWordParser('<', '<=', '==', '<>', '>', '>=')
	sumOperation = manyWordParser('-', '+')
	multiplyOperation = manyWordParser('*', '/')

	arithmeticExpr = wordParser('non_alter')
	arithmeticExpr_dash = wordParser('non_alter')
	operatorsList_dash = wordParser('non_alter')
	term_dash = wordParser('non_alter')

	for i in range(0, 50):
		factor = regexParser('[a-z]+') | regexParser('[0-9]+') | wordParser('(') >> arithmeticExpr >> wordParser(')')
		term_dash = multiplyOperation >> factor >> term_dash | multiplyOperation >> factor
		term = factor >> term_dash | factor
		arithmeticExpr_dash = sumOperation >> term | sumOperation >> term >> arithmeticExpr_dash
		arithmeticExpr = term >> arithmeticExpr_dash | term
		expr = arithmeticExpr >> relationOperation >> arithmeticExpr | arithmeticExpr
		operator = regexParser('[a-z]+') >> wordParser('=') >> expr >> saveVarParser()
		operatorsList_dash = wordParser(';') >> operator | wordParser(';') >> operator >> operatorsList_dash
		operatorsList = operator >> operatorsList_dash | operator
		block = wordParser('begin') >> operatorsList >> wordParser('end')
		s = block

	chain = 'begin arg = 1234 * 1234 * var * 134 ; vav = 134 * 12 end'
	#chain = ''
	chain = chain.split(' ')
	print s.parse(chain)
	print ''
	for line in varsResult:
		print line