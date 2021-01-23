# coding: utf-8
import logging
from functools import reduce


__version__ = "2.0.0"
logger = logging.getLogger(__name__)


class GreenInput(object):
    """GRIN(GReen INput)

        这个绿色输入法软件在使用上并不如主流的各种输入法软件方便，
    它甚至需要你在结果窗口自己把内容粘贴到其它目标软件之中。
        它主要用于在网吧之类的不允许使用者随意安装软件的场合使用。
    因为本绿色输入法不需要往Windows系统及注册表之中写入任何内容。
        具体的输入法编码规则，是由被加载的符合特定规则的码表文件
    指定。所以理论上只要能配合适当的码表，就可以用本输入法软件按
    任意输入法的编码方式进入文字输入。码表格式请参考本软件附带的
    若干个示范*.txt格式文件。
        需要提供或交流输入法或码表的人士可联系 rayluo.mba@gmail.com ,
    主题请写明《关于GRIN的码表》。

    rayluo.mba@gmail.com 2021
    """
    MaxCodes = 4  # None means unlimited
    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    wildcard = '?'
    codename = "Test Input"
    CodeTable = {  # Words in Unicode. Example: { 'ni':[u'你', u'妮'], ... }
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
        }

    def __init__(self, filename=None):
        if filename:
            self.load_table(filename)
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
        logger.debug("INPUT: snippet='%s'", snippet)
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
        keys = [  # Find all candidates first, before subsequent filtering
            key for key in self.CodeTable.keys() if key.startswith(code)]
        keys.sort()  # Simple code shall be showed at the top (a.k.a. 简码先见)
        lists = [self.CodeTable[key] for key in keys[:limit]][:limit]
        return reduce(lambda x,y:x+y, lists, [])[:limit]  # Flatten them

    def _decode(self, x, charset):
        try: return unicode(x, charset)
        except: return x

    def load_table(self, filename):
        import ConfigParser
        codeFile = ConfigParser.SafeConfigParser()
        default_charset = "utf16"
        codeFile.readfp(DecodeW2kCodeFile(
            open(filename,'rU').read(),
            encoding=default_charset,  # NOTE:
                # Historically, UTF16 is good enough to read metadata from GB18030 input,
                # but UTF16BOM is also observed to incorrectly convert "不" to "上".
                # Ideally we should know encoding beforehand and they better be UTF8.
            ))
        self.MaxCodes = codeFile.getint('Description', 'MaxCodes')
        self.alphabet = codeFile.get('Description', 'UsedCodes')
        self.wildcard = codeFile.get('Description', 'WildChar')
        try: charset = codeFile.get('Description', 'Charset')
        except: charset = default_charset
        try: self.codename = self._decode(codeFile.get('Description', 'Name'), charset)
        except: self.codename = filename
        self.CodeTable = {}
        for hz, code in codeFile.items('Text'):
          # TODO: Show a stat for duplicate percentage for the given code table?
          if self.CodeTable.get(code) is None: self.CodeTable[code]=[]
          self.CodeTable[code].append(self._decode(hz, charset))
        self.postInitInput()
        cPickle.dump(
            (self.codename, self.MaxCodes, self.wildcard, self.alphabet, self.selectors, self.CodeTable),
            open('cache.pkl','w'))


class DecodeW2kCodeFile:  # It maps W2kCodeFile format to ConfigParser format
  def __init__(self, alldata, encoding='utf8'):
    try: alldata = unicode(alldata, encoding)  # W2k Code file needs Unicode-decode
    except: logger.exception("Ignore %s decode error", encoding)
    self.lines = alldata.splitlines(True)
    self.offset = 0

  def readline(self, size=None):  # This implementation ignores size parameter
    import string
    while self.offset < len(self.lines):
      line = self.lines[self.offset]
      self.offset = self.offset + 1
      #print 'Got:', line
      if line.startswith('//'): # comments
        continue
      elif '[' in line or '=' in line:  # valid for ConfigParser
        return line
      elif line.strip()=='':  # Skip blank line
        continue
      else:
        hz = line.rstrip( string.printable )
        code = line[len(hz):]
        if hz and code:
          return hz + '=' + code  # This maps to a key-value pair.
            # Cannot use "code=hz", b/c it won't handle one-code-multiple-word (重码)
            # By go with "hz=code", we choose to not support one-word-multiple-code
            # (i.e.  目前这里不支持码表内出现同一个汉字（词）有不同的输入编码)
        else:
            logger.warn(
                'Unrecognised code start (%s/%s) at line #%d: %s',
                hz, code, self.offset, line)
    else: return ''


if __name__ == "__main__":
    import doctest
    doctest.testmod()

