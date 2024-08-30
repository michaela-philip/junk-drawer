import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from redlining.census_tract_classification import tract as tract

tract_by_grade_10 = tract.groupby('grade_10')['ownershp'].agg(['min', 'max', 'mean', 'median']).reset_index()
# tract_by_grade_4 = tract.groupby('grade_4')['ownershp'].agg(['min', 'max', 'mean', 'median']).reset_index()

def get_histograms(column):
    unique_grades = sorted(tract[column].unique())
    fig, axes = plt.subplots(2, 5, figsize = (18, 10), sharey = True, sharex = True)
    axes = axes.flatten()
    for ax, grade in zip(axes, unique_grades):
        tract[tract[column] == grade]['ownershp'].hist(ax=ax)
        ax.set_title(f'Grade {grade}')
    plt.subplots_adjust(hspace=0.4)
    fig.suptitle('Home Ownership Rates by HOLC Grade')
    fig.supylabel('Tracts')
    fig.savefig(f'redlining/data/output/ownership_hist_{column}.jpeg', dpi = 300)

get_histograms('grade_10')
get_histograms('grade_4')

