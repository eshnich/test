
import sys


class EvaluationError(Exception):
	"""Exception to be raised if there is an error during evaluation."""
	pass

def tokenize(source):
	"""
	Splits an input string into meaningful tokens (left parens, right parens,
	other whitespace-separated values).  Returns a list of strings.

	Arguments:
		source (str): a string containing the source code of a carlae
					  expression
	"""
	lines = str.split(source, '\n')
	array = []
	for line in lines:
		array.extend(tokenize_line(line))
	return array
	
def tokenize_line(source):
	"""
	Splits an input string into meaningful tokens, where the input string consists
	of only one line of input

	Arguments:
		source (str): a string containing the source code of a carlae
					  expression
	"""
	array = str.split(source)
	new_array = []
	for token in array:
		last = 0
		for i in range(len(token)):
			if token[i] == ';':
				return new_array
			if token[i] in ['(',')']:
				if i > last:
					new_array.append(token[last:i])
				new_array.append(token[i])
				last = i+1
		if last < len(token):
			new_array.append(token[last:])
	return new_array

def right_type(x):
	"""
	Takes in a string x, and returns a float/int if x represents a float/int,
	or a string otherwise
	"""
	if isfloat(x):
		return float(x)
	if isint(x):
		return int(x)
	return x

def isfloat(x):
	"""
	Returns True if x is a float
	"""
	try:
		float(x)
		return True
	except ValueError:
		return False

def isint(x):
	"""
	Returns True if x is an int
	"""
	try:
		int(x)
		return True
	except ValueError:
		return False

def matching_paren(array):
	"""
	Given a list of tokens beginning with "(", returns the index of the closed parenthesis
	which matches this opening parenthesis. If no closed parenthesis exists, raise SyntaxError
	"""

	count = 0
	for i in range(len(array)):
		x = array[i]
		if x == ")":
			count -= 1
		if x == "(":
			count += 1
		if count == 0:
			return i
	raise SyntaxError

def parse(tokens):		 
	"""
	Parses a list of tokens, constructing a representation where:
		* symbols are represented as Python strings
		* numbers are represented as Python ints or floats
		* S-expressions are represented as Python lists

	Arguments:
		tokens (list): a list of strings representing tokens
	"""

	#first token is an atomic expression
	if tokens[0] not in ["(",")"]:
		return right_type(tokens[0])

	#otherwise, list must begin with ( and end with )
	if tokens[0] != "(" or tokens[-1] != ")":
		raise SyntaxError

	n = len(tokens)
	i = 1
	array = []

	#go through the list, recursively calling parse on each of the subexpressions
	while i<n-1:
		#next expression is a subexpression
		if tokens[i] == "(":
			end = matching_paren(tokens[i:n-1])
			exp = parse(tokens[i:i+end+1])
			i += end + 1
		#unmatched closed parenthesis
		elif tokens[0] == ")":
			raise SyntaxError
		#next expression is a number/symbol
		else:
			exp = parse([tokens[i]])
			i += 1
		array.append(exp)
	return array

#product of an array of elements
def prod(array):
	i = 1
	for x in array:
		i *= x
	return i

def equals(args): return ((len(args) == 1) or (args[0] == args[1] and equals(args[1:]))) #array is all equal
def greater(args): return ((len(args) == 1) or (args[0] > args[1] and greater(args[1:]))) #array in increasing order
def greater_equal(args): return ((len(args) == 1) or (args[0] >= args[1] and greater_equal(args[1:]))) #array in nondecreasing order
def less(args): return ((len(args) == 1) or (args[0] < args[1] and less(args[1:]))) #array in decreasing order
def less_equal(args): return ((len(args) == 1) or (args[0] <= args[1] and less_equal(args[1:]))) #array in nonincreasing order
def not_x(x): return False if x[0] else True #negate a function

class LinkedList():

	def __init__(self, elt, next_val):
		self.elt = elt
		self.next = next_val

def list_func(args):
	"""
	creates a Linked List from a list of arguments
	"""
	if not args:
		return None
	else:
		head = LinkedList(args[0],list_func(args[1:]))
	return head

def car(l):
	#returns the head of a LinkedList
	if type(l[0]) is not LinkedList:
		raise EvaluationError
	return l[0].elt

def cdr(l):
	#returns the LinkedList formed be removing the first element
	if type(l[0]) is not LinkedList:
		raise EvaluationError
	return l[0].next

def length(l):
	#return the length of a linked list
	if type(l) is list:
		l = l[0]
	if l == None:
		return 0
	if type(l) is not LinkedList:
		raise EvaluationError
	return 1 + length(l.next)

def access(a):
	#accesses the element at the ith index of the list
	l = a[0]
	if l == None:
			raise EvaluationError
	index = a[1]
	i = 0
	while (i < index):
		if l == None:
			raise EvaluationError
		l = l.next
		i+=1
	return l.elt

def concat(lists):
	#concatenates a list of LinkedList objects
	if len(lists) == 0:
		return None
	if len(lists) == 1:
		return lists[0]
	l = lists[0]
	if l is None:
		return concat(lists[1:])
	head = LinkedList(l.elt,None)
	r = head
	while l.next is not None:
		l = l.next
		r.next = LinkedList(l.elt,None)
		r = r.next
	r.next = concat(lists[1:])
	return head

def map_func(args):
	#applies a given function to each element of a LinkedList, returning a new LinkedList
	f = args[0]
	l = args[1]
	head = LinkedList(call(f,[l.elt]),None)
	node = head
	
	for i in range(1,length(l)):
		l = l.next
		node.next = LinkedList(call(f,[l.elt]),None)
		node = node.next
	return head

def filter_func(args):
	#returns a LinkedList of elements satisfying a boolean function
	f = args[0]
	l = args[1]

	vals = []
	for i in range(0,length(l)):
		if call(f,[l.elt]):
			vals.append(l.elt)
		l = l.next
	return list_func(vals)

def reduce(args):
	#recursively applies a function to members of a LinkedList
	f = args[0]
	l = args[1]
	initial = args[2]

	if l is None:
		return initial
	initial = call(f,[initial,l.elt])
	return reduce([f,l.next,initial])

def evaluate_file(file, env = None):
	#evaluates the content of a file
	exp = open(file).read()
	if env == None:
		env = Environment(builtin,{})
	return evaluate(parse(tokenize(exp)),env)

def begin(args):
	return args[len(args)-1]	

#builtin functions
carlae_builtins = {
	'+': sum,
	'-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
	'*': prod,
	'/': lambda args: args[0]/prod(args[1:]),
	'#t': True,
	'#f': False,
	'=?': equals,
	'>': greater,
	'>=': greater_equal,
	'<': less,
	'<=': less_equal,
	'not': not_x,
	'list': list_func,
	'car': car,
	'cdr': cdr,
	'length': length,
	'elt-at-index': access,
	'concat': concat,
	'map': map_func,
	'filter': filter_func,
	'reduce': reduce,
	'begin': begin
}



#Environment class - contains pointer to parent env. and dictionary of variable names
class Environment():

	def __init__(self,parent,vals):
		self.parent = parent
		self.vals = vals

#builtin environment - has carlae builtins as its variables
builtin = Environment(None,carlae_builtins)


def find_key(key, env):
	"""
	Given a key and an environment, determines what that key maps to in that environment
	"""
	if key in env.vals:
		return env.vals[key]
	elif env.parent == None:
		return None
	else:
		return find_key(key,env.parent)

def find_env(key, env):
	"""
	Given a key and an environment, determines what environment that key is defined in
	"""
	if key in env.vals:
		return env
	elif env.parent == None:
		return None
	else:
		return find_env(key,env.parent)

#Function class:
#args - array of arguments to the Function
#function - expression which represents body of function
#env - environment in which Function was 
class Function():

	def __init__(self,args,function,env):
		self.args = args
		self.function = function
		self.env = env

def call(f,args):
	"""
	calls the function f with arguments args, where
	f is either a built in function or Function object
	"""
	if type(f) is Function:
		new_env = Environment(f.env,{})
		if len(args) != len(f.args):
			raise EvaluationError
		for i in range(len(args)):
			new_env.vals[f.args[i]] = args[i]
		return evaluate(f.function,new_env)
	if callable(f):
		return f(args)
	raise EvaluationError



def evaluate(tree, env=None):
	"""
	Evaluate the given syntax tree according to the rules of the carlae
	language.

	Arguments:
		tree (type varies): a fully parsed expression, as the output from the
							parse function
	"""

	#default environment if none is specified
	if env == None:
		env = Environment(builtin,{})

	#tree is a number
	if type(tree) is float or type(tree) is int:
		return tree

	#tree is an expression
	if type(tree) is list:
		#empty list
		if not tree:
			raise EvaluationError

		#'if' special form
		if tree[0] == "if":
			if evaluate(tree[1], env):
				return evaluate(tree[2],env)
			return evaluate(tree[3],env)

		#'and' special form
		if tree[0] == "and":
			for exp in tree[1:]:
				if not evaluate(exp,env):
					return False
			return True

		#'or' special form
		if tree[0] == "or":
			for exp in tree[1:]:
				if evaluate(exp,env):
					return True
			return False

		#'define' special form
		if tree[0] == "define":
			#first argument is an S-expression, so we're using the shortcut for defining a function
			if type(tree[1]) is list:
				name = tree[1][0]
				result = Function(tree[1][1:],tree[2],env)
			else:
				#defining a variable
				name = tree[1]
				result = evaluate(tree[2],env)

			env.vals[name] = result
			return result

		#'lambda' special form - defining a function
		if tree[0] == "lambda":
			result = Function(tree[1],tree[2],env)
			return result

		#'let' special form
		if tree[0] == "let":
			variables = tree[1]
			body = tree[2]
			var = {}
			for name,value in variables:
				var[name] = evaluate(value, env)
			new_env = Environment(env,var)
			result = evaluate(body,new_env)
			return result

		#'set' special form
		if tree[0] == "set!":

			stored = find_env(tree[1],env)
			if stored == None:
				raise EvaluationError
			result = evaluate(tree[2],env)
			stored.vals[tree[1]] = result
			return result

		#if not a special form, then we evaluate the expression by recursively evaluating its subexpressions
		fn = evaluate(tree[0],env)
		args = []
		for var in tree[1:]:
			args.append(evaluate(var,env))

		return call(fn, args)

	#otherwise, we get the value of a variable
	if find_key(tree, env) != None:
		return find_key(tree,env)

	raise EvaluationError

#return result + environment result was calculating in 
def result_and_env(tree, env = None):
	if env == None:
		env = Environment(builtin,{})
	return (evaluate(tree,env), env)

#REPL
if __name__ == '__main__':
	# code in this block will only be executed if lab.py is the main file being
	# run (not when this module is imported)
	global_env = Environment(builtin,{})

	#looks at command line arguments, if any
	if len(sys.argv) > 1:
		for i in range(1,len(sys.argv)):
			evaluate_file(sys.argv[i],global_env)
	run = True
	
	#REPL
	while run:
		try:
			val = input("in> ")
			if val == "QUIT":
				run = False
			else:
			
				tokens = tokenize(val)
				parsed = parse(tokens)
				result = evaluate(parsed,global_env)
				print(result)
		except (EvaluationError, SyntaxError):
			print("ERROR")