# coding: gb2312
from distutils.core import setup
import icelib.gui_setup

setup(
    cmdclass={'py2exe':icelib.gui_setup.myPy2Exe}, # 注：常规Py2exe不会自动把tix8184.dll和tcl/tix8.1目录包入，需事后手工copy。这个抄来的类可以解决这个问题。
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
