import pandas as pd
import math
import os
from datetime import timedelta
from datetime import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class Experiment:
    def __init__(self):
        self.name = ''
        self.dfdir = ''
        self.df = {}
        self.mice = []
        self.cno = []
        self.schedule = {}
        self.mice_info = {}
        self.alcohol_corners = []
        self.water_corners = []
        self.daily = {}
        self.phase_colors = {
            "Habituation": "lightgrey",
            "Priming": "khaki",
            "AlcoholConsumption": "lightskyblue",
            "Withdrawal": "salmon",
            "Relapse": "firebrick"
            }
    def saveSchedule(self, phases):
        schedule = "Phase\tStart\tEnd\nHabituation\t"+phases[0]+"\t"+phases[1]+"\nPriming\t"+phases[2]+"\t"+phases[3]+"\nAlcoholConsumption\t"+phases[4]
        schedule_path = self.name+"/Schedule.txt"
        with open(schedule_path, "x") as f:
            f.write(schedule)
        f.close()
    def createDirectory(self):
        os.mkdir(self.name)
    def saveData(self):
        data_path = self.name+"/Data.txt"
        with open(data_path, "x") as f:
            f.write(self.dfdir)
        f.close()
    def saveMiceInfo(self):
            self.df['StartDate'] = pd.to_datetime(self.df['StartDate']).dt.date
        
            relapse = (
                self.df.groupby("Animal")["StartDate"]
                .agg(["max"])
                .sort_values(["max"])
                .copy()
            )
            
            def Schedule(row):
                row["Withdrawal"] = row["max"] - timedelta(days=7)
                row["Relapse"] = row["max"]
                return row
            def Group(row):
                animal = str(row["Animal"])
                if animal in self.cno:
                    row['Group'] = 'CNO'
                else:
                    row['Group'] = 'Saline'
                return row

            mice_schedule = relapse.apply(Schedule, axis = 1).drop("max",axis=1).reset_index()
            self.mice_info = mice_schedule.apply(Group, axis = 1)

            color_list = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray',
                        'tab:olive','tab:cyan','#1f77b4','#ffbb78','#98df8a','#ff9896','#c5b0d5','#331e78','#ede218']
            color_assignment = dict(zip(
                    mice_schedule['Animal'].unique(),
                    np.random.choice(color_list, size = len(mice_schedule['Animal'].unique()),replace=False)
                ))
            self.mice_info['Color'] = self.mice_info['Animal'].map(color_assignment)

            path = self.name+"/Info.txt"
            self.mice_info.to_csv(path, sep="\t", index=False)

    def setSchedule(self, path):
        schedule = pd.read_csv(path, sep='\t')
        schedule['Start'] = pd.to_datetime(schedule['Start']).dt.date
        schedule['End'] = pd.to_datetime(schedule['End']).dt.date
        self.schedule = schedule.set_index("Phase").T.to_dict()
    def setData(self, path):
        with open(path) as f:
            data_path = f.readline()
        f.close()
        self.df = pd.read_csv(data_path, sep='\t')
        self.df['StartTime'] = self.df['StartTime'].astype(str).str.split('.').str[0]
        self.df['StartTime'] = pd.to_datetime(self.df['StartTime'], format='%H:%M:%S').dt.time
        self.df['StartDate'] = pd.to_datetime(self.df['StartDate']).dt.date
        def assignPhase(row):
            date = row['StartDate']
            animal = row['Animal']
            wd = self.mice_info[animal]["Withdrawal"]
            rp = self.mice_info[animal]["Relapse"]
        
            if self.schedule['Habituation']['Start'] <= date <= self.schedule['Habituation']['End']:
                return "Habituation"
        
            elif self.schedule['Priming']['Start'] <= date <= self.schedule['Priming']['End']:
                return "Priming"
        
            elif self.schedule['AlcoholConsumption']['Start'] <= date < wd:
                return "AlcoholConsumption"
        
            elif wd <= date < rp:
                return "Withdrawal"
        
            elif date == rp:
                return "Relapse"
        
            return None
        self.df["Phase"] = self.df.apply(assignPhase, axis=1)
    def setInfo(self, path):
        mice_info = pd.read_csv(path, sep='\t')
        mice_info['Withdrawal'] = pd.to_datetime(mice_info['Withdrawal']).dt.date
        mice_info['Relapse'] = pd.to_datetime(mice_info['Relapse']).dt.date
        self.mice_info = mice_info.set_index("Animal").T.to_dict()
    def analyze(self):
        self.mice = list(self.df['Animal'].unique())
        self.alcohol_corners = list(self.df[(self.df['CornerCondition'] == 'Correct')&(self.df['StartDate']==self.schedule['AlcoholConsumption']['Start'])]['Corner'].unique())
        self.water_corners = list(self.df[(self.df['CornerCondition'] == 'Neutral')&(self.df['StartDate']==self.schedule['AlcoholConsumption']['Start'])]['Corner'].unique())
        
        start_window = time(14, 0)
        end_window = time(16, 0)
        animal_dates = self.df[["Animal", "Phase", "StartDate"]].drop_duplicates()

        df_filtered = self.df[
                        (self.df["StartTime"] >= start_window) &
                        (self.df["StartTime"] <= end_window) 
                    ].copy()
        
    
        self.daily = (
                    df_filtered
                    .groupby(["Animal", "Phase", "StartDate", "Corner"])[["LickNumber", "NosepokeNumber"]]
                    .sum()
                    .unstack(fill_value=0)
                    .reset_index()
                    .copy()
                )
        
        self.daily.columns = [
            f'{measure}{corner}'
            for measure, corner in self.daily.columns
        ]

        self.daily.reset_index()

        self.daily = animal_dates.merge(
            self.daily,
            on=["Animal","Phase", "StartDate"],
            how="left"
        )
        self.daily = self.daily.fillna(0)

    def dailyLicks(self):
        animals = sorted(self.mice)
        schedule = self.schedule
        daily_licks = self.daily[self.daily["Phase"] != 0].copy()
        daily_licks["LickSum"] = daily_licks[f'LickNumber{self.alcohol_corners[0]}']+daily_licks[f'LickNumber{self.alcohol_corners[1]}']
        ncols = 3
        nrows = math.ceil(len(animals)/ncols)
        
        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=(16,13),
            sharex=True,
            sharey=True
        )
        
        axes = axes.flatten()
        
        for ax, animal in zip(axes, animals):
        
            d = (
                daily_licks[daily_licks["Animal"] == animal]
                .sort_values("StartDate")
            )
        
            ax.plot(
                d["StartDate"],
                d["LickSum"],
                "-o",
                color=self.mice_info[animal]['Color'],
                linewidth=2,
                markersize=5
            )
        
                
            ax.axvspan(
                schedule['Habituation']['Start'],
                schedule['Habituation']['End'],
                color=self.phase_colors["Habituation"],
                alpha=0.30
            )
            ax.axvspan(
                schedule['Priming']['Start'],
                schedule['Priming']['End'],
                color=self.phase_colors["Priming"],
                alpha=0.30
            )      
        
            wd = self.mice_info[animal]["Withdrawal"]
            rp = self.mice_info[animal]["Relapse"]
        
            ax.axvspan(
                schedule['AlcoholConsumption']['Start'],
                wd,
                color=self.phase_colors["AlcoholConsumption"],
                alpha=0.20
            )
            ax.axvspan(
                wd,
                rp,
                color=self.phase_colors["Withdrawal"],
                alpha=0.25
            )
        
            ax.axvline(
                rp,
                color=self.phase_colors["Relapse"],
                linestyle="--",
                linewidth=2
            )
        
        
            ax.set_title(f"Animal {animal}", fontsize=11)
            ax.tick_params(axis="x", rotation=45)
        
        # Remove empty axes
        for ax in axes[len(animals):]:
            fig.delaxes(ax)
        
        fig.suptitle(
            "Daily Lick Number (Corners "+str(self.alcohol_corners[0])+" and "+str(self.alcohol_corners[1])+", 14:00–16:00)",
            fontsize=18,
            fontweight="bold"
        )
        
        fig.supxlabel("Date")
        fig.supylabel("Daily Lick Number")
        
        plt.tight_layout()
        plt.show()
    def dailyNosepokes(self):
        animals = sorted(self.mice)
        daily_nosepoke = self.daily[self.daily["Phase"] != 0].copy()
        daily_nosepoke["NosepokeSum"] = daily_nosepoke[f'NosepokeNumber{self.alcohol_corners[0]}']+daily_nosepoke[f'NosepokeNumber{self.alcohol_corners[1]}']
        ncols = 3
        nrows = math.ceil(len(animals)/ncols)

        fig, axes = plt.subplots(
            nrows,
            ncols,
            figsize=(18,14),
            sharex=True,
            sharey=True
        )

        axes = axes.flatten()

        for ax, animal in zip(axes, animals):

            d = (
                daily_nosepoke[daily_nosepoke["Animal"] == animal]
                    .sort_values("StartDate")
            )

            colors = d["Phase"].map(self.phase_colors)

            bars = ax.bar(
                d["StartDate"],
                d["NosepokeSum"],
                color=colors,
                edgecolor="black",
                linewidth=0.5,
                width=0.8
            )

            # Write values on bars
            for bar in bars:

                height = bar.get_height()

                if height > 0:

                    ax.text(
                        bar.get_x() + bar.get_width()/2,
                        height,
                        f"{int(height)}",
                        ha="center",
                        va="bottom",
                        fontsize=6,
                        rotation=90
                    )

            ax.set_title(f"Animal {animal}", fontsize=11)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)

        # Remove empty axes
        for ax in axes[len(animals):]:
            fig.delaxes(ax)

        # Legend
        legend_handles = [
            mpatches.Patch(color=color, label=phase)
            for phase, color in self.phase_colors.items()
        ]

        fig.legend(
            handles=legend_handles,
            loc="upper center",
            ncol=6,
            frameon=False,
            fontsize=10
        )

        fig.suptitle(
            "Daily Nosepoke Number (Corners "+str(self.alcohol_corners[0])+" and "+str(self.alcohol_corners[1])+", 14:00–16:00)",
            fontsize=18,
            fontweight="bold"
        )

        fig.supxlabel("Date", fontsize=14)
        fig.supylabel("Daily Lick Number", fontsize=14)

        plt.tight_layout(rect=[0,0,1,0.95])

        plt.show() 
    def relapseDrinking(self):
        relapse = self.daily[self.daily["Phase"] == "Relapse"].copy()
        groups = list(set(animal["Group"] for animal in self.mice_info.values()))
        group_map = {
            animal: features["Group"]
            for animal, features in self.mice_info.items()
        }
        relapse["Group"] = relapse["Animal"].map(group_map)
        relapse["LickSum"] = relapse[f'LickNumber{self.alcohol_corners[0]}']+relapse[f'LickNumber{self.alcohol_corners[1]}']

        means = []
        sems = []

        # ==========================
        # Mean ± SEM
        # ==========================
        for g in groups:

            vals = relapse.loc[
                relapse["Group"] == g,
                "LickSum"
            ]

            means.append(vals.mean())
            sems.append(vals.sem())

        plt.figure(figsize=(7,6))

        plt.bar(
            groups,
            means,
            yerr=sems,
            color=["white", "tab:blue"],
            edgecolor="black",
            linewidth=2,
            capsize=6,
            width=0.6,
            zorder=1
        )

        # ==========================
        # Individual animals
        # ==========================

        for i, g in enumerate(groups):

            d = relapse[relapse["Group"] == g]

            for _, row in d.iterrows():

                x = np.random.normal(i, 0.1)

                plt.scatter(
                    x,
                    row["LickSum"],
                    s=110,
                    color=self.mice_info[row["Animal"]]["Color"],
                    edgecolor="black",
                    linewidth=0.8,
                    zorder=10,
                    label=str(row["Animal"])
                )

        # ==========================
        # Remove duplicate legend entries
        # ==========================

        handles, labels = plt.gca().get_legend_handles_labels()
        unique = dict(zip(labels, handles))

        plt.legend(
            unique.values(),
            unique.keys(),
            title="Animal",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            fontsize=9
        )

        plt.ylabel("Lick Number")
        plt.xlabel("")
        plt.title("Alcohol drinking during relapse (14:00–16:00)")
        plt.tight_layout()
        plt.show() 