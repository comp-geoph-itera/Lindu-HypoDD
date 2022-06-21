# Lindu Software: A Repository for handling HypoDD

This GUI program is dedicated to operate **HypoDD** as a graphical user interface. It is focusing on providing the description and understanding how to input parameters properly instead of simplifying the HypoDD program.

The latest release: https://github.com/comp-geoph-itera/Lindu-HypoDD/releases/download/v0.0.3/Lindu_hypoDD_v0.0.3.zip (only for **Windows**)

We use Python **3.9.10**. The Python requirements for using the scripts (the script files can be found in /src/ folder):

```
altgraph==0.17.2
future==0.18.2
pefile==2022.5.30
pyinstaller==5.1
pyinstaller-hooks-contrib==2022.7
PyQt5==5.15.6
PyQt5-Qt5==5.15.2
PyQt5-sip==12.10.1
PyQtWebEngine==5.15.5
PyQtWebEngine-Qt5==5.15.2
pywin32-ctypes==0.2.0
```

*pyinstaller is only used for generating the executable files.

In order to fill HypoDD and mingw64 folders, we can copy the contents from the release compressed (Lindu_hypoDD_vX.X.X.zip) files.

## FUTURE PLANS

1. The `Help` will be fully applied as a full version.
2. Auto-generating the values of some certain parameters to make easier using the program.
3. Interactive descriptions that will help users to understand how to put a proper value in a parameter.
4. Merging to Lindu Software as a whole seismology program.

# Gallery
<p align="center">
	<img src="/src/figs/lindu-hypoDD-1.png" alt="The Lindu-HypoDD GUI Interface" width="800"/>
	<br>
	The Lindu-HypoDD GUI Interface
	<br>	
</p>
