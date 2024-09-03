import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table

from census_tract_classification import tract as tract

def get_histograms(column, categorynum):
    unique_grades = sorted(tract[column].unique())
    fig, axes = plt.subplots(2, int(len(unique_grades) / 2), figsize = (18, 10), sharey = True, sharex = True)
    axes = axes.flatten()
    for ax, grade in zip(axes, unique_grades):
        tract[tract[column] == grade]['ownershp'].hist(ax=ax)
        ax.set_title(f'Grade {grade}')
    plt.subplots_adjust(hspace=0.4)
    fig.suptitle(f'Home Ownership Rates by HOLC Grade ({categorynum} Categories)')
    fig.supylabel('Tracts')
    fig.savefig(f'redlining/data/output/ownership_hist_{column}.jpeg', dpi = 300)

get_histograms('grade_10', 10)
get_histograms('grade_4', 4)

def get_stats_table(column, categorynum):
    pivot_table = tract.pivot_table('ownershp', index=column, aggfunc=['min', 'max', 'mean', 'median'])
    pivot_table.columns = ['Min', 'Max', 'Mean', 'Median']
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    tbl = table(ax, np.round(pivot_table, 3), loc='center', cellLoc='center', colWidths=[0.1]*len(pivot_table.columns))
    plt.title(f'Home Ownership Summary Statistics by HOLC Grade ({categorynum} Categories)')
    plt.tight_layout()
    plt.savefig(f'redlining/data/output/pivot_table_{column}.jpeg', dpi=300, bbox_inches = 'tight')


get_stats_table('grade_10', 10)
get_stats_table('grade_4', 4)