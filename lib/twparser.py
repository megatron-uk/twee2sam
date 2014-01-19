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
	RE_LINK = re.compile(r'\[\[(.*)\]\]')

	def __init__(self, tiddler):
		self.title = tiddler.title
		self.commands = []
		self._parse(tiddler)

	def __repr__(self):
		return "<Passage {0}{1}>".format(self.title, ident_list(self.commands))

	def _parse(self, tiddler):
		tokens = self._tokenize(tiddler)
		self.commands = tokens

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

##		tokens = []
##
##		# Remove the line continuations (\ followed by line break)
##		source = re.sub(r'\\[ \t]*\n', '', str(tiddler.text))
##
##		for line in source.split('\n'):
##			tokens += self._tokenize_line(line)
##
##		self.commands.append(source)
##
##	def _tokenize_line(self, line):
##		pass




def ident_list(list):
	parts = []
	for o in list:
		for s in str(o).split('\n'):
			parts.append('\n\t' + s)

	return ''.join(parts)