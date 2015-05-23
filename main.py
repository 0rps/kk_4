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

			# hardcode: checking is current parser is var parser
			# and if next char in chain is '=' then print result[0]
			flag = self.isvar and res[1][0] == '='

			if res is not None:
				otherRes = other.parse(res[1])
				if otherRes is None:
					return None

				res[0].extend(otherRes[0])
				res[1] = otherRes[1]

				if flag:
					varsResult.append(reduce(lambda x, y: "{0} {1}", res[0], ''))

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


def regexParser(regex, isvar=False):
	cregex = re.compile('^{0}$'.format(regex))
	parser = baseParser(lambda expr: cregex.match(expr) is not None)
	parser.isvar = isvar

	return parser

def manyWordParser(*args):
	res = wordParser(args[0])
	for arg in args[1:]:
		res = res | wordParser(arg)

	return res

if __name__ == '__main__':

	relationOperation = manyWordParser('<', '<=', '==', '<>', '>', '>=')
	sumOperation = manyWordParser('-', '+')
	multiplyOperation = manyWordParser('*', '/')

	arithmeticExpr = wordParser('non_alter')
	term = wordParser('non_alter')
	operatorsList = wordParser('non_alter')

	for i in range(0, 50):
		factor = regexParser('[a-z]+') | regexParser('[0-9]+') | wordParser('(') >> arithmeticExpr >> wordParser(')')
		term = term >> multiplyOperation >> factor | factor
		arithmeticExpr = arithmeticExpr >> sumOperation >> term | term
		expr = arithmeticExpr >> relationOperation >> arithmeticExpr | arithmeticExpr
		operator = regexParser('[a-z]+', True) >> wordParser('=') >> expr
		operatorsList = operator | operatorsList >> wordParser(';') >> operator
		block = wordParser('begin') >> operatorsList >> wordParser('end')
		s = block

	chain = '1234 * 1234 * var * 134'
	print term.parse(chain.split(' '))