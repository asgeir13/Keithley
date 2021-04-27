import numpy as np
import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

V=[0,1,2,3,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130]
I=[0,0.11,0.24,0.36,0.6,1.2,1.81,2.42,3.02,3.62,4.21,4.82,5.4,5.98,6.56,7.12,7.68,8.24,8.79,9.33,9.85,10.32,10.79,11.23,11.61,12.15,12.58,12.95,13.41,13.81]
B=[43.6,75,104.8,127.1,196.8,377,541,683,797,881,953,994,1037,1069,1099,1119,1137,1157,1183,1198,1202,1226,1230,1247,1253,1264,1263,1274,1285,1294]
t=tk.filedialog.askopenfilenames() #use tkinter to make a popup file open window
f=interp1d(V,B,kin
d='cubic') #spline fit to the calibration data, this is used to concert V to mT
fi=interp1d(I,B,kind='cubic')
dicti=dict()
listi=list()

d=float(input('Thickness [nm]: ')) #demand sample thickness in nm
d=d*10**-9
for n, item in enumerate(t): #this for loop reads the IV data files and findes the slope of IV for each measurement
    V=pd.read_csv(item, header=None, sep='\t', decimal='.', usecols=[0,1], engine='python', skiprows=1)
    I=V[1].to_numpy()
    v=V[0].to_numpy()
    regression=np.polyfit(I,v,1)
    s=item.split('V')[0].split('/')[-1]
    s=float(s)
    field=f(s) #here is the Voltage converted to mT with the spline extrapolation
    amp=item.split('A')[0].split('V')[-1]
    amp=float(amp)
    fieldamp=fi(amp)
    sign=item.split('V')[-1].split('.')[0]
    print(sign)
    current=item.split('A')[1]
    voltage=item.split('A')[2].split('V')[0]
    name=str(np.around(fieldamp,2))+'mT_'+current+'.'+voltage
    if item.split('/')[-2]=='Py1012_2':
        if len(sign)==1:
            if sign=='+':
                 name=str(np.around(fieldamp,2))+'mT_'+current+'.'+voltage
            else:
                name=str(-1*np.around(fieldamp,2))+'mT_'+current+'.'+voltage
        elif len(sign)==2:
            if sign[0]=='+':
                name=str(np.around(fieldamp,2))+'mT_'+current+'.'+voltage
            else:
                name=str(-1*np.around(fieldamp,2))+'mT_'+current+'.'+voltage
        else:
            name=str(-1*np.around(fieldamp,2))+'mT_'+current+'.'+voltage
    
    if n==0:
        listi.append(name.split('mT')[0])
    else:
        listi.append(name.split('mT')[0])

    dicti[name]=regression[0]

radict=dict()
radict1=dict()
for item in listi: #this double for loop parses the filenames that we made to secure correct assignments i.e. 12.34, 21.34, 12.43 and 21.43 are all equal with abs() of slope
    for key in dicti:
        #print(key)
        if key.split('m')[0]==item:
            ele=key.split('_')[1]
            #print(ele)
            if ele=='12.34' or ele=='21.34' or ele=='12.43' or ele=='21.43':
                ABCD=dicti[key]
            elif ele=='13.24' or ele=='13.42' or ele=='31.24' or ele=='31.42':
                ACBD=dicti[key]
            elif ele=='14.23' or ele=='14.32' or ele=='41.23' or ele=='41.32':
                ADBC=dicti[key]
            elif ele=='23.14' or ele=='23.41' or ele=='32.14' or ele=='32.41':
                BCAD=dicti[key]
            elif ele=='24.13' or ele=='24.31' or ele=='42.13' or ele=='42.31':
                BDAC=dicti[key]
            else:
                DCAB=dicti[key]
   
    try: #these are van der Pauw calculations to determine resistivity here we assume square samples with no shape effect or corrections
        i1234=(abs(ABCD)+abs(DCAB))/2
        i1423=(abs(ADBC)+abs(BCAD))/2
        rho=np.pi*d*(abs(i1234)+abs(i1423))/(2*np.log(2))
        radict[round(float(item)*10**-3,5)]=[rho] 
    except:
        print('need van der Pauw meas')

    try: #this is the Hall resistivity
        i1324=ACBD
        i2413=BDAC
        rho1=d*(abs(i1324)+abs(i2413))/2
        radict1[round(float(item)*10**-3,5)]=[rho1]
    except:
        print('need hall meas')
    
x=radict1.keys()
Hall=[value for values in radict1.values() for value in values]
vdP=[value for values in radict.values() for value in values]
title=t[0].split('/')[-2]
pos=(np.max(Hall)+np.min(Hall))/2
plt.plot(x,Hall,'+')
plt.text(x=0.3, y=pos, s=f'd= {np.around(d*10**9,0)} nm')
plt.xlabel('B [T]')
plt.title(title)
plt.ylabel(r'$\rho_H \ [\Omega m]$')
plt.show()
try:
    plt.plot(x,vdP,'o')
    plt.xlabel('B [T]')
    plt.title(title)
    plt.ylabel(r'$\rho_{vdP} \ [\Omega m]$')
    plt.show()
except:
    print('Need vdP')
