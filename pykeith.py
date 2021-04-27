# Program to measure IV and calculate slope (resistance)
import sys,os,pdb
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from scipy.interpolate import interp1d
import datetime


#App class makes the frames and allows easy switching between them, frames are the different windows that pop up and cover the GUI,
#startpage is a the only frame as is

class App(tk.Tk):   
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Keith")
        container = tk.Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        #x, y = self.winfo_screenwidth(), self.winfo_screenheight()
        #self.geometry("%dx%d+%d+%d" % (800,450,x/2-800/2,y/2-450/2))

        self.frames = {}
        #for-loop to place each page in the container or parent page
        #for F in (StartPage):

        frame = StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid(row = 0, column = 0, sticky="nsew")

        self.show_frame(StartPage)
        #raises the page to the top with tkraise()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    #this is the main page and the only frame
class StartPage(tk.Frame):
    def __init__(self, parent, controller): #this makes the layout of the frame, first we make the figure and then some parameter control over the sweep settings
        tk.Frame.__init__(self, parent)
        
        self.fig = plt.figure(constrained_layout=False, figsize=[10,9])
        gs1 = self.fig.add_gridspec(nrows=1, ncols=1, left=0.1, right=0.95, wspace=0.3)
        self.ax = self.fig.add_subplot(gs1[0,0])
        self.ax.set_xlabel('I [A]')
        self.ax.set_ylabel('V [V]')
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=30, columnspan=30)
        self.canvas.draw_idle()
        self.toolbarframe=tk.Frame(self)
        self.toolbarframe.grid(row=101, column=0, columnspan=10, sticky='new')
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarframe)
        self.toolbar.grid(row=102, column=0, columnspan=10, sticky='')

        tk.Label(self, text='Source',relief='ridge').grid(row=1, column=31) 
        tk.Button(self, text='Exit', command=self._quit).grid(row=1, column=42)  #this calls the exit fuction, the program can freeze up if not exited with this button
        
        self.vscurr, self.vsvolt= tk.IntVar(self), tk.IntVar(self)  #defining integer variables that can be 0 or 1 for the checkbuttons below
        self.scurr=tk.Checkbutton(self, text='Current', variable=self.vscurr, command=lambda: self.set_source(0)).grid(row=2, column=32,sticky='w') 
        self.svolt=tk.Checkbutton(self, text='Voltage', variable=self.vsvolt, command=lambda: self.set_source(1)).grid(row=3, column=32,sticky='w')
        self.vscurr.set(1)  #setting source as current as default

     #   tk.Label(self, text='Range', relief='ridge').grid(row=5, column=31)       #the following text is commented but here is a range checkbutton grid, this can be used to implement range control
     #   tk.Label(self, text='Voltage', relief='ridge').grid(row=6, column=32)     #the choice of range is not necessary for the current setup, in which case the sweep range is set to BEST.
     #   self.voltrange=['200 V','20 V','2 V','200 mV','Auto']
     #   self.currentrange=['1 A', '100 mA', '10 mA', '1 mA', '100 \u03BC A', '10 \u03BC A', '1 \u03BC A', 'Auto']

   #     self.varttwocv, self.varautov=tk.IntVar(self), tk.IntVar(self)
   #     self.vartwocmv, self.varttwov, self.varttwenty=tk.IntVar(self), tk.IntVar(self), tk.IntVar(self)
   #     self.varonea,self.varonecma,self.vartenma=tk.IntVar(self),tk.IntVar(self),tk.IntVar(self)
   #     self.varonema,self.varcentmica,self.vartenmica,self.varonemica,self.varautoa=tk.IntVar(self),tk.IntVar(self),tk.IntVar(self),tk.IntVar(self),tk.IntVar(self)
   #     self.checklistv=[self.varttwocv,  self.varttwenty,  self.varttwov, self.vartwocmv, self.varautov]
   #     self.twocv=tk.Checkbutton(self, text=self.voltrange[0], variable=self.varttwocv, command=lambda: self.set_checkvolt(0)).grid(row=7, column=32,sticky='w')
   #     self.twenty=tk.Checkbutton(self, text=self.voltrange[1], variable=self.varttwenty, command=lambda: self.set_checkvolt(1)).grid(row=8, column=32,sticky='w')
   #     self.twov=tk.Checkbutton(self, text=self.voltrange[2], variable=self.varttwov, command=lambda: self.set_checkvolt(2)).grid(row=9, column=32,sticky='w')
   #     self.twocmv=tk.Checkbutton(self, text=self.voltrange[3], variable=self.vartwocmv, command=lambda: self.set_checkvolt(3)).grid(row=10, column=32,sticky='w')
   #     self.autov=tk.Checkbutton(self, text=self.voltrange[4], variable=self.varautov, command=lambda: self.set_checkvolt(4)).grid(row=11, column=32,sticky='w')
   #     
   #     self.checklista=[self.varonea,self.varonecma,self.vartenma,self.varonema,self.varcentmica,self.vartenmica,self.varonemica,self.varautoa]
   #     self.onea=tk.Checkbutton(self, text=self.currentrange[0],variable=self.varonea, command=lambda: self.set_checkcurr(0)).grid(row=7, column=33,sticky='w')
   #     self.onecma=tk.Checkbutton(self, text=self.currentrange[1],variable=self.varonecma, command=lambda: self.set_checkcurr(1)).grid(row=8, column=33,sticky='w')
   #     self.tenma=tk.Checkbutton(self, text=self.currentrange[2], variable=self.vartenma, command=lambda: self.set_checkcurr(2)).grid(row=9, column=33,sticky='w')
   #     self.onema=tk.Checkbutton(self, text=self.currentrange[3], variable=self.varonema, command=lambda: self.set_checkcurr(3)).grid(row=10, column=33,sticky='w')
   #     self.centmica=tk.Checkbutton(self, text=self.currentrange[4], variable=self.varcentmica, command=lambda: self.set_checkcurr(4)).grid(row=11, column=33,sticky='w')
   #     self.tenmica=tk.Checkbutton(self, text=self.currentrange[5], variable=self.vartenmica, command=lambda: self.set_checkcurr(5)).grid(row=12, column=33,sticky='w')
   #     self.onemica=tk.Checkbutton(self, text=self.currentrange[6], variable=self.varonemica, command=lambda: self.set_checkcurr(6)).grid(row=13, column=33,sticky='w')
   #     self.autoa=tk.Checkbutton(self, text=self.currentrange[7], variable=self.varautoa, command=lambda: self.set_checkcurr(7)).grid(row=14, column=33,sticky='w')
   #     tk.Label(self, text='Current', relief='ridge').grid(row=6, column=33)
        
        self.set=tk.Button(self, text='Setup', command=self.setup).grid(row=5, column=34)
        self.scan=tk.Button(self, text='Scan', command=self.scan).grid(row=5, column=36)

        tk.Label(self, text='Sweep', relief='ridge').grid(row=1, column=35)
        tk.Label(self, text='Start').grid(row=2, column=35)
        self.start=tk.Entry(self, width=6)   #this configures the sweep, start, stop and step values
        self.start.grid(row=2, column=36)
        tk.Label(self, text='Stop').grid(row=3,column=35)
        self.stop=tk.Entry(self, width=6)
        self.stop.grid(row=3, column=36)
        tk.Label(self, text='Step').grid(row=4, column=35)
        self.step=tk.Entry(self, width=6)
        self.step.grid(row=4, column=36)
        
        self.fourvar=tk.IntVar()   #here we set the keitheley to the 4 wire configuration
        self.fourvar.set(1)
        self.four=tk.Checkbutton(self, text='4-wire', variable=self.fourvar)
        self.four.grid(row=4, column=32,sticky='w')

        self.measlist=tk.Listbox(self, height=6, width=6)
        self.measlist.grid(row=6, column=36, rowspan=3, sticky='n')
        tk.Label(self, text='Power supply', relief='ridge').grid(row=5,column=31)
        tk.Label(self, text='Voltage [V]').grid(row=6, column=32)
        self.ventry=tk.Entry(self, width=5)
        self.ventry.grid(row=6, column=33)
        tk.Label(self, text='Current [A]').grid(row=7, column=32)
        self.centry=tk.Entry(self, width=5)
        self.centry.grid(row=7, column=33)
        ele=['12I43V','43I12V','14I23V','23I14V','24I13V','13I24V']
        for i, el in enumerate(ele):        #makes a list that helps saving the measurement quicker, now instead of writing the 12I43V for the filename the item selected in the list adds to the filename
            self.measlist.insert(i,el)
        tk.Label(self, text='Folder').grid(row=8,column=32)
        self.samplename=tk.Entry(self,width=5)
        self.samplename.grid(row=8, column=33)
        tk.Label(self,text='Resistance [\u2126]').grid(row=9,column=32)
        self.resist=tk.Entry(self,width=5)
        self.resist.grid(row=9,column=33)

    def set_source(self,arg):  #function that runs with the source checkbuttons, when current is chosen the voltage checkbutton unchecks and vice versa
        if arg==0:
            self.vsvolt.set(0)
        elif arg==1:
            self.vscurr.set(0)


#    def set_checkvolt(self,arg):                   #sets the range for voltage and current
#        for i, ele in enumerate(self.checklistv):
#           if i!=arg:
#                ele.set(0)
#        if arg==0:
#            self.voltrangevalue=' 200'
#        elif arg==1:
#            self.voltrangevalue=' 20'
#        elif arg==2:
#            self.voltrangevalue=' 2'
#        elif arg==3:
#            self.voltrangevalue=' 2E-1'
#        else:
#            self.voltrangevalue=':AUTO ON'
#
#    def set_checkcurr(self,arg):
#        for i, ele in enumerate(self.checklista):
#            if i!=arg:
#                ele.set(0)
#        
#        if arg==0:
#            self.currentrangevalue=' 1'
#        elif arg==1:
#            self.currentrangevalue=' 1E-1'
#        elif arg==2:    
#            self.currentrangevalue=' 1E-2'
#        elif arg==3:
#            self.currentrangevalue=' 1E-3'
#        elif arg==4:
#            self.currentrangevalue=' 1E-4'
#        elif arg==5:    
#            self.currentrangevalue=' 1E-5'
#        elif arg==6:
#            self.currentrangevalue=' 1E-6'
#        else:
#            self.currentrangevalue=':AUTO ON'
        
    def setup(self):     #this function finds the keithley with another function findKeithley
        self.instr=instr
        start=self.start.get()
        stop=self.stop.get() 
        step=self.step.get()
        self.count=(abs(float(start))+abs(float(stop)))/float(step)+1   #calculates the number of measurements

        if self.vscurr.get()==0 and self.vsvolt.get()==1:   #configures the Keithley, what to source and to measure
            self.source='VOLT'
            self.measure='CURR'
            #measurerange=self.currentrangevalue  #this is used with the commented range code here above
            #sourcerange=self.voltrangevalue
        elif self.vscurr.get()==1 and self.vsvolt.get()==0:
            self.source='CURR'
            self.measure='VOLT'
           # measurerange=self.voltrangevalue
           # sourcerange=self.currentrangevalue
        else:
            print('Choose source')
        
        #list of commands that are sent to the Keithley to configure the sweep
        #RST - resets the keithley configuration
        #rsen on - activates 4 wire mode
        #arm:sour bus - controls the sweep trigger, after configuration the sweep doesn't run without triggering the measurement, this sets the trigger to the usb bus of the PC
        #del:auto on - this is the delay, time that passes by between the change in source value and the corresponding measurement at that source value, here set to auto 
        #sens:func and sour:func - configures sense and source
        #swe:spac lin - this sets the sweep to linear steps
        #swe:rang best - this is the range setup, here set to best
        #Mode swe - sets to sweep mode
        #sour:START... - start, stop and step of sweep
        #trig:coun - important, here the input is the number of measurements in each sweep

        cmd = ['*RST', \
            ':SYST:CLE', \
            ':SYST:RSEN ON', \
            ':ARM:SOUR BUS', \
            ':SOUR:DEL:AUTO ON', \
            ':SENS:FUNC "%s"' % self.measure, \
            ':SOUR:FUNC %s' % self.source, \
            ':SOUR:SWE:SPAC LIN',\
            ':SOUR:SWE:RANG BEST', \
            ':SOUR:%s:MODE SWE' % self.source, \
            ':SOUR:%s:START %s' % (self.source, start), \
            ':SOUR:%s:STOP %s' % (self.source, stop), \
            ':SOUR:%s:STEP %s' % (self.source, step), \
            ':TRIG:COUN %s' % str(self.count)] 

        for command in cmd:
            print("Writing to Keithley: %s" % (command,))  #function that runs through the command list and checks for errors
            self.instr.write(command)
            error = self.checkError(self.instr)
            time.sleep(.1)

    def scan(self):  #after setup the Keithley is ready to run the sweep and only needs a trigger, here are commands that trigger the sweep and gather the data. The measurement is plotted and saved with the function file_save
        self.instr.write(':OUTP ON')
        self.instr.write(':INIT')
        self.instr.write('*TRG')
        timi=0.09*self.count
        time.sleep(timi)  #waits, 0.09 is the average time per count
        self.instr.write('OUTP OFF')
        self.instr.write(':ABOR')
        self.instr.write(':FETC?')
        red=self.instr.read('\n')
        self.array=np.array([float(item) for item in red.split(',')],dtype='float64').reshape(int(self.count),5)
        self.ax.clear()
        self.ax.plot(self.array[:,1], self.array[:,0], 'o')
        self.ax.set_xlabel('I [A]')
        self.ax.set_ylabel('V [V]')
        self.canvas.draw()
        regression=np.polyfit(self.array[:,1],self.array[:,0],1)
        self.resist.delete(0,END)
        self.resist.insert(0, str(np.around(regression[0],4)))
        self.file_save()

    def _quit(self):  #exits the tkinter GUI loop, necessesary for gentle shut down of the program
        app.quit()
       	app.destroy()

    def file_save(self):
        combination=self.measlist.get(self.measlist.curselection()[0])   #gets the selected item from the measlist
        Bfield=f(float(self.centry.get()))
        samplename=self.samplename.get()  #get the folder name, where we want to save our measurements
        path=f'c:/Users/Geiri/Documents/Master/measurements/{samplename}/'  #this needs to be changed, here we choose where to save our data, so change the path up to /{samplename}/
        try:  #this makes a the folder in windows, if the folder exists then the file is simply saved in the folder
            os.mkdir(path)
        except OSError as error:
            print(error)
        
        #filename=f'{path}{np.around(Bfield,2)}mT_{combination}.txt'
        filename=f'{path}{float(self.ventry.get())}V{float(self.centry.get())}A{combination}.txt' #filename and path
        intro=f''' #IV measurements for vdP or Hall resistivity, measured {datetime.datetime.now()}, this file inclued the source I or V and the corresponding V or I measurements, the slope is taken and the applied magnetic field is given\n #The magnetic field is {Bfield} mT\n
        #Source is {self.source} and we measure {self.measure}\n #V [V]\tI [A]'''
        np.savetxt(filename, self.array[:,:2], delimiter='\t', header=intro, fmt='%.5e', comments='')
    
    def checkError(self, instr):
        err = instr.query(":SYST:ERR:NEXT?")
        #print(err)
        if err.split(',')[0] != "0":
            print("ERROR: %s" % err)
            error = True
        else:
            error = False
        return error

try:
    rm = visa.ResourceManager()
    addr = None
    for instrument in rm.list_resources():
        if "GPIB0::" in instrument and "::INSTR" in instrument:
            addr = instrument
            print("Keithley is located at %s" % (addr,))
    instr = rm.open_resource(addr,timeout=10000.)

except:
    print('Connect to Keithley')

#calibration data for the magnet, V and I is the voltage and the current that the amplifier displays and B is the magnetic field measured with a Gaussmeter
V=[0,1,2,3,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130]
I=[0,0.11,0.24,0.36,0.6,1.2,1.81,2.42,3.02,3.62,4.21,4.82,5.4,5.98,6.56,7.12,7.68,8.24,8.79,9.33,9.85,10.32,10.79,11.23,11.61,12.15,12.58,12.95,13.41,13.81]
B=[43.6,75,104.8,127.1,196.8,377,541,683,797,881,953,994,1037,1069,1099,1119,1137,1157,1183,1198,1202,1226,1230,1247,1253,1264,1263,1274,1285,1294]
f=interp1d(I,B,kind='cubic')  #fitting the calibration data, use here spline

app = App()
app.mainloop()
