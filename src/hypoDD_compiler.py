"""
author: Yudha Styawan
email: yudhastyawan26@gmail.com

this code has been inspired by hypoDDpy, see their github for more details
"""

import subprocess
import glob
import os
import shutil
from pathlib import Path

FILE_DIR = os.path.dirname(__file__)
if not os.path.isdir(os.path.join(FILE_DIR,"hypoDD")):
    FILE_DIR = Path(os.path.dirname(__file__)).parent
BIN_DIR = os.path.join(FILE_DIR, "bin")
HYPODD_PROG_DIR = os.path.join(FILE_DIR, "hypoDD")
HYPODD_INC_DIR = os.path.join(FILE_DIR, "hypoDD", "include")
HYPODD_DIR = os.path.join(HYPODD_PROG_DIR, "src", "hypoDD")
PH2DT_DIR = os.path.join(HYPODD_PROG_DIR, "src", "ph2dt")
CDIR = os.path.join(FILE_DIR, "mingw64", "bin")
FC = os.path.join(CDIR, "gfortran.exe")
CC = os.path.join(CDIR, "gcc.exe")


class hypoDDCompile(object):
    def __init__(self, working_dir = BIN_DIR, stdout_function = print, stderr_function = print, msg_function = print):
        self.stdout = stdout_function
        self.stderr = stderr_function
        self.msg = msg_function
        self.working_dir = working_dir
        if not os.path.exists(self.working_dir): 
            self.msg(f"[msg] {self.working_dir} is not exist, it will be created by this program.")
            os.makedirs(working_dir)
        else:
            self.msg(f"[msg] {self.working_dir} has been exist, the contaning files will be overwrited.")
        self.is_configured = False
    
    def configure_hypodd(
        self,
        MAXEVE=3000,
        MAXDATA=2800000,
        MAXEVE0=50,
        MAXDATA0=60000,
        MAXLAY=30,
        MAXSTA=2000,
        MAXCL=200,
        **kwargs
    ):
        self.hypodd_inc_config = {
            "MAXEVE": MAXEVE,
            "MAXDATA": MAXDATA,
            "MAXEVE0": MAXEVE0,
            "MAXDATA0": MAXDATA0,
            "MAXLAY": MAXLAY,
            "MAXSTA": MAXSTA,
            "MAXCL": MAXCL,
        }

        self.msg(f"[msg] {str(self.hypodd_inc_config)}")

        self.is_configured = True
    
    def create_hypoDD_inc_file(self):
        hypoDD_inc = """
      integer*4 MAXEVE, MAXLAY, MAXDATA, MAXSTA, MAXEVE0, MAXDATA0
      integer*4 MAXCL
      parameter(MAXEVE   = {MAXEVE},
     &          MAXDATA  = {MAXDATA},
     &          MAXEVE0  = {MAXEVE0},
     &          MAXDATA0 = {MAXDATA0},
     &          MAXLAY   = {MAXLAY},
     &          MAXSTA   = {MAXSTA},
     &          MAXCL    = {MAXCL})""".format(
            MAXEVE=self.hypodd_inc_config["MAXEVE"],
            MAXDATA=self.hypodd_inc_config["MAXDATA"],
            MAXEVE0=self.hypodd_inc_config["MAXEVE0"],
            MAXDATA0=self.hypodd_inc_config["MAXDATA0"],
            MAXLAY=self.hypodd_inc_config["MAXLAY"],
            MAXSTA=self.hypodd_inc_config["MAXSTA"],
            MAXCL=self.hypodd_inc_config["MAXCL"],
        )
        
        hypoDD_inc = hypoDD_inc[1:]
        return hypoDD_inc

    def create_hypoDD_bat_file(self):
        compile_bat = f"""
@echo off

SET PATH=%PATH%;{CDIR}
SET CMD=hypoDD
SET CC="{CC}"
SET FC="{FC}"
""" + r"""
SET SRCS=%CMD% aprod cluster1 covar datum delaz delaz2 direct1 dist dtres exist freeunit getdata getinp ifindi indexxi juliam lsfit_lsqr lsfit_svd lsqr matmult1 matmult2 matmult3 mdian1 normlz partials ran redist refract resstat scopy sdc2 setorg skip snrm2 sort sorti sscal svd tiddid trialsrc trimlen ttime vmodel weighting
SET CSRCS=atoangle_ atoangle datetime_ hypot_ rpad_ sscanf3_
SET OBJS=%CMD%.o aprod.o cluster1.o covar.o datum.o delaz.o delaz2.o direct1.o dist.o dtres.o exist.o freeunit.o getdata.o getinp.o ifindi.o indexxi.o juliam.o lsfit_lsqr.o lsfit_svd.o lsqr.o matmult1.o matmult2.o matmult3.o mdian1.o normlz.o partials.o ran.o redist.o refract.o resstat.o scopy.o sdc2.o setorg.o skip.o snrm2.o sort.o sorti.o sscal.o svd.o tiddid.o trialsrc.o trimlen.o ttime.o vmodel.o weighting.o atoangle_.o atoangle.o datetime_.o hypot_.o rpad_.o sscanf3_.o
SET INCLDIR=..\..\include
SET CFLAGS=-O -I%INCLDIR%
SET FFLAGS=-I%INCLDIR%

FOR %%A in (%SRCS%) do (
echo %FC% %FFLAGS% -c %%A.f -o %%A.o
%FC% %FFLAGS% -c %%A.f -o %%A.o
)

FOR %%A in (%CSRCS%) do (
echo %CC% %CFLAGS% -c %%A.c -o %%A.o
%CC% %CFLAGS% -c %%A.c -o %%A.o
)

echo %FC% %OBJS% -o %CMD%.exe
%FC% %OBJS% -o %CMD%.exe
        """
        compile_bat = compile_bat[1:]
        return compile_bat

    def compile_hypodd(self):
        if self.is_configured == False:
            self.msg("[msg] please do the configuration using configure()")
        else:
            self.msg("[msg] create a configuration file")
            hypoDD_inc = self.create_hypoDD_inc_file()
            with open(os.path.join(HYPODD_INC_DIR, "hypoDD.inc"), 'w') as file:
                file.write(hypoDD_inc)
                file.close()
            
            self.msg("[msg] create a compiler batch file")
            compile_bat = self.create_hypoDD_bat_file()
            with open(os.path.join(HYPODD_DIR, "compile.bat"), 'w') as file:
                file.write(compile_bat)
                file.close()
            
            self.msg("[msg] remove old files in the hypoDD source folder")
            oldfiles = []
            for itype in ("*.o", "*.out", "*.exe", "*.fln"):
                oldfiles.extend(glob.glob(os.path.join(HYPODD_DIR,itype)))

            for oldfile in oldfiles:
                if os.path.isfile(oldfile) == True: os.remove(oldfile)
            
            self.msg("[msg] compiling a hypoDD program . . .")
            cmd = f"cd {HYPODD_DIR} && .\compile.bat"
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')

            while True:
                out = process.stdout.readline()
                err = process.stderr.readline()
                if (out == '' or err == '') and process.poll() is not None:
                    break
                if out != '':
                    self.stdout(f'[stdout] {out.strip()}')
                if err != '':
                    self.stderr(f'{err.strip()}')
            self.msg(f'[msg] EXIT CODE: {process.returncode}')

            if process.returncode == 0:
                self.msg('[msg] copying files to the target directory')
                shutil.copy(os.path.join(HYPODD_DIR, "hypoDD.exe"), os.path.join(self.working_dir, "hypoDD.exe"))
            
            self.msg("[msg] remove old files in the hypoDD source folder")
            oldfiles = []
            for itype in ("*.o", "*.out", "*.exe", "*.fln", "*.bat"):
                oldfiles.extend(glob.glob(os.path.join(HYPODD_DIR,itype)))

            for oldfile in oldfiles:
                if os.path.isfile(oldfile) == True: os.remove(oldfile)
            
            if process.returncode == 0:
                self.msg('[msg] FINISHED . . .')
            else:
                self.msg('[msg] FAILED . . .')

if __name__ == '__main__':
    newHypoDD = hypoDDCompile("temp_dir")
    newHypoDD.configure_hypodd()
    newHypoDD.compile_hypodd()
    
    





# oldfiles = []
# for itype in ("*.o", "*.out", "*.exe", "*.fln"):
#     oldfiles.extend(glob.glob(os.path.join(r"C:\Users\Lenovo\Documents\projects\hypoDD\src\hypoDD",itype)))

# for oldfile in oldfiles:
#     if os.path.isfile(oldfile) == True: os.remove(oldfile)

# cmd = r"cd C:\Users\Lenovo\Documents\projects\hypoDD\src\hypoDD && .\compile.bat"
# process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')

# while True:
#     out = process.stdout.readline()
#     if out == '' and process.poll() is not None:
#         break
#     if out != '':
#         print(out.strip(), flush=True)
# print('EXIT: ', process.returncode)