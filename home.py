import tkinter as tk
from tkinter import ttk
import pandas as pd
import math
import os
import experiment as exp

         
class ScheduleEntry:
    def __init__(self, frame):
        self.frame = frame
        # ------ Habituation ------
        self.habituation_label = ttk.Label(self.frame, text="Habituation").grid(column=1, row=1, sticky='W')

        self.habituationStart_label = ttk.Label(self.frame, text="Start:").grid(column=1, row=2, sticky='E')
        self.habituationStart = tk.StringVar()
        self.habituationStart_entry = ttk.Entry(self.frame, width=7, textvariable=self.habituationStart)
        self.habituationStart_entry.grid(column=2, row=2, sticky='we')

        self.habituationEnd_label = ttk.Label(self.frame, text="End:").grid(column=3, row=2, sticky='E')
        self.habituationEnd = tk.StringVar()
        self.habituationEnd_entry = ttk.Entry(self.frame, width=7, textvariable=self.habituationEnd)
        self.habituationEnd_entry.grid(column=4, row=2, sticky='we')
        # ----------
        # ----- Priming ------
        self.primingLabel = ttk.Label(self.frame, text="Priming").grid(column=1, row=4, sticky='W')

        self.primingStartLabel = ttk.Label(self.frame, text="Start:").grid(column=1, row=5, sticky='E')
        self.primingStart = tk.StringVar()
        self.primingStart_entry = ttk.Entry(self.frame, width=7, textvariable=self.primingStart)
        self.primingStart_entry.grid(column=2, row=5, sticky='we')
        
        self.primingEnd_label = ttk.Label(self.frame, text="End:").grid(column=3, row=5, sticky=tk.E)
        self.primingEnd = tk.StringVar()
        self.primingEnd_entry = ttk.Entry(self.frame, width=7, textvariable=self.primingEnd)
        self.primingEnd_entry.grid(column=4, row=5, sticky=(tk.W, tk.E))
        # ----------
        # ----- Alcohol Consumption -----
        self.alcoholConsumption_label = ttk.Label(self.frame, text="Alcohol Consumption").grid(column=1, row=7, sticky='W')
        
        self.alcoholConsumptionStart_label = ttk.Label(self.frame, text="Start:").grid(column=1, row=8, sticky='E')
        self.alcoholConsumptionStart = tk.StringVar()
        self.alcoholConsumptionStart_entry = ttk.Entry(self.frame, width=8, textvariable=self.alcoholConsumptionStart)
        self.alcoholConsumptionStart_entry.grid(column=2, row=8, sticky='we')
        # ----------
        
class Home:
    def __init__(self, master):
        self.master = master
        self.master.resizable(0, 0)
        self.master.title("Binge drinking protocol")

        self.frame = ttk.Frame(self.master, padding=(12,12,12,12))
        self.frame.grid(column=0,row=0,sticky='nwes')
        self.frame.columnconfigure(1, weight=4)
        self.frame.columnconfigure(2, weight=1)

        self.expLabel = ttk.Label(self.frame, text="Select experiment:").grid(column=1, row=1, sticky='w')
        self.exp = [x[1] for x in os.walk('experiments')][0]
        self.expvar = tk.StringVar(value=self.exp)
        self.expvar_entry = tk.Listbox(self.frame, listvariable=self.expvar)
        self.expvar_entry.grid(column=1, row=2, sticky='we')
        self.button = ttk.Button(self.frame, text = 'Open', command = self.open_experiment).grid(column=1, row=3, sticky='e')
        self.updateButton = tk.Button(self.frame, text='update', command=self.update_list).grid(column=1, row=4, sticky='w')

        ttk.Label(self.frame, text='').grid(column=2, row=1)
        self.button1 = ttk.Button(self.frame, text = 'New experiment', command = self.new_experiment).grid(column=2, row=2, sticky='nwes')

        for widget in self.frame.winfo_children():
            widget.grid(padx=5, pady=5)


    
    def new_experiment(self):
        self.newExperiment = tk.Toplevel(self.master)
        self.app = NewExperiment(self.newExperiment)
    def open_experiment(self):
        selection = self.expvar_entry.get('active')
        self.experimentInfo = tk.Toplevel(self.master)
        self.app = ExperimentInfo(self.experimentInfo, selection)
    def update_list(self):
        self.expvar.set([x[1] for x in os.walk('experiments')][0])

class NewExperiment:
    def __init__(self, master):
        self.experiment = exp.Experiment()

        self.master = master
        self.master.resizable(0, 0)
        self.master.title("New Experiment")

        self.frame = ttk.Frame(self.master, padding=(12,12,12,12))
        self.frame.grid(column=0,row=0,sticky='nwes')

        # ------ Load data ------
        self.dataLabel = ttk.Label(self.frame, text="Data").grid(column=1, row=1, sticky='w')
        self.data = tk.StringVar()
        self.data_entry = ttk.Entry(self.frame, width=7, textvariable=self.data)
        self.data_entry.grid(column=2, row=1, sticky='we')
        self.dataButton = ttk.Button(self.frame, text="Load", command=self.load_data).grid(column=3, row=1, sticky='W')
        self.dataError = ttk.Label(self.frame, foreground='red')
        # -----------------------
        # ------ Input Schedule ------
        self.scheduleFrame = ttk.Frame(self.master, padding=(12,12,12,12))
        self.scheduleFrame.grid(column=0, row=1)
        self.scheduleEntry = ScheduleEntry(self.scheduleFrame)
        self.scheduleErrors = []
        # ----------
        # ----- Groups -----
        self.groupsLabel = ttk.Label(self.scheduleFrame, text="Select CNO mice:").grid(column=1, row=10, sticky='E')
        self.mice = []
        self.micevar = tk.StringVar(value=self.mice)
        self.micevar_entry = tk.Listbox(self.scheduleFrame, listvariable=self.micevar, selectmode='multiple')
        self.micevar_entry.grid(column=2, row=10, sticky='we')
        # ----------
        # ----- Name -----
        self.nameLabel = ttk.Label(self.scheduleFrame, text="Name:").grid(column=1, row=11, sticky='E')
        self.name = tk.StringVar()
        self.name_entry = ttk.Entry(self.scheduleFrame, width=7, textvariable=self.name)
        self.name_entry.grid(column=2, row=11, sticky='we')
        self.nameError = ttk.Label(self.scheduleFrame, foreground='red')
        self.nameError.grid(column=2, row=12)

        # ----------
        self.scheduleButton = ttk.Button(self.scheduleFrame, text="Submit", command=self.submit_schedule).grid(column=3, row=11, sticky='W')

        for child in self.frame.winfo_children(): 
                child.grid_configure(padx=5, pady=5)
        for child in self.scheduleFrame.winfo_children(): 
                child.grid_configure(padx=5, pady=5)
        
    def load_data(self):
            try:
                # ----- Open file -----
                path = self.data.get()
                self.df = pd.read_csv(path,sep="\t")
                # ----------
                # ----- Mice list -----
                self.mice_list = list(self.df['Animal'].unique())
                self.mice_list = list(map(str, self.mice_list))
                self.micevar.set(self.mice_list)
                setattr(self.experiment, 'mice', self.mice_list)
                # ----------
                setattr(self.experiment,'dfdir', path)
                setattr(self.experiment, 'df', self.df)
                self.dataError.grid_remove()
            except:
                self.dataError['text'] = "Couldn't load the data"
                self.dataError.grid(column=1, row=3)

    def submit_schedule(self):
        # ----- errors -----
        for error in self.scheduleErrors:
            error.grid_remove()
        self.scheduleErrors.clear()
        self.nameError['text'] = ""
        # ----------
        self.entries = [widget.get() for widget in self.scheduleEntry.frame.winfo_children() if isinstance(widget, tk.Entry)]
        # ----- Experiment Name -----
        if not self.entries[-1]:
            self.nameError['text'] = "Please name your experiment"
            return
        else:
            name = 'experiments/'+self.name.get()
            setattr(self.experiment, 'name', name)
            self.entries.pop(-1)
        # ----------
        # ------ Experiment Schedule -----
        i=0
        for entry in self.entries:
            if not entry:
                self.scheduleError = ttk.Label(self.scheduleFrame, text='Please enter the date', foreground='red')
                self.scheduleError.grid(column=2*(i%2)+2, row=3*math.ceil((i+1)/2))
                self.scheduleErrors.append(self.scheduleError)
            else:
                try: 
                    pd.to_datetime(entry).date()
                except:
                    self.scheduleError = ttk.Label(self.scheduleFrame, text='Please enter a correct date', foreground='red')
                    self.scheduleError.grid(column=2*(i%2)+2, row=3*math.ceil((i+1)/2))
                    self.scheduleErrors.append(self.scheduleError)
            i = i+1
        # ----------
        # ----- Groups -----
        self.cno = [self.micevar_entry.get(i) for i in self.micevar_entry.curselection()]
        setattr(self.experiment,'cno',self.cno)
        # ----------
        if self.scheduleErrors == []:
            try:
                self.experiment.createDirectory()
                self.experiment.saveSchedule(self.entries)
                self.experiment.saveData()
                self.experiment.saveMiceInfo()
            except FileExistsError:
                self.nameError['text'] = 'An experiment with this name already exists'
             
class ExperimentInfo:
    def __init__(self, master, experiment):
        self.master = master
        self.master.resizable(0, 0)
        self.master.title(experiment)

        self.selection = experiment
        self.experiment = exp.Experiment()

        self.experiment.setSchedule('experiments/'+self.selection+'/Schedule.txt')
        self.experiment.setInfo('experiments/'+self.selection+'/Info.txt')
        self.experiment.setData('experiments/'+self.selection+'/Data.txt')
        self.experiment.analyze()
        def dailyLicks():
            self.experiment.dailyLicks()
        def dailyNosepokes():
            self.experiment.dailyNosepokes()
        def relapseDrinking():
            self.experiment.relapseDrinking()

        self.frame = ttk.Frame(self.master, padding=(12,12,12,12))
        self.frame.grid(column=0,row=0,sticky='nwes')
        self.name = ttk.Label(self.frame, text=self.selection).grid(column=1, row=1, sticky='w')
        self.licks = ttk.Button(self.frame, text="Daily licks", command=dailyLicks).grid(column=1, row=2, sticky='we')
        self.nosepokes = ttk.Button(self.frame, text="Daily nosepokes", command=dailyNosepokes).grid(column=1, row=3, sticky='we')
        self.relapse = ttk.Button(self.frame, text="Relapse Drinking", command=relapseDrinking).grid(column=1, row=4, sticky='we')



def main(): 
    root = tk.Tk()
    app = Home(root)
    root.mainloop()

if __name__ == '__main__':
    main()
