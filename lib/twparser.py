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
	RE_LINK = re.compile(r'\[\[(.*?)\]\]')

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
			elif tk_type == 'lk':
				commands.append(LinkCmd(token))
			elif tk_type == 'ul' or tk_type == 'ol':
				commands.append(ListCmd(token, self._parse_commands(token[1])))

		return commands

	def _tokenize(self, tiddler):
		# Remove the line continuations (\ followed by line break)
		source = re.sub(r'\\[ \t]*\n', '', str(tiddler.text))
		return self._tokenize_string(source)

	def _tokenize_string(self, string):
		tokens = []

		# Processes the ordered/unordered lists
		st_pos = 0
		st_len = len(string)
		for item in Passage.RE_ITEM_LIST.finditer(string):
			# Processes non-list strings
			it_st = item.start()
			if st_pos < it_st and st_pos < st_len:
				tokens += self._tokenize_string_not_uli(string[st_pos:it_st])
			st_pos = item.end() + 1 # Skips the line break after the item

			# Processes list strings
			tokens += self._tokenize_string_uli(item.group(1), item.group(2))

		# Processes remaining strings, if any.
		if st_pos < st_len:
			tokens += self._tokenize_string_not_uli(string[st_pos:st_len])

		return tokens

	def _tokenize_string_uli(self, kind, contents):
		list_type = 'ul' if kind == '*' else 'ol'
		return [(list_type, self._tokenize_string(contents.strip()))]

	def _tokenize_string_not_uli(self, string):
		tokens = []

		# Processes the links
		st_pos = 0
		st_len = len(string)
		for item in Passage.RE_LINK.finditer(string):
			# Processes non-link text
			it_st = item.start()
			if st_pos < it_st and st_pos < st_len:
				tokens.append(('tx', string[st_pos:it_st]))
			st_pos = item.end()

			# Processes link text
			tokens.append(('lk', item.group(1)))

		# Processes remaining strings, if any.
		if st_pos < st_len:
			tokens.append(('tx', string[st_pos:st_len]))

		return tokens




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


class ListCmd(AbstractCmd):
	"""Class for list commands"""

	def __init__(self, token, children):
		AbstractCmd.__init__(self, 'list', token, children)

	def __repr__(self):
		return '<cmd {0} ordered: {1}{2}>'.format(self.kind, self.ordered, ident_list(self.children))

	def _parse(self, token):
		self.ordered = token[0] != 'ul'


def ident_list(list):
	parts = []
	for o in list:
		for s in str(o).split('\n'):
			parts.append('\n\t' + s)

	return ''.join(parts)