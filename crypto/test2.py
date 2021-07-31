import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp
from multiprocessing import freeze_support,Manager
import time
from matplotlib.animation import FuncAnimation
plt.style.use('fivethirtyeight')

my_c = ['x','y']
initial = [[1,3],[2,4],[3,8],[4,6],[5,8],[6,5],[6,2],[7,7]]
df = pd.DataFrame(columns=my_c)

def data(List):
    
    for i in initial:
     
        List.append(i) # appending values
        time.sleep(1) # waiting 1 second #
        List.pop(0) # cleaning list

def animate(self,List):
    global df

    lst = list(List) # converting proxy back to list
    
    if len(lst) != 0 : # checking list isnt empty to avoid erros
     
        df.loc[len(df.index+1)] = lst  #appendig values to dataframe
        plt.plot(df['x'],df['y'],label = "Price")#reploting it
        plt.tight_layout()

def run(List): 
    ani = FuncAnimation(plt.gcf(),animate,fargs= List, interval=1000) #passes shared List as an argument to Animate function  
    plt.show() 

if __name__ == '__main__':
    manager = mp.Manager() # creates manager object
    List  =  manager.list() # list to be shared amoung processes is created 
    freeze_support()
    p1 = mp.Process(target = run,args =(List,)) #process is created
    p2 = mp.Process(target = data,args=(List,)) # process that generates and updates data is created
    p2.start() # process starts 
    p1.start() # process starts
    p2.join() # join makes sure process ends
    p1.join() # join makes sure process ends





