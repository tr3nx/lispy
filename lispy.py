#!/usr/bin/python3
import re

class InputReader:
	def __init__(self, input):
		self.input = input
		self.pos = 0

	def __str__(self):
		return self.input

	def top(self):
		if self.eof():
			return ''

		return self.skip().top() if (self.peek() == ' ') else self.input[self.pos:]

	def read(self, amount=1):
		ret = ''
		if self.eof():
			return ret

		for _ in range(amount):
			ret += self.next()

		return ret

	def next(self):
		ret = self.input[self.pos]
		self.pos += 1
		return '' if (self.eof()) else ret

	def skip(self, amount=1):
		self.pos += amount;
		return self;

	def peek(self, offset=0):
		return '' if (self.pos + offset >= len(self.input)) else self.input[self.pos + offset]

	def eof(self):
		return self.pos >= len(self.input) and self.peek() == '';

class Tokenizer:
	def __init__(self, reader, types):
		self.reader = reader
		self.types = types
		self.tokens = self.tokenize()

	def tokenize(self):
		tokens = []

		while not self.reader.eof():
			code = reader.top();
			for (name, reg) in self.types:
				match = re.match(r'^(' + reg + ')', code)
				if match:
					matched = match.group()
					reader.skip(len(matched))
					if name == "integer":
						matched = int(matched)

					tokens.append({'name'  : name, 'value' : matched })
					break

		return tokens

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tree = self.parse()

	def parse(self):
		return self.parse_expr()

	def parse_expr(self):
		if self.peek() == 'oparen':
			return self.parse_list()

		return self.parse_atomic()

	def parse_list(self):
		if self.peek(1) == 'symbol':
			if self.tokens[1]['value'] == 'lambda':
				return self.parse_lambda()

			if self.tokens[1]['value'] == 'quote':
				return self.parse_quote()

		return self.parse_procedure()

	def parse_lambda(self):
		self.consume('oparen')
		self.consume('symbol')
		self.consume('oparen')

		argvars = []
		while not self.peek() == 'cparen':
			argvars.append(self.consume('symbol')['value'])

		self.consume('cparen')
		body = self.parse_expr()
		self.consume('cparen')

		return { 'name' : 'lambda', 'argvars' : argvars, 'body' : body }

	def parse_quote(self):
		self.consume('oparen')
		self.consume('symbol')

		quoted = ''
		depth = 0
		while True:
			if self.peek() == 'cparen' and depth == 0:
				break
			if self.peek() == 'oparen':
				depth += 1
			if self.peek() == 'cparen':
				depth -= 1

			toke = self.tokens[-1:][0]
			self.tokens = self.tokens[-1:] + self.tokens[:-1]
			quoted += str(toke.value)

		self.consume('cparen')

		return { 'name' : 'quote', 'quoted' : quoted }

	def parse_procedure(self):
		self.consume('oparen')

		if self.peek() == 'oparen':
			rator = self.parse_list()
		else:
			rator = self.consume('symbol')['value']

		rand = []
		while not self.peek() == 'cparen':
			rand.append(self.parse_expr())

		self.consume('cparen')

		return { 'name' : 'procedure', 'func' : rator, 'args' : rand }

	def parse_atomic(self):
		if self.peek() == 'integer':
			return self.consume('integer')['value']

		if self.peek() == 'string':
			return self.consume('string')['value']

		return self.consume('symbol')['value']

	def peek(self, offset=0):
		if offset >= len(self.tokens) or not self.tokens[offset]:
			raise ValueError('Parse Error: Closing paren missing?')

		return self.tokens[offset]['name']

	def consume(self, name):
		toke = self.tokens[0:][0]
		self.tokens = self.tokens[1:] + self.tokens[:1]
		if not toke['name'] == name:
			raise ValueError('Syntax Error: [{}] Expected \'{}\' but got \'{}\''.format(len(self.tokens), name, toke['name']))
		return toke

class Generator:
	def __init__(self, tree):
		self.tree = tree
		self.code = self.generate(self.tree)

	def generate(self, tree):
		code = ''
		if isinstance(tree, dict):
			if tree['name'] == 'procedure':
				code += self.generate_procedure(tree['func'], tree['args'])
			elif tree['name'] == 'quote':
				code += self.generate_quote(tree['quoted'])
			else:
				code += self.generate_lambda(tree['argvars'], tree['body'])
		elif isinstance(tree, list):
			code += ''.join(str(t) for t in tree)
		else:
			code += tree

		return code

	def generate_procedure(self, rator, args):
		rand = []
		for arg in args:
			if isinstance(arg, dict):
				rand.append(self.generate(arg))
			else:
				rand.append(arg)

		if isinstance(rator, dict):
			rator = self.generate(rator)

		return '(' + rator + ' ' + ' '.join(str(t) for t in rand) + ')'

	def generate_lambda(self, argvars, body):
		return '(lambda (' + ''.join(str(t) for t in argvars) + ') ' + self.generate(body) + ')'

	def generate_quote(self, quoted):
		return '(quote ' + quoted + ')';

class Evaluator:
	def __init__(self, tree, builtins):
		self.tree = tree
		self.builtins = builtins
		self.result = self.evaluate(self.tree)

	def evaluate(self, node):
		if isinstance(node, dict):
			if node['name'] == "procedure":
				return self.evaluate_procedure(node)
			if node['name'] == "lambda":
				return self.evaluate_lambda(node)
			if node['name'] == "quote":
				return self.evaluate_quote(node)

		return node

	def evaluate_procedure(self, node):
		args = []
		for arg in node['args']:
			if (isinstance(arg, dict)):
				args.append(self.evaluate(arg))
			else:
				args.append(arg)

		return self.builtins[self.evaluate(node['func'])](args)

	def evaluate_lambda(self, node):
		pass

class Builtins:
	def __init__(self):
		self.funcs = {
			'+': self.add,
			'*': self.multiply
		}

	def add(self, args):
		total = 0
		for arg in args:
			total += int(arg)
		return total

	def multiply(self, args):
		total = 1
		for arg in args:
			total *= int(arg)
		return total

# code = '((lambda (x) (+ 14 x)) (+ 23 (* 5 1)))'
code = '(+ (* 4 10) 2)'
reader = InputReader(code)
# print(reader)

tokenizer = Tokenizer(reader, [
	('oparen',  r'\('),
	('cparen',  r'\)'),
	('integer', r'[\-]?[0-9]+(?:[\.]?[0-9]+)?'),
	('string',  r'\'[^\']*\''),
	('symbol',  r'[a-zA-Z0-9+*]+'),
])
tokens = tokenizer.tokens
# print(tokens)
# for token in tokens:
	# print(token)

parser = Parser(tokens)
# print(parser.tree)

generator = Generator(parser.tree)
print(generator.code)
print('Matching? {}'.format(generator.code == code))

builtins = Builtins()
evaluator = Evaluator(parser.tree, builtins.funcs)
print('Result: {}'.format(evaluator.result))
