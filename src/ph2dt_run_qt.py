"""
author: Yudha Styawan
email: yudhastyawan26@gmail.com

this code has been inspired by hypoDDpy, see their github for more details
"""

import subprocess
import sys
import glob
import os
import shutil
from pathlib import Path

FILE_DIR = os.path.dirname(__file__)
if not os.path.isdir(os.path.join(FILE_DIR,"hypoDD")):
    FILE_DIR = Path(os.path.dirname(__file__)).parent
BIN_DIR = os.path.join(FILE_DIR, "bin")
CDIR = os.path.join(FILE_DIR, "mingw64", "bin")

class ph2dtRun(object):
    def __init__(self, working_dir = BIN_DIR, stdout_function = print, stderr_function = print, msg_function = print):
        self.stdout = stdout_function
        self.stderr = stderr_function
        self.msg = msg_function
        self.working_dir = working_dir
        if not os.path.exists(self.working_dir): 
            self.msg(f"[msg] {self.working_dir} is not exist.")
        else:
            self.msg(f"[msg] {self.working_dir} has been exist, the contaning files will be overwrited.")
        self.is_configured = False
        self.is_exists = False
    
    def configure_ph2dt(self,
        MINWGHT_ph2dt = 0,
        MAXDIST_ph2dt = 500,
        MAXSEP_ph2dt = 10,
        MAXNGH_ph2dt = 10,
        MINLNK_ph2dt = 8,
        MINOBS_ph2dt = 8,
        MAXOBS_ph2dt = 50, 
        station_dat_ph2dt = 'station.dat', 
        phase_dat_ph2dt = 'phase.dat',
        **kwargs
        ):

        self.ph2dt_inp_config = {
            "MINWGHT": MINWGHT_ph2dt,
            "MAXDIST": MAXDIST_ph2dt,
            "MAXSEP": MAXSEP_ph2dt,
            "MAXNGH": MAXNGH_ph2dt,
            "MINLNK": MINLNK_ph2dt,
            "MINOBS": MINOBS_ph2dt, 
            "MAXOBS": MAXOBS_ph2dt,
            "station_dat": station_dat_ph2dt,
            "phase_dat": phase_dat_ph2dt
        }

        self.msg(f"[msg] {str(self.ph2dt_inp_config)}")

        self.is_configured = True

    
    def create_ph2dt_inp_file(self):
        ph2dt_inp = "\n".join([
            "{station_dat}",
            "{phase_dat}",
            "{MINWGHT} {MAXDIST} {MAXSEP} {MAXNGH} {MINLNK} {MINOBS} {MAXOBS}"
        ])

        ph2dt_inp = ph2dt_inp.format(**self.ph2dt_inp_config)
        return ph2dt_inp
    
    def run_ph2dt(self):
        if self.is_configured == False:
            self.msg("[msg] please do the configuration using configure()")
        else:
            self.msg("[msg] create an input file")
            ph2dt_inp = self.create_ph2dt_inp_file()
            with open(os.path.join(self.working_dir, "ph2dt.inp"), 'w') as file:
                file.write(ph2dt_inp)
                file.close()
            
            self.msg("[msg] create a batch file")
            compile_bat = "\n".join([
                "@echo off",
                f"SET PATH=%PATH%;{CDIR}",
                ".\ph2dt.exe ph2dt.inp"
            ])
            with open(os.path.join(self.working_dir, "ph2dt.bat"), 'w') as file:
                file.write(compile_bat)
                file.close()
        
            self.msg("[msg] running a ph2dt program . . .")
            shutil.copy(os.path.join(BIN_DIR, "ph2dt.exe"), os.path.join(self.working_dir, "ph2dt.exe"))
            cmd = f"cd {self.working_dir} && .\ph2dt.bat"
            cmd = os.path.join(self.working_dir, "ph2dt.bat")
        return cmd
            # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')

            # while True:
            #     out = process.stdout.readline()
            #     err = process.stderr.readline()
            #     if (out == '' or err == '') and process.poll() is not None:
            #         break
            #     if out != '':
            #         self.stdout(f'[stdout] {out.strip()}')
            #     if err != '':
            #         self.stderr(f'{err.strip()}')
            # self.msg(f'[msg] EXIT CODE: {process.returncode}')
            # # print(process.communicate()[0])

            # self.msg("[msg] remove ph2dt.exe")
            # oldfiles = []
            # for itype in ("*.o", "*.out", "*.exe", "*.fln"):
            #     oldfiles.extend(glob.glob(os.path.join(self.working_dir,itype)))

            # for oldfile in oldfiles:
            #     if os.path.isfile(oldfile) == True: os.remove(oldfile)
            
            # if process.returncode == 0:
            #     self.msg('[msg] FINISHED . . .')
            # else:
            #     self.msg('[msg] FAILED . . .')

if __name__ == '__main__':
    newph2dt = ph2dtRun(r"C:\Users\Lenovo\Documents\projects\hypoDD\examples\mytest1-res2")
    newph2dt.configure_ph2dt()
    newph2dt.run_ph2dt()