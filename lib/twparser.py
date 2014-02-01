import re;
from tiddlywiki import TiddlyWiki



class TwParser:
	"""Parses a TiddlyWiki object into an AST"""

	def __init__(self, tw):
		self.passages = {}
		self._parse(tw);
		pass

	def __repr__(self):
#		return "<TwParser\n" + '\n'.join(["\t" + str(psg) for psg in self.passages.values()]) + ">"
		return "<TwParser {0}>".format(ident_list(self.passages.values()))

	def _parse(self, tw):
		"""Parses the TiddlyWiki object"""
		for tiddler in tw.tiddlers.values():
			self._parse_tiddler(tiddler);

	def _parse_tiddler(self, tiddler):
		"""Parses a Tiddler object"""
		passage = Passage(tiddler)
		self.passages[passage.title] = passage




class Passage:
	"""Represents a parsed passage"""

	RE_ITEM_LIST = re.compile(r'^([#\*])\s(.*)$', flags=re.MULTILINE)
	RE_MACRO = re.compile(r'\<\<(\w+)(\s*.*?)\>\>')
	RE_LINK = re.compile(r'\[\[(.*?)\]\]')
	RE_IMG = re.compile(r'\[img\[(.*?)\]\]')
 	RE_TEXT = re.compile(r'(.*)', flags=re.DOTALL)

	def __init__(self, tiddler):
		self.title = tiddler.title
		self.commands = []
		self._parse(tiddler)

	def __repr__(self):
		return "<Passage {0}{1}>".format(self.title, ident_list(self.commands))

	def _parse(self, tiddler):
		tokens = self._tokenize(tiddler)
		self.commands += self._parse_commands(tokens)

	def _parse_commands(self, tokens):
		commands = []

		while tokens:
			token = tokens.pop(0)
			tk_type = token[0]
			if tk_type == 'tx':
				commands.append(TextCmd(token))
			elif tk_type == 'mc':
				macro = self._parse_macro(token, tokens)
				if macro:
					commands.append(macro)
			elif tk_type == 'im':
				commands.append(ImageCmd(token))
			elif tk_type == 'lk':
				commands.append(LinkCmd(token))
			elif tk_type == 'ul' or tk_type == 'ol':
				commands.append(ListCmd(token, self._parse_commands(token[1])))

		return commands

	# Well, it's not really a tokenizer, more like a 1st level parser, but meh.
	def _tokenize(self, tiddler):
		# Remove the line continuations (\ followed by line break)
		source = re.sub(r'\\[ \t]*\n', '', str(tiddler.text))
		return self._tokenize_string(source)

	def _tokenize_string(self, string):
		def test_command(string, remaining_tests):
			# Determine what will be checked
			if not remaining_tests:
				return []

			regex, action, skipped_chars = remaining_tests[0]
			remaining_tests = remaining_tests[1:]

			# Starts checking for snippets matching the regex
			tokens = []

			st_pos = 0
			st_len = len(string)
			for item in regex.finditer(string):
				# Processes preceding non-matching text
				it_st = item.start()
				if st_pos < it_st and st_pos < st_len:
					tokens += test_command(string[st_pos:it_st], remaining_tests)
				st_pos = item.end() + skipped_chars

				# Executes the action
				tokens += action(item)

			# Processes remaining text, if any.
			if st_pos < st_len:
				tokens += test_command(string[st_pos:st_len], remaining_tests)

			return tokens

		def process_item_list(match):
			kind = match.group(1)
			contents = match.group(2)
			list_type = 'ul' if kind == '*' else 'ol'
			return [(list_type, self._tokenize_string(contents.strip()))]

		def process_macro(match):
			return [('mc', (match.group(1), match.group(2)))]

		def process_image(match):
			return [('im', match.group(1))]

		def process_link(match):
			return [('lk', match.group(1))]

		def process_text(match):
			return [('tx', match.group(1))]

		tests = [
			(Passage.RE_ITEM_LIST, process_item_list, 1),
			(Passage.RE_MACRO, process_macro, 0),
			(Passage.RE_IMG, process_image, 0),
			(Passage.RE_LINK, process_link, 0),
            (Passage.RE_TEXT, process_text, 0)
		]

		return test_command(string, tests)

	def _parse_macro(self, token, tokens):
 		kind, params = token[1]
		if kind == 'set':
			macro = SetMacro(token)
		elif kind == 'pause':
			macro = PauseMacro(token)
		else:
			macro = InvalidMacro(token, 'unknown macro: ' + kind)

		if macro.error:
			self._warning(macro.error)
			return InvalidMacro(token, macro.error)

		return macro

	def _warning(self, msg):
		print 'Warning on {0}: {1}'.format(self.title, msg)




class AbstractCmd:
	"""Base class for the different kinds of commands"""

	def __init__(self, kind, token, children=None):
		self.kind = kind
		self.children = children
		self._parse(token)

	def __repr__(self):
		return '<cmd {0}>'.format(self.kind)


class TextCmd(AbstractCmd):
	"""Class for text commands"""

	def __init__(self, token):
		AbstractCmd.__init__(self, 'text', token)

	def __repr__(self):
		return '<cmd {0}{1}>'.format(self.kind, ident_list([self.text]))

	def _parse(self, token):
		self.text = token[1]


class ImageCmd(AbstractCmd):
	"""Class for image commands"""

	def __init__(self, token):
		AbstractCmd.__init__(self, 'image', token)

	def __repr__(self):
		return '<cmd {0}{1}>'.format(self.kind, ident_list([self.path]))

	def _parse(self, token):
		self.path = token[1]


class LinkCmd(AbstractCmd):
	"""Class for link commands"""

	def __init__(self, token):
		AbstractCmd.__init__(self, 'link', token)

	def __repr__(self):
		return '<cmd {0}\n\ttarget: {1}\n\tlabel: {2}\n\ton_click: {3}>'.format(self.kind, self.target, self.label, self.on_click)

	def _parse(self, token):
		text = token[1]

		link_action = text.split('][')
		self.on_click = link_action[1] if len(link_action) > 1 else None

		lbl_tgt = link_action[0].split('|')
		if len(lbl_tgt) > 1:
			self.target = lbl_tgt[-1]
			self.label = '|'.join(lbl_tgt[:-1])
		else:
			self.target = link_action[0]
			self.label = None

	def actual_label(self):
		return self.label if self.label else self.target


class ListCmd(AbstractCmd):
	"""Class for list commands"""

	def __init__(self, token, children):
		AbstractCmd.__init__(self, 'list', token, children)

	def __repr__(self):
		return '<cmd {0} ordered: {1}{2}>'.format(self.kind, self.ordered, ident_list(self.children))

	def _parse(self, token):
		self.ordered = token[0] != 'ul'




class AbstractMacro(AbstractCmd):
	"""Class for macros """

	RE_EXPRESSION = re.compile(r'(true|false|[\w\$])', flags=re.IGNORECASE)

	def __init__(self, token, children=[]):
		AbstractCmd.__init__(self, token[1][0], token, children)
		self.params = token[1][1]
		self.error = None

	def __repr__(self):
		return '<cmd {0}{1}>'.format(self.kind, ident_list([self.text]))

	def _parse(self, token):
		pass

	def _parse_expression(self, expr):
		expr = expr.strip()
		if not AbstractMacro.RE_EXPRESSION.match(expr):
			self.error = 'invalid expression: ' + expr
			return None

		if expr.lower() == 'true':
			return True
		elif expr.lower() == 'false':
			return False
		else:
			return expr




class InvalidMacro(AbstractMacro):
	"""Class for invalid macros"""

	def __init__(self, token, error=None):
		AbstractMacro.__init__(self, token)
		self.kind = 'invalid'
		self.error = error


class SetMacro(AbstractMacro):
	"""Class for the 'set' macro"""

	RE_ATTRIBUTION = re.compile(r'\s*([\w\$]+)\s*(?:=|\sto\s)\s*(.*)')

	def _parse(self, token):
		kind, params = token[1]
		match = SetMacro.RE_ATTRIBUTION.match(params)
		if not match:
			self.error = 'invalid "set" expression: ' + params
			return

		self.target = match.group(1)
		self.expr = self._parse_expression(match.group(2))


class PauseMacro(AbstractMacro):
	"""Class for the 'pause' macro"""





def ident_list(list):
	parts = []
	for o in list:
		for s in str(o).split('\n'):
			parts.append('\n\t' + s)

	return ''.join(parts)