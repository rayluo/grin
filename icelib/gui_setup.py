# coding: gb2312

from distutils.core import setup
import py2exe
from py2exe.build_exe import py2exe as BuildExe
import os,sys

def TixInfo():
    import Tkinter
    import _tkinter

    tk=_tkinter.create()

    tcl_version=_tkinter.TCL_VERSION
    tk_version=_tkinter.TK_VERSION
    tix_version=tk.call("package","version","Tix")

    tcl_dir=tk.call("info","library")

    del tk, _tkinter, Tkinter

    return (tcl_version,tk_version,tix_version,tcl_dir)

class myPy2Exe(BuildExe): # from  http://www.py2exe.org/index.cgi/TixSetup

    def plat_finalize(self, modules, py_files, extensions, dlls):
        BuildExe.plat_finalize(self, modules, py_files, extensions, dlls)

        if "Tix" in modules:
            # Tix adjustments
            tcl_version,tk_version,tix_version,tcl_dir = TixInfo()

            tixdll="tix%s%s.dll"% (tix_version.replace(".",""),
                                    tcl_version.replace(".",""))
            tcldll="tcl%s.dll"%tcl_version.replace(".","")
            tkdll="tk%s.dll"%tk_version.replace(".","")

            dlls.add(os.path.join(sys.prefix,"DLLs",tixdll))

            self.dlls_in_exedir.extend( [tcldll,tkdll,tixdll ] )

            tcl_src_dir = os.path.split(tcl_dir)[0]
            tcl_dst_dir = os.path.join(self.lib_dir, "tcl")
            self.announce("Copying TIX files from %s..." % tcl_src_dir)
            self.copy_tree(os.path.join(tcl_src_dir, "tix%s" % tix_version),
                           os.path.join(tcl_dst_dir, "tix%s" % tix_version))

if __name__=='__main__':
  setup(
      ## The following two options are for an autorun
      script_args=['py2exe'],
      options={'py2exe':{
            #'bundle_files':1,
            'compressed':1
        }
      },

      cmdclass={'py2exe':myPy2Exe}, # 注：常规Py2exe不会自动把tix8184.dll和tcl/tix8.1目录包入，需事后手工copy。这个抄来的类可以解决这个问题。
  #    windows=['gui.py'],
  )
