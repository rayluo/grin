# coding: gb2312
from distutils.core import setup
import icelib.gui_setup

setup(
    cmdclass={'py2exe':icelib.gui_setup.myPy2Exe}, # ע������Py2exe�����Զ���tix8184.dll��tcl/tix8.1Ŀ¼���룬���º��ֹ�copy���������������Խ��������⡣
    #options = { 'py2exe': { 'packages': 'encodings' } },
    windows=[
      { "script":'grin.py',
        #"bitmap_resources": [(1, "grin.jpg")],
        "icon_resources": [(1, "grin.ico")],
      } ],
    data_files = [ ("", [
        'grin.ico',
        'capnum.txt',
        #'winbxmcz.txt',
        'winbxm.txt',
        ] )
      ],
)
