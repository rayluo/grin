# coding: gb2312
from Tkinter import *
from Tix import *
import os,time,types,sys

icon = os.path.splitext(sys.argv[0])[0] + '.ico'

def prepstr(s): # Copy from IDLE
    # Helper to extract the underscore from a string, e.g.
    # prepstr("Co_py") returns (2, "Copy").
    i = s.find('_')
    if i >= 0:
        s = s[:i] + s[i+1:]
    return i, s

class OutputWindow(ScrolledText):
  def __init__(self, parent, text=''): # I don't know what parameters is needed yet, I know few about Tck/Tk
    t = Toplevel(parent, takefocus=1) # Don't know how to make it wider
    if os.path.exists(icon): t.iconbitmap(icon)
    self.scrolledText = ScrolledText( t, options='text.width 50 text.height 30 wrap none font gb2312')
    self.scrolledText.pack(fill=BOTH)
    Button( t, text='Ok', command=t.destroy ).pack(side=BOTTOM)
    t.focus_force()
    if text: self.append(text)
  def append(self, text): # Don't know how to show Chinese
    if text:
      self.scrolledText.text.insert('insert', # VERY LUCKY TO GUESS THE "insert" KEYWORD... I hate the uncompleted Tkinter documents
        text + ( not text.endswith('\n') and '\n' or '' ) )
  def dummy(self): pass # for lambda

class Application(Frame):
  ProductName = '''GUI Base V1.2, iceberg@21cn.com, build@date 2006-10-27 22:53
      '''
    # V1.1 在菜单中应用了全局热键
    # V1.2 自动化的about信息
  outputWindow = None
  def genOutputWindow(self, text=''): # This works as a wrapper which within namespace of sub-classes
    return OutputWindow(self, text)
  def __init__(self, master):
    Frame.__init__(self, master)
    self.pack(fill=X)
    if master: master.config( menu = self.createMenu( self.menuSpecs() ) )  # Show menu
    self.createNotebookWidget()
    self.createMainWidget()

  def menuSpecs(self):  # 重载此方法实现菜单的定制
    return [  # Each item should be a (label_underscope, callback|subMenuList, [sequence])
      ("_File",
        [ ('', None),
          ('E_xit', self.quit, '<Alt-x>'),
        ] ),
      ("_Help", [
        ("_Help", lambda: self.genOutputWindow( self.help() ).dummy() ),  # OutputWindow(self, self.help()).dummy()  ),
        ("_About", lambda: self.createPopupDialog(self.about()) ),
        ('', None),
        ('_Debug', self.debug, '<Alt-d>'),
        ] ),
      ]
  def createMenu(self, menu_specs):
    menu = Tkinter.Menu(self, tearoff=0)
    for item in menu_specs:
      try: label, content, sequence = item
      except: label, content = item; sequence = None
      underline, label = prepstr(label)
      if not label:
        menu.add_separator()
      elif type(content) is types.ListType: # Recursive
        menu.add_cascade(label=label, underline=underline, menu=self.createMenu(content) )
      else:
        #print 'Menu:', label, sequence
        if sequence:
          menu.add_command(label=label, underline=underline, command=content, accelerator=sequence)
          self.bind_all(sequence, lambda event: content() )
        else:
          menu.add_command(label=label, underline=underline, command=content)
    return menu

  def createNotebookWidget(self): # NOTE: When using Notebook widget, the main menu lost hot-key control, nor even ALT-F4.
    tabs = [ getattr(self, m) for m in dir(self) if m.startswith('createTab') ] # Seems following an alphabet order
    if tabs:
      self.nb=NoteBook(self)
      self.nb.pack()
      for tab in tabs:
        tab()

  def createMainWidget(self): pass

  def createPopupDialog(self, text=''):
    t = Toplevel(self, takefocus=1)
    if os.path.exists(icon): t.iconbitmap(icon)
    Label( t, text=text).pack()
    Button( t, text='Ok', command=t.destroy ).pack(side=BOTTOM)
    t.focus_force() # This gets focus, but can not always keep it

  def debug(self):
    self.outputWindow = self.genOutputWindow('Hello')
    self.outputWindow.append('World')
  def help(self): return 'Help Message'
  def aboutMsg(self):
    return '''GUI Base V1.2, iceberg@21cn.com, build@date 2006-10-22 15:00
      '''
    # V1.1 在菜单中应用了全局热键
    # V1.2 自动化的about信息

  def about(self):  # 各子类设置自己的aboutMsg()成员方法即可。这个方法会自动递归引用。
    aboutMsg = self.aboutMsg() + '\n'
    parentName = self.__class__.__bases__ and self.__class__.__bases__[0].__name__ or ''
    parent = self.__class__.__bases__ and self.__class__.__bases__[0] or None
    while parent and parent.__name__ != 'Frame':
      aboutMsg = aboutMsg + '  based on: %s' % parent.aboutMsg(self)
      parent = parent.__bases__[0]
    return aboutMsg

  @classmethod
  def run(cls):
    root = Tk()
    app = cls(master=root)
    root.title(app.about())
    if os.path.exists(icon): root.iconbitmap(icon)
    root.protocol('WM_DELETE_WINDOW', root.quit)  # Otherwise, when closing window, will occur _tkinter.TclError: can't invoke "wm" command:  application has been destroyed
    app.mainloop()
    root.destroy()

if __name__ == '__main__':
  Application.run()
