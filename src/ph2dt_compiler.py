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


class ph2dtCompile(object):
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
    
    def configure_ph2dt(
        self,
        MEV_ph2dt=16000,
        MSTA_ph2dt=2400,
        MOBS_ph2dt=500,
        **kwargs
    ):
        self.ph2dt_inc_config = {
            "MEV": MEV_ph2dt,
            "MSTA": MSTA_ph2dt,
            "MOBS": MOBS_ph2dt,
        }

        self.msg(f"[msg] {str(self.ph2dt_inc_config)}")

        self.is_configured = True
    
    def create_ph2dt_inc_file(self):
        ph2dt_inc = """
      integer	MEV, MSTA, MOBS
      parameter(MEV=    {MEV},    
     &		MSTA=   {MSTA},		
     &		MOBS=   {MOBS})""".format(
            MEV=self.ph2dt_inc_config["MEV"],
            MSTA=self.ph2dt_inc_config["MSTA"],
            MOBS=self.ph2dt_inc_config["MOBS"]
        )
        
        ph2dt_inc = ph2dt_inc[1:]
        return ph2dt_inc

    def create_ph2dt_bat_file(self):
        compile_bat = f"""
@echo off

SET PATH=%PATH%;{CDIR}
SET CMD=ph2dt
SET CC="{CC}"
SET FC="{FC}"
""" + r"""
SET SRCS=%CMD% cluster datetime delaz ifindi indexx indexxi sorti trimlen
SET CSRCS=atoangle_ atoangle rpad_ sscanf3_
SET OBJS=%CMD%.o cluster.o datetime.o delaz.o ifindi.o indexx.o indexxi.o sorti.o trimlen.o atoangle_.o atoangle.o rpad_.o sscanf3_.o
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

    def compile_ph2dt(self):
        if self.is_configured == False:
            self.msg("[msg] please do the configuration using configure()")
        else:
            self.msg("[msg] create a configuration file")
            ph2dt_inc = self.create_ph2dt_inc_file()
            with open(os.path.join(HYPODD_INC_DIR, "ph2dt.inc"), 'w') as file:
                file.write(ph2dt_inc)
                file.close()
            
            self.msg("[msg] create a compiler batch file")
            compile_bat = self.create_ph2dt_bat_file()
            with open(os.path.join(PH2DT_DIR, "compile.bat"), 'w') as file:
                file.write(compile_bat)
                file.close()
            
            self.msg("[msg] remove old files in the ph2dt source folder")
            oldfiles = []
            for itype in ("*.o", "*.out", "*.exe", "*.fln"):
                oldfiles.extend(glob.glob(os.path.join(PH2DT_DIR,itype)))

            for oldfile in oldfiles:
                if os.path.isfile(oldfile) == True: os.remove(oldfile)
            
            self.msg("[msg] compiling a ph2dt program . . .")
            cmd = f"cmd.exe /C compile.bat"
            process = subprocess.Popen(cmd, cwd=PH2DT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')

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
                shutil.copy(os.path.join(PH2DT_DIR, "ph2dt.exe"), os.path.join(self.working_dir, "ph2dt.exe"))
            
            # self.msg("[msg] remove old files in the ph2dt source folder")
            # oldfiles = []
            # for itype in ("*.o", "*.out", "*.exe", "*.fln", "*.bat"):
            #     oldfiles.extend(glob.glob(os.path.join(PH2DT_DIR,itype)))

            # for oldfile in oldfiles:
            #     if os.path.isfile(oldfile) == True: os.remove(oldfile)
            
            if process.returncode == 0:
                self.msg('[msg] FINISHED . . .')
            else:
                self.msg('[msg] FAILED . . .')

if __name__ == '__main__':
    newph2dt = ph2dtCompile("temp_dir")
    newph2dt.configure_ph2dt()
    newph2dt.compile_ph2dt()
    
    





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