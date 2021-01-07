# coding: gb2312
from Tkinter import *
from Tix import *
import icelib.gui

class GreenInput(icelib.gui.Application):
  MaxCodes = 0 # 0��ʾ������
  UsedCodes='abcdefghijklmnopqrstuvwxyz'
  WildChar ='?'
  ChooseCodes=None  # �Զ��趨
  CodeTable = {}  # ��: { 'ni':['��', '��'], ... }
  charset = ''

  def aboutMsg(self): return '''GRIN(GReen INput), V1.0, iceberg@21cn.com, build@date 2006-10-27 22:48
    '''
    # @todo ֧�ֶ���10�������ֵķ�ҳ
    # @todo ֧�ֶ����뷨����������ͳ��
    # @todo ֧������
  def help(self): return unicode('''
        �����ɫ���뷨�����ʹ���ϲ����������ĸ������뷨������㣬
    ��������Ҫ���ڽ�������Լ�������ճ��������Ŀ�����֮�С�
        ����Ҫ����������֮��Ĳ�����ʹ�������ⰲװ����ĳ���ʹ�á�
    ��Ϊ����ɫ���뷨����Ҫ��Windowsϵͳ��ע���֮��д���κ����ݡ�
        ��������뷨����������ɱ����صķ����ض����������ļ�
    ָ��������������ֻҪ������ʵ�������Ϳ����ñ����뷨�����
    �������뷨�ı��뷽ʽ�����������롣����ʽ��ο������������
    ���ɸ�ʾ��*.txt��ʽ�ļ���
        ��Ҫ�ṩ�������뷨��������ʿ����ϵ iceberg@21cn.com ,
    ������д��������GRIN�������
    ''', 'gb2312')
  def __init__(self, master):
    icelib.gui.Application.__init__(self, master)
    self.initInput()  # ����ChooseCodes��ʼ������Ҫ�������ȵ��ô˷�����������������
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
    self.candidates['font'] = self.candidates['font'].split()[0] + ' 18'

    Label(parent, text="", anchor=W).pack(side=TOP, fill=X) # Separator

    Label(parent, text="Result (Select all, and press CTRL+C to copy, then CTRL+V to other software):", anchor=W).pack(side=TOP, fill=X)
    self.output = Text(parent, width=60, height=4)
    self.output.pack(fill=BOTH, expand=1)
    self.output['font'] = self.output['font'].split()[0] + ' 18'

    Button(parent, text='Reset', anchor=W, command=self.reset).pack(side=BOTTOM)

  def reset(self):
    self.output.delete('0.0', END)
    self.candidates.delete(0, END)
    self.code.delete(0, END)
  def dropLastKey(self):
    self.code.delete(len(self.code.get())-1)  # ɾ�����һ��������ַ�
  def inputCode(self, event=None):
    inputKey = event.char # ע�⵱�����ϵ��ַ��������ַ�ʱ�����ֵ��ͬ�� chr(event.keycode).lower()
    print "START: '%s'(%d), '%s', \"%s\"" % ( event.char, event.keycode, inputKey, self.code.get() )
    if event.keycode==8:  # backspace
      return
    if inputKey not in self.UsedCodes + self.ChooseCodes:
      return self.dropLastKey()
    if inputKey in self.ChooseCodes:
      order = self.ChooseCodes.index(inputKey) % 10 # So '1' and ' ' both point to the first candidate
      self.dropLastKey()
      result = self.__translate( self.code.get() )
      print 'DEBUG=',order, result, min( len(result)-1, order ), result and result[ min( len(result)-1, order ) ] or ''
      self.output.insert( INSERT, result and result[ min( len(result)-1, order ) ] or inputKey )
      self.candidates.delete(0, END)
      self.code.delete(0, END)
      return
    if inputKey in self.UsedCodes:
      result = self.__translate( self.code.get() )
      if len(result)==0:  # No matching
        return self.dropLastKey()
      elif len(result)==1 and self.isEndOfInput( self.code.get() ):
        self.output.insert( INSERT, result[0] )  # END�����'0.0'����ʼ��INSERT�ǵ�ǰ
        self.candidates.delete(0, END)
        self.code.delete(0, END)
      else:
        self.candidates.delete(0, END)
        for offset in range( 0, min(10, len(result)) ):
          self.candidates.insert(END, "%d:%s" % (offset+1, result[offset]) )
      return

  def isEndOfInput(self, code): # ȡ��������볤�������������˿ո�
    if self.MaxCodes: return len(code)>=self.MaxCodes
    else: return code.endswith(' ')

  def __translate(self, code):
    if not code: return []
    else:
      #print 'Before:', code
      result = self.translate(code.strip())
      #print 'After:', result
      return result
  def translate(self, code):  # @return a list containing candidates
    keys = [ key for key in self.CodeTable.keys() if key.startswith(code) ] # ����һ��Ҫ���������з���������keys���Ժ�Ĳ�������ǰ10����ɸѡ������ᶪʧ����������
    keys.sort() # �����ȼ�
    lists = [ self.CodeTable[key] for key in keys[:10] ] [:10]  # Ŀǰ��֧�ֶ���10����ѡ�ֵķ�ҳ
    return reduce( lambda x,y:x+y, lists, [] )  [:10]
  def _decode(self, x):
    try: return unicode( x, self.charset )
    except: return x

  def guiOutput(self, actionName, fileName, result):
    self.outputWindow.append( "%s %s: %s" % (actionName, fileName, result and result or 'successful') )


class InputTest(GreenInput):
  MaxCodes=4
  CodeTable={
    'one':  [u'Ҽ', u'һ'],
    'two':  [u'��', u'��'],
    'thre': [u'��', u'��'],
    'four': [u'��', u'��'],
    'five': [u'��', u'��'],
    'six':  [u'½', u'��'],
    'seve': [u'��', u'��'],
    'eigh': [u'��', u'��'],
    'nine': [u'��', u'��'],
    'ten':  [u'ʰ', u'ʮ'],
    'zero': [u'��']
    }
  def aboutMsg(self): return '''InputTest, iceberg@21cn.com, build@date 2006-10-15 11:37
    '''


class DecodeW2kCodeFile:
  def __init__(self, alldata, encoding='obsolete'):
    try: alldata = unicode(alldata, 'utf16')  # W2k Code file needs Unicode-decode ���ǣ��������ֻᱻת��Ϊ���ϡ�����
    except: pass  # �����κ�ת��
    self.lines = alldata.splitlines(True)
    self.offset = 0
  def readline(self, size=None): # ��ʵ���к���size����
    import string
    while self.offset < len(self.lines):
      line = self.lines[self.offset]
      self.offset = self.offset + 1
      #print 'Got:', line
      if line.startswith('//'): # comments
        continue
      elif '[' in line or '=' in line:  # valid for ConfigParser
        return line
      elif line.strip()=='': # ȥ������
        continue
      else:
        hz = line.rstrip( string.printable )
        code = line[len(hz):]
        if hz and code:
          return hz + '=' + code  # ע��: �����code=hz����������������������֮��Ŀǰ���ﲻ֧������ڳ���ͬһ�����֣��ʣ��в�ͬ��������롣
        else: print 'Unrecognised code start (%s/%s) at line #%d: %s' % (hz, code, self.offset, line)
    else: return ''

import cPickle
class OpenInput(GreenInput):
  encoding = 'utf16'
  CodeName = None
  codeFileDialogue = None
  def aboutMsg(self): return '''GReen INput(%s), iceberg@21cn.com, build@date 2006-10-15 11:37
    ''' % self.CodeName
  def popupFileSelectDialogue(self):
    self.codeFileDialogue.popup()
  def menuSpecs(self):  # ���ش˷���ʵ�ֲ˵��Ķ���
    return [  # Each item should be a (label_underscope, callback|subMenuList, [sequence])
      ("_File",
        [ ('_Load...', self.popupFileSelectDialogue), # ��Ҫ��һ����Ա��������װһ�£������ڴ˴�ִ��ʱ��self.codeFileDialogue��ΪNone������δ����popup()������
            # '<Control-o>'), # ��֪��Ϊʲô�����ﶨ���κο�ݼ����ᵼ�³����˳�
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
    if not self.codeFileDialogue:
      self.codeFileDialogue = ExFileSelectDialog(self, command=self.loadCodeTable)
      self.codeFileDialogue.fsbox.configure( filetypes=FileTypeList({'*.txt': 'Input Code Files'}) )
    if os.path.exists('cache.pkl'):
      print "Load from cache..."
      self.CodeName, self.MaxCodes, self.WildChar, self.UsedCodes, self.ChooseCodes, self.charset, self.CodeTable = cPickle.load(
        open('cache.pkl') )
    print self.MaxCodes, self.WildChar, self.UsedCodes, self.ChooseCodes  #, self.CodeTable
    print time.ctime()
  def loadCodeTable(self, event=None):
    filename = event  # Equals to: self.codeFileDialogue.fsbox.cget('value')
    import ConfigParser
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
  OpenInput.run()
  #InputBxm.run()
  #InputCapitalNumber.run()
  #InputTest.run()
