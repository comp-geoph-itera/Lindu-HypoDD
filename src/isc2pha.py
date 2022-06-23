import os
from pathlib import Path
from datetime import datetime, timedelta
import re

class isc2pha(object):
    def __init__(self, filename):
        self.filename = filename
        self.events = {key:[] for key in ['YR', 'MO', 'DY', 'HR', 'MN', 'SC', 
                                     'LAT', 'LON', 'DEP', 'MAG', 'EH', 
                                     'EZ', 'RMS', 'ID']}
        self.sts = {key:[] for key in ['ID', 'STA', 'TT', 'WGHT', 'PHA']}
    
    def read(self):
        id = 0
        ev = False
        idst = 0
        st = False
        chkst = True
        evdate = None
        mag = False
        magval = 0.0
        evchk = [0,11,23,30,36,45,55,61,67,71,77,83,88,93,97,104,111]
        with open(self.filename, 'r') as file:
            for item in file:
                currLine = item.split()
                if ev == True:
                    if chkst == False:
                        for key in self.events.keys():
                            if key != 'MAG':
                                del self.events[key][-1]

                    currLine = [item[evchk[c]:evchk[c+1]].strip() for c in range(len(evchk) - 1)]
                    idate = currLine[0].split('/')
                    self.events["ID"].append(id)
                    self.events["YR"].append(int(idate[0]))
                    self.events["MO"].append(int(idate[1]))
                    self.events["DY"].append(int(idate[2]))
                    itime = currLine[1].split(':')
                    self.events["HR"].append(int(itime[0]))
                    self.events["MN"].append(int(itime[1]))
                    self.events["SC"].append(float(itime[2]))
                    strtime = ":".join([str(int(itime[0])), str(int(itime[1])), str(float(itime[2]))])

                    evdate = datetime.strptime(" ".join([currLine[0], strtime]), "%Y/%m/%d %H:%M:%S.%f")

                    self.events["LAT"].append(float(currLine[4]))
                    self.events["LON"].append(float(currLine[5]))
                    self.events["DEP"].append(float(re.sub('[A-Za-z]','', currLine[9])))
                    
                    self.events["RMS"].append(float(currLine[2]) if currLine[2] != '' else 0.0)
                    self.events["EH"].append(0.0)
                    self.events["EZ"].append(0.0)
                    
                    ev = False
                    chkst = False
                
                if mag == True:
                    magval = float(currLine[1])
                    mag = False
                
                if currLine == []:
                    st = False

                if st == True:
                    if currLine[3] in ['P', 'S']:
                        self.sts["ID"].append(id)
                        self.sts["STA"].append(currLine[0])
                        itime = currLine[4].split(':')
                        strtime = ":".join([str(int(itime[0])), str(int(itime[1])), str(float(itime[2]))])
                        stdate = datetime.strptime(" ".join([evdate.strftime('%Y/%m/%d'), strtime]), "%Y/%m/%d %H:%M:%S.%f")
                        if stdate >= evdate:
                            tt = stdate - evdate
                        else:
                            tt = stdate + timedelta(days=1) - evdate
                        self.sts["TT"].append(tt.total_seconds())
                        self.sts["WGHT"].append(1)
                        if currLine[3] == 'P':
                            self.sts["PHA"].append("P")
                        else:
                            self.sts["PHA"].append("S")
                        # self.sts["PHA"].append("S" if (idst-1 >= 0) and self.sts["STA"][-2] == currLine[0] else "P")
                        idst += 1

                if currLine != [] and currLine[0] == 'Date':
                    ev = True
                    id += 1
                    idst = 0
                
                if currLine != [] and currLine[0] == 'Magnitude':
                    mag = True

                if currLine != [] and currLine[0] == 'Sta':
                    st = True
                    chkst = True
                    self.events["MAG"].append(magval)
                    magval = 0.0

                # if id > 5: break
        # e, s = self.events, self.sts
        # self.events = pd.DataFrame(self.events)
        # self.sts = pd.DataFrame(self.sts)
        # del e, s
    
    def write(self, filename):
        pha_list = []
        e = self.events
        s = self.sts
        n = 0

        for i in range(len(e["ID"])):
            pha_list.append("# " + " ".join([str(e[key][i]) for key in list(e.keys())]))
            for j in range(n, len(s["ID"])):
                if s["ID"][j] == e["ID"][i]:
                    pha_list.append(" ".join([str(s[key][j]) for key in list(s.keys())[1::]]))

        # self.events["text"] = self.events.loc[:,:].astype(str).agg(lambda x: '# ' + ' '.join(x), 1)
        # self.sts["text"] = self.sts.loc[:,'STA':].astype(str).agg(' '.join, 1)
        # for i in range(len(self.events)):
        #     pha_list.append(self.events["text"][i])
        #     pha_list += self.sts["text"][self.sts["ID"] == self.events["ID"][i]].tolist()
        pha_text = "\n".join(pha_list)
        
        with open(filename, 'w') as f:
            f.write(pha_text)

if __name__ == '__main__':
    filename = os.path.join(Path(os.path.dirname(__file__)).parent, "examples", "isc", "test3.txt")
    main = isc2pha(filename)
    main.read()
    filename = os.path.join(Path(os.path.dirname(__file__)).parent, "examples", "isc", "phase.dat")
    main.write(filename)