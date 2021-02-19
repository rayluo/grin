# coding: utf-8
#import logging  # It has lots dependency, thus slower than most other modules.
    # Avoid it. See also https://github.com/brython-dev/brython/issues/1607
import json
#import pickle  # pickle requires a binary file, but Brython supports text only
from collections import defaultdict


__version__ = "2.0.0"


def tree():  # https://gist.github.com/hrldcpr/2012250
    return defaultdict(tree)


def locate(node, path, *, readonly=False):
    """For given path (which is a sequence) and a starting node,
    return its node (which can be an empty dict"""
    for level in path:
        if level not in node and readonly:  # This helps when node is a normal dict
            return  # Gracefully downgrade
        node = node[level]
    return node


def nodes(root):
    """Return an iterator which yield each node, in Inorder traversal.
    Path info would not be available, though."""
    yield root
    for k, v in root.items():
        if isinstance(v, dict):  # So it supports both defaultdict and dict
            for node in nodes(v):
                yield node


class Codes(object):
    """Represent codes into tree for faster scan.

    >>> codes = Codes({
    ...     'ten':  ['foo', 'bar'],
    ...     'two':  ['hello', 'world'],
    ...     })
    >>> snapshot = json.dumps(codes._root, sort_keys=True)
    >>> snapshot
    '{"t": {"e": {"n": {"": ["foo", "bar"]}}, "w": {"o": {"": ["hello", "world"]}}}}'

    >>> codes.get("ten")
    ['foo', 'bar']
    >>> codes.get("te")
    ['foo', 'bar']
    >>> codes.get("t")
    ['foo', 'bar', 'hello', 'world']
    >>> codes.get("t", limit=3)
    ['foo', 'bar', 'hello']
    >>> codes.get("t", limit=1)
    ['foo']

    >>> codes2 = Codes()
    >>> codes2._root = json.loads(snapshot)  # Side effect: it becomes a normal dict
    >>> codes2.get("ten")
    ['foo', 'bar']
    >>> codes2.get("te")
    ['foo', 'bar']
    """
    HZ = ""  # This will be used as a key to mean a code has corresponding hanzi
            # We choose a string NOT conflict with input alphabet.
            # Do not use None, because None can not be round-trip to/from json

    def __init__(self, mappings=None):
        self._root = tree()
        for code, hz in (mappings or {}).items():
            self.add(code, hz)

    def add(self, path, values):
        """Store leaf as {None: ["foo", "bar"]}"""
        ## Brython 3.9.1 seems to not support setdefault(...)
        #locate(self._root, path).setdefault(None, []).extend(values)
        node = locate(self._root, path)
        if self.HZ not in node:
            node[self.HZ] = []
        node[self.HZ].extend(values)

    def get(self, path, *, limit=None):
        limit = limit or 10
        candidates = []
        branch = locate(self._root, path, readonly=True)
        for node in nodes(branch) if branch else []:
            # The Inorder traversal of nodes() naturally favors short code
            candidates.extend(node.get(self.HZ, []))
            if len(candidates) >= limit:
                break  # Early exit
        return candidates[:limit]


class GreenInput(object):
    """GRIN(GReen INput)

        这个绿色输入法软件在使用上并不如主流的各种输入法软件方便，
    它甚至需要你在结果窗口自己把内容粘贴到其它目标软件之中。
        它主要用于在网吧之类的不允许使用者随意安装软件的场合使用。
    因为本绿色输入法不需要往Windows系统及注册表之中写入任何内容。
        具体的输入法编码规则，是由被加载的符合特定规则的码表文件
    指定。所以理论上只要能配合适当的码表，就可以用本输入法软件按
    任意输入法的编码方式进入文字输入。码表格式请参考本软件附带的
    若干个示范*.w2k格式文件。
        需要提供或交流输入法或码表的人士可联系 rayluo.mba@gmail.com ,
    主题请写明《关于GRIN的码表》。

    rayluo.mba@gmail.com 2021
    """
    MaxCodes = 4  # None means unlimited
    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    wildcard = '?'
    codename = "Built-in Input Method for test"
    codes = Codes({  # Words in Unicode. Example: { 'ni':[u'你', u'妮'], ... }
        'zero': ['零'],  # Use this to test auto-select when max-code rached with single candidate
        'one':  ['壹', '一'],
        'two':  ['贰', '二'],
        'thre': ['叁', '三'],
        'four': ['肆', '四'],
        'five': ['伍', '五'],
        'six':  ['陆', '六'],
        'seve': ['柒', '七'],
        'eigh': ['捌', '八'],
        'nine': ['玖', '九'],
        'ten':  ['拾', '十'],
        })
    cache = {}

    def __init__(self, filename=None):
        if filename:
            self.load_table(filename)
        self._post_init()

    def _post_init(self):
        self.selectors = {  # E.g. {"1": 0, "2": 1, ..., " ": 0}
            s: i % 10
            for i, s in enumerate(
                # Length is 11, ends with space
                '!@#$%^&*() ' if '1' in self.alphabet else '1234567890 '
            )}
        if self.wildcard in self.alphabet:
            raise ValueError('wildcard must not overlap some alphabet')
        if set(self.selectors) & self.alphabet:
            raise ValueError('selectors must not overlap some alphabet')

    def input(self, snippet):
        """Given the snippet which contains several codes plus one optional index,
        return {"snippet": normalized_snippet, "candidates": [], "result": "..."}

        This function does NOT maintain an internal buffer.
        On the contrary, it expects accumulated input from an external input field.

        >>> result = GreenInput().input("t")
        >>> result["snippet"]
        't'
        >>> set(result["candidates"]) == {'贰', '二', '叁', '三', '拾', '十'}
        True
        >>> result["result"]
        ''

        >>> result = GreenInput().input("tw")
        >>> result["snippet"]
        'tw'
        >>> set(result["candidates"]) == {'贰', '二'}
        True
        >>> result["result"]
        ''

        >>> result = GreenInput().input("twx")  # Invalid input should be discarded
        >>> result["snippet"]
        'tw'
        >>> set(result["candidates"]) == {'贰', '二'}
        True
        >>> result["result"]
        ''

        >>> GreenInput().input("tw1") == {
        ...     "snippet": "", "candidates": [], "result": '贰'}
        True

        >>> GreenInput().input("tw ") == {
        ...     "snippet": "", "candidates": [], "result": '贰'}
        True

        >>> GreenInput().input("tw2") == {
        ...     "snippet": "", "candidates": [], "result": '二'}
        True

        >>> GreenInput().input("2") == {
        ...     "snippet": "", "candidates": [], "result": '2'}
        True

        >>> GreenInput().input("") == {
        ...     "snippet": "", "candidates": [], "result": ''}
        True

        >>> result = GreenInput().input("four")
        >>> result["snippet"]
        'four'
        >>> set(result["candidates"]) == {'肆', '四'}
        True
        >>> result["result"]
        ''

        >>> GreenInput().input("zero") == {
        ...     "snippet": "", "candidates": [], "result": '零'}
        True

        >>> GreenInput().input("") == {
        ...     "snippet": "", "candidates": [], "result": ''}
        True
        """
        snippet = "".join(filter(
            lambda c: c in self.alphabet or c in self.selectors, snippet))
        if not snippet:  # This happens when the input area was cleaned by backspace
            return {"snippet": snippet, "candidates": [], "result": ""}
        code = "".join(filter(lambda c: c in self.alphabet, snippet))
        selector = snippet[-1] if snippet and snippet[-1] in self.selectors else None
        if not code:  # Then pass through the selector
            return {"snippet": "", "candidates": [], "result": selector or ""}
        assert code
        candidates = self.translate(code)
        if not candidates:  # Encounter invalid input
            valid = code[:-1]  # Discard last code because it doesn't match anything
            return {
                "snippet": valid,
                "candidates": self.translate(valid) if valid else [],
                "result": "",
                }
        if len(candidates) == 1 and len(code) == self.MaxCodes:
            return {"snippet": "", "candidates": [], "result": candidates[0]}
        if selector and self.selectors[selector] < len(candidates):  # returns chosen
            return {
                "snippet": "",
                "candidates": [],
                "result": candidates[self.selectors[selector]],
                }
        return {"snippet": code, "candidates": candidates, "result": ""}

    def translate(self, code, limit=10):  # @return a list containing candidates
        if code in self.cache:  # self.cache is expected to be pre-populated
            return self.cache[code]
        return self.codes.get(code, limit=limit)

    def load_table(self, filename, encoding="utf-8"):
        """Load code table in Windows 2000 format and change current instance.

        >>> grin = GreenInput()
        >>> grin.load_table("capnum.w2k")
        >>> grin.codename
        '大写数字'
        >>> grin.codes.get("wor")
        ['词组']
        >>> grin.save_json("capnum.test")  # Use a non-grn name, to avoid polluting publish

        The loaded grin2 contains a normal dict, rather than a defaultdict.
        So, the following test case would work only because we have a readonly mode.
        >>> grin2 = GreenInput()
        >>> grin2.load_json("capnum.test")
        >>> grin2.codename
        '大写数字'
        >>> grin2.codes.get("wor")
        ['词组']
        >>> grin2.codes.get("none")
        []
        """
        from configparser import ConfigParser
        import string
        if not filename:
            return
        definition = ConfigParser(allow_no_value=True, comment_prefixes=('/', '#'))
        definition.read(filename, encoding=encoding)  # Very slow on Brython
        self.MaxCodes = definition.getint('Description', 'MaxCodes')
        self.alphabet = set(definition.get('Description', 'UsedCodes'))
        self.wildcard = definition.get('Description', 'WildChar')
        self.codename = definition.get('Description', 'Name', fallback=filename)
        self.codes = Codes()
        for key, value in definition.items('Text'):
            # TODO: Show a stat for duplicate percentage for the given code table?
            hz = key.rstrip(string.printable)
            code = key[len(hz):]
            self.codes.add(code, [hz])
        self._post_init()
        self.cache = {  # Prepopulate the slowest yet most frequent snippets
            c: self.translate(c) for c in self.alphabet}

    def save_json(self, filename):
        with open(filename, "w") as f:
            json.dump({
                    "MaxCodes": self.MaxCodes,
                    "alphabet": sorted(list(self.alphabet)),  # stable output
                    "selectors": self.selectors,
                    "wildcard": self.wildcard,
                    "codename": self.codename,
                    "codes": self.codes._root,  # Note: It downgrades to a normal dict
                    "cache": self.cache,
                },
                f,
                separators=(',', ':'),  # Compact output
                sort_keys=True,  # It would probably help produce stable output
                )

    def load_json(self, filename):
        with open(filename) as f:
            cached = json.load(f)
            self.MaxCodes = cached["MaxCodes"]
            self.alphabet = set(cached["alphabet"])
            self.selectors = cached["selectors"]
            self.wildcard = cached["wildcard"]
            self.codename = cached["codename"]
            self.codes = Codes()
            self.codes._root = cached["codes"]  # Note: This is a normal dict
            self.cache = cached["cache"]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("Doctest passed")
    import sys
    if len(sys.argv) < 2:
        sys.exit("Usage: %s ime_name.w2k [ime_name.w2k.grn]" % sys.argv[0])
    GreenInput(sys.argv[1]).save_json(
        sys.argv[2] if len(sys.argv) >= 3 else sys.argv[1] + ".grn")

