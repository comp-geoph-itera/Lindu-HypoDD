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

class hypoDDrelocate(object):
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
    
    def configure_hypodd(self,
        IDAT = 2,
        IPHA = 1,
        DIST = 200,
        OBSCC = 0,
        OBSCT = 8,
        ISTART = 2,
        ISOLV = 1,
        NSET = 2,
        RATIO = 1.75,
        TOP = [0.0, 1.0, 3.0, 6.0, 14.0, 25.0],
        VEL = [3.77, 4.64, 5.34, 5.75, 6.22, 7.98],
        DATA_WEIGHTING_AND_REWEIGHTING = [[4, 1, 0.5, -9, -9, 0.01, -9, -9, -9, 20],
                                          [4, 1, 0.5, 5, 3, 0.01, -9, 5, 10, 20]],
        CID = 0,
        ID = "",
        dt_cc = 'dt.cc', 
        dt_ct = 'dt.ct', 
        event_sel = 'event.sel', 
        station_dat = 'station.dat', 
        hypoDD_loc = 'hypoDD.loc', 
        hypoDD_reloc = 'hypoDD.reloc', 
        hypoDD_sta = 'hypoDD.sta', 
        hypoDD_res = 'hypoDD.res', 
        hypoDD_src = 'hypoDD.src',
        **kwargs
        ):

        self.hypodd_inp_config = {
            "IDAT": IDAT,
            "IPHA": IPHA,
            "DIST": DIST,
            "OBSCC": OBSCC,
            "OBSCT": OBSCT,
            "ISTART": ISTART,
            "ISOLV": ISOLV,
            "NSET" : NSET,
            "RATIO": RATIO,
            "TOP": " ".join([str(x) for x in TOP]),
            "VEL": " ".join([str(x) for x in VEL]),
            "DATA_WEIGHTING_AND_REWEIGHTING": "\n".join([" ".join([str(x) for x in set]) for set in DATA_WEIGHTING_AND_REWEIGHTING]),
            "CID": CID,
            "ID": ID,
            'dt_cc': dt_cc, 
            'dt_ct': dt_ct, 
            'event_sel': event_sel, 
            'station_dat': station_dat, 
            'hypoDD_loc': hypoDD_loc, 
            'hypoDD_reloc': hypoDD_reloc, 
            'hypoDD_sta': hypoDD_sta, 
            'hypoDD_res': hypoDD_res, 
            'hypoDD_src': hypoDD_src
        }

        self.hypodd_inp_config["NLAY"] = len(TOP)

        self.msg(f"[msg] {str(self.hypodd_inp_config)}")

        self.is_configured = True

    
    def create_hypoDD_inp_file(self):
        cf = self.hypodd_inp_config
        hypoDD_inp = "\n".join([
            "{dt_cc}",
            "{dt_ct}",
            "{event_sel}",
            "{station_dat}",
            "{hypoDD_loc}",
            "{hypoDD_reloc}",
            "{hypoDD_sta}",
            "{hypoDD_res}",
            "{hypoDD_src}",
            "{IDAT} {IPHA} {DIST}",
            "{OBSCC} {OBSCT}",
            "{ISTART} {ISOLV} {NSET}",
            "{DATA_WEIGHTING_AND_REWEIGHTING}",
            "{NLAY} {RATIO}",
            "{TOP}",
            "{VEL}",
            "{CID}",
            "{ID}"
        ])

        hypoDD_inp = hypoDD_inp.format(**self.hypodd_inp_config)
        return hypoDD_inp
    
    def relocate_hypodd(self):
        if self.is_configured == False:
            self.msg("[msg] please do the configuration using configure()")
        else:
            self.msg("[msg] create an input file")
            hypoDD_inp = self.create_hypoDD_inp_file()
            with open(os.path.join(self.working_dir, "hypoDD.inp"), 'w') as file:
                file.write(hypoDD_inp)
                file.close()
            
            self.msg("[msg] create a batch file")
            compile_bat = "\n".join([
                "@echo off",
                f"SET PATH=%PATH%;{CDIR}",
                ".\hypoDD.exe hypoDD.inp"
            ])
            with open(os.path.join(self.working_dir, "hypoDD.bat"), 'w') as file:
                file.write(compile_bat)
                file.close()
        
            self.msg("[msg] running a hypoDD program . . .")
            shutil.copy(os.path.join(BIN_DIR, "hypoDD.exe"), os.path.join(self.working_dir, "hypoDD.exe"))
            cmd = f"cd {self.working_dir} && .\\hypoDD.bat"
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8', errors='ignore')

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

            self.msg("[msg] remove hypoDD.exe")
            oldfiles = []
            for itype in ("*.o", "*.out", "*.exe", "*.fln"):
                oldfiles.extend(glob.glob(os.path.join(self.working_dir,itype)))

            for oldfile in oldfiles:
                if os.path.isfile(oldfile) == True: os.remove(oldfile)
            
            if process.returncode == 0:
                self.msg('[msg] FINISHED . . .')
            else:
                self.msg('[msg] FAILED . . .')

if __name__ == '__main__':
    newHypoDD = hypoDDrelocate(r"C:\Users\Lenovo\Documents\projects\hypoDD\examples\mytest1-res2")
    newHypoDD.configure_hypodd()
    newHypoDD.relocate_hypodd()