import os
from pathlib import Path
from datetime import datetime

class bmkg2pha(object):
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
        evdate = None
        with open(self.filename, 'r') as file:
            for item in file:
                currLine = item.split()
                if ev == True:
                    idate = currLine[0].split('/')
                    self.events["ID"].append(id)
                    self.events["YR"].append(int(idate[0]))
                    self.events["MO"].append(int(idate[1]))
                    self.events["DY"].append(int(idate[2]))
                    itime = currLine[1].split(':')
                    self.events["HR"].append(int(itime[0]))
                    self.events["MN"].append(int(itime[1]))
                    self.events["SC"].append(float(itime[2]))

                    evdate = datetime.strptime(" ".join([currLine[0], currLine[1]]), "%Y/%m/%d %H:%M:%S.%f")

                    self.events["LAT"].append(float(currLine[2]) * (1 if currLine[3] == 'N' else -1))
                    self.events["LON"].append(float(currLine[4]) * (1 if currLine[5] == 'E' else -1))
                    self.events["DEP"].append(float(currLine[6]))

                    self.events["MAG"].append(float(currLine[8].split('=')[1]))
                    self.events["EH"].append(0.0)
                    self.events["EZ"].append(0.0)
                    
                    ev = False
                
                if currLine != [] and currLine[0] == 'RMS-ERR:':
                    st = False
                    self.events["RMS"].append(float(currLine[1]))

                if st == True:
                    self.sts["ID"].append(id)
                    self.sts["STA"].append(currLine[0])
                    tt = datetime.strptime(" ".join([currLine[2], currLine[3]]), "%y/%m/%d %H:%M:%S.%f") - evdate
                    self.sts["TT"].append(tt.total_seconds())
                    self.sts["WGHT"].append(1)
                    if (idst-1 >= 0) and self.sts["STA"][-2] == currLine[0]:
                        if self.sts["TT"][-1] >= self.sts["TT"][-2]:
                            self.sts["PHA"].append("S")
                        else:
                            self.sts["PHA"][-1] = "S"
                            self.sts["PHA"].append("P")
                    else:
                        self.sts["PHA"].append("P")
                    # self.sts["PHA"].append("S" if (idst-1 >= 0) and self.sts["STA"][-2] == currLine[0] else "P")
                    idst += 1

                if currLine != [] and currLine[0] == 'Event':
                    ev = True
                    id += 1
                    idst = 0

                if currLine != [] and currLine[0] == 'Stat':
                    st = True

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
    filename = os.path.join(Path(os.path.dirname(__file__)).parent, "examples", "bmkg1", "maret")
    main = bmkg2pha(filename)
    main.read()
    filename = os.path.join(Path(os.path.dirname(__file__)).parent, "examples", "bmkg1", "phase.dat")
    main.write(filename)