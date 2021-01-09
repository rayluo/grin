# coding: gb2312
import logging
from Tkinter import *
from Tix import *
import icelib.gui

logger = logging.getLogger(__name__)

class GreenInput(icelib.gui.Application):
  MaxCodes = 0 # 0表示无限制
  UsedCodes='abcdefghijklmnopqrstuvwxyz'
  WildChar ='?'
  ChooseCodes=None  # 自动设定
  CodeTable = {}  # 例: { 'ni':['你', '妮'], ... }
  charset = ''

  def aboutMsg(self): return '''GRIN(GReen INput), V1.1, rayluo.mba@gmail.com, build@date 2020-1-7
    '''
    # @todo 支持多于10个重码字的翻页
    # @todo 支持对输入法的重码率作统计
    # @todo 支持联想
    # V1.1 Refactor so that it can run on Python 2.7
  def help(self): return unicode('''
        这个绿色输入法软件在使用上并不如主流的各种输入法软件方便，
    它甚至需要你在结果窗口自己把内容粘贴到其它目标软件之中。
        它主要用于在网吧之类的不允许使用者随意安装软件的场合使用。
    因为本绿色输入法不需要往Windows系统及注册表之中写入任何内容。
        具体的输入法编码规则，是由被加载的符合特定规则的码表文件
    指定。所以理论上只要能配合适当的码表，就可以用本输入法软件按
    任意输入法的编码方式进入文字输入。码表格式请参考本软件附带的
    若干个示范*.txt格式文件。
        需要提供或交流输入法或码表的人士可联系 iceberg@21cn.com ,
    主题请写明《关于GRIN的码表》。
    ''', 'gb2312')
  def __init__(self, master):
    icelib.gui.Application.__init__(self, master)
    self.initInput()  # 由于ChooseCodes初始化的需要，决定先调用此方法再做下列整理工作
    self.postInitInput()
  def initInput(self):
    pass
  def postInitInput(self):
    self.ChooseCodes = '1' in self.UsedCodes and '!@#$%^&*() ' or '1234567890 ' # Ends with space
    assert self.WildChar not in self.UsedCodes, 'WildChar overlaps some UsedCodes'
    assert not [ c for c in self.ChooseCodes if c in self.UsedCodes ], 'ChooseCodes overlaps some UsedCodes'
    self.master.title(self.about())
  def createMainWidget(self):
    parent = self

    Label(parent, text="Input your code here:", anchor=W).pack(side=TOP, fill=X)
    self.code = Entry(parent)
    self.code.pack(fill=X)
    self.code.focus_set()
    self.code.bind('<KeyRelease>', self.inputCode)

    Label(parent, text="", anchor=W).pack(side=TOP, fill=X) # Separator

    Label(parent, text="Candidates:", anchor=W).pack(side=TOP, fill=X)
    self.candidates = Listbox(parent)
    self.candidates.pack(expand=1, fill=BOTH)
    try: self.candidates['font'] = self.candidates['font'].split()[0] + ' 18'
    except: pass # Happens in python2.5

    Label(parent, text="", anchor=W).pack(side=TOP, fill=X) # Separator

    Label(parent, text="Result (Select all, and press CTRL+C to copy, then CTRL+V to other software):", anchor=W).pack(side=TOP, fill=X)
    self.output = Text(parent, width=60, height=4)
    self.output.pack(fill=BOTH, expand=1)
    try: self.output['font'] = self.output['font'].split()[0] + ' 18'
    except: pass # Happens in python2.5

    Button(parent, text='Reset', anchor=W, command=self.reset).pack(side=BOTTOM)

  def reset(self):
    self.output.delete('0.0', END)
    self.candidates.delete(0, END)
    self.code.delete(0, END)
  def dropLastKey(self):
    self.code.delete(len(self.code.get())-1)  # 删除最后一个输入的字符
  def inputCode(self, event=None):
    logger.debug("INPUT: char='%s', keycode=%d, code.get()='%s'",
        event.char,  # In Python 2.4/2.5 era, input of "!@#$..." would
                    # result in a char different than chr(event.keycode).lower()
                    # In Python 2.7, this seems to be always an empty string
        event.keycode,  # Something relevant to the key's physical position on keyboard
        self.code.get(),  # This seems to contain all inputed keys, tested in Python 2.7 on Linux
            # Known issue: Tkinter widget is too slow to recognize a quick "1234"
            #   as four separated keys, it would return one 4-letter string.
        )
    inputKey = self.code.get()[-1] if self.code.get() else None
    if not inputKey:  # This happens when the input area was cleaned by backspace
        self.candidates.delete(0, END)
        return
    if inputKey not in self.UsedCodes + self.ChooseCodes:
      return self.dropLastKey()
    if inputKey in self.ChooseCodes:
      order = self.ChooseCodes.index(inputKey) % 10 # So '1' and ' ' both point to the first candidate
      self.dropLastKey()
      result = self.__translate( self.code.get() )
      position = min(len(result)-1, order)
      logger.debug('FOUND: %s[%d] = %s', result, position, result[position] if result else '')
      self.output.insert(
            INSERT,
            result[position] if result
                else inputKey,  # This would allow inputting numeric keys
            )
      self.candidates.delete(0, END)
      self.code.delete(0, END)
      return
    if inputKey in self.UsedCodes:
      result = self.__translate( self.code.get() )
      if len(result)==0:  # No matching
        return self.dropLastKey()
      elif len(result)==1 and self.isEndOfInput( self.code.get() ):
        self.output.insert( INSERT, result[0] )  # END是最后，'0.0'是起始，INSERT是当前
        self.candidates.delete(0, END)
        self.code.delete(0, END)
      else:
        self.candidates.delete(0, END)
        for offset in range( 0, min(10, len(result)) ):
          self.candidates.insert(END, "%d:%s" % (offset+1, result[offset]) )
      return

  def isEndOfInput(self, code):
    return code.endswith(' ') or len(code) >= self.MaxCodes

  def __translate(self, code):
    if not code: return []
    else:
      #print 'Before:', code
      result = self.translate(code.strip())
      #print 'After:', result
      return result
  def translate(self, code):  # @return a list containing candidates
    keys = [ key for key in self.CodeTable.keys() if key.startswith(code) ] # 这里一定要遍历了所有符合条件的keys，以后的步骤再做前10个的筛选，否则会丢失部分重码字
    keys.sort() # 简码先见
    lists = [ self.CodeTable[key] for key in keys[:10] ] [:10]  # 目前不支持多于10个候选字的翻页
    return reduce( lambda x,y:x+y, lists, [] )  [:10]
  def _decode(self, x):
    try: return unicode( x, self.charset )
    except: return x

  def guiOutput(self, actionName, fileName, result):
    self.outputWindow.append( "%s %s: %s" % (actionName, fileName, result and result or 'successful') )


class InputTest(GreenInput):
  MaxCodes=4
  CodeTable={
    'one':  [u'壹', u'一'],
    'two':  [u'贰', u'二'],
    'thre': [u'叁', u'三'],
    'four': [u'肆', u'四'],
    'five': [u'伍', u'五'],
    'six':  [u'陆', u'六'],
    'seve': [u'柒', u'七'],
    'eigh': [u'捌', u'八'],
    'nine': [u'玖', u'九'],
    'ten':  [u'拾', u'十'],
    'zero': [u'零']
    }
  def aboutMsg(self): return '''InputTest, iceberg@21cn.com, build@date 2006-10-15 11:37
    '''


class DecodeW2kCodeFile:
  def __init__(self, alldata, encoding='obsolete'):
    try: alldata = unicode(alldata, 'utf16')  # W2k Code file needs Unicode-decode 但是，“不”字会被转换为“上”？！
    except: pass  # 不作任何转换
    self.lines = alldata.splitlines(True)
    self.offset = 0
  def readline(self, size=None): # 本实现中忽略size参数
    import string
    while self.offset < len(self.lines):
      line = self.lines[self.offset]
      self.offset = self.offset + 1
      #print 'Got:', line
      if line.startswith('//'): # comments
        continue
      elif '[' in line or '=' in line:  # valid for ConfigParser
        return line
      elif line.strip()=='': # 去除空行
        continue
      else:
        hz = line.rstrip( string.printable )
        code = line[len(hz):]
        if hz and code:
          return hz + '=' + code  # 注意: 如果是code=hz，则处理不了重码的情况。换言之，目前这里不支持码表内出现同一个汉字（词）有不同的输入编码。
        else: print 'Unrecognised code start (%s/%s) at line #%d: %s' % (hz, code, self.offset, line)
    else: return ''

import cPickle
class OpenInput(GreenInput):
  encoding = 'utf16'
  CodeName = None

  def aboutMsg(self): return '''GReen INput(%s), V1.1, rayluo.mba@gmail.com, build@date 2020-1-8
    ''' % self.CodeName
        # V1.1 Replace undocumented(?) and now broken ExFileSelectDialog()

  def menuSpecs(self):
    return [  # Each item should be a (label_underscope, callback|subMenuList, [sequence])
      ("_File",
        [ ('_Load...', self.loadCodeTable),
            # '<Control-o>'),  # Somehow, hotkey here would cause program abort
          ('', None),
          ('E_xit', self.quit, '<Alt-x>'),
        ] ),
      ("_Help", [
        ("_Help", lambda: self.genOutputWindow( self.help() ).dummy() ),  # OutputWindow(self, self.help()).dummy()  ),
        ("_About", lambda: self.createPopupDialog(self.about()) ),
        ('', None),
        ('_Debug', self.debug, '<Alt-d>'),
        ] ),
      ]

  def initInput(self):
    GreenInput.initInput(self)
    import time, os
    print time.ctime()
    if os.path.exists('cache.pkl'):
      print "Load from cache..."
      self.CodeName, self.MaxCodes, self.WildChar, self.UsedCodes, self.ChooseCodes, self.charset, self.CodeTable = cPickle.load(
        open('cache.pkl') )
    print self.MaxCodes, self.WildChar, self.UsedCodes, self.ChooseCodes  #, self.CodeTable
    print time.ctime()
  def loadCodeTable(self):
    import ConfigParser
    from tkFileDialog import askopenfilename
        # The previous ExFileSelectDialog() from Python 2.4/2.5 no longer works
    filename = askopenfilename(filetypes=[
        ("Input Code files", (".txt",)),
        ("All files", ".*"),
        ])
    if not filename:
        return
    codeFile = ConfigParser.SafeConfigParser()
    codeFile.readfp( DecodeW2kCodeFile( open(filename,'rU').read(), self.encoding ) )
    self.MaxCodes = codeFile.getint('Description', 'MaxCodes')
    self.UsedCodes = codeFile.get('Description', 'UsedCodes')
    self.WildChar = codeFile.get('Description', 'WildChar')
    try: self.charset = codeFile.get('Description', 'Charset')
    except: self.charset = ''
    try: self.CodeName = self._decode( codeFile.get('Description', 'Name') )
    except: self.CodeName = filename
    self.CodeTable = {}
    for hz, code in codeFile.items('Text'):
      if self.CodeTable.get(code) is None: self.CodeTable[code]=[]
      self.CodeTable[code].append( self._decode(hz) )
    self.postInitInput()
    cPickle.dump( ( self.CodeName, self.MaxCodes, self.WildChar, self.UsedCodes, self.ChooseCodes, self.charset, self.CodeTable ),
      open('cache.pkl','w') )

class InputCapitalNumber(OpenInput):
  CodeName = 'capnum.txt'

class InputBxm(OpenInput):
  encoding = ''
  CodeName = 'winbxm.txt'
  charset = 'gb2312'

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  #icelib.gui.Application.run()  # This can test GUI with icon
  #GreenInput.run()  # This starts a scaffold GRIN instance
  #InputTest.run()  # This starts the built-in demo
  OpenInput.run()
  #InputBxm.run()
  #InputCapitalNumber.run()
