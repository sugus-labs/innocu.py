import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pathlib
from datetime import datetime

def create_daily_charts(x,y):

    plt.rc('font', size = 22)  
    plt.rc('axes', titlesize = 22)   
    plt.rc('axes', labelsize = 20)  
    plt.rc('xtick', labelsize = 18)  
    plt.rc('ytick', labelsize = 18)
    plt.rc('legend', fontsize = 18) 
    plt.rc('figure', titlesize = 22) 

    fig, ax = plt.subplots(figsize = (14, 7))

    ax.bar(x, y, color = 'yellowgreen')
    ax.set(xlabel = 'Hours', ylabel = 'KW')

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"

    dir = pathlib.Path(__file__).parent.absolute()
    folder = r"charts/daily"
    path_plot = "{0}/{1}/{2}".format(dir, folder, filename)
    
    fig.savefig(path_plot, dpi = fig.dpi)

    return path_plot, dir

#path_plot, dir = create_daily_charts(x, y)