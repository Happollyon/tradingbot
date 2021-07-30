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
        #every 1 sec the list created with the manager.list() is updated
        #print(f"list in loop {List}")#making sure list is not empty
       
        List.append(i)
        time.sleep(1)
        List.pop(0)
       
       

def animate(self,List):
    print(f"list in animate {List}")# prints <class 'int'> instead of  <class 'multiprocessing.managers.ListProxy'>
    global df
    lst = list(List)
    if len(lst) != 0 :
        df = df.append({'x':lst[0],'y':lst[1]}, ignore_index = True)
        plt.plot(df['x'],df['y'],label = "Price")
        plt.tight_layout()

def run(List): 
    print(f"run funciton {type(List)}") # prints  <class 'multiprocessing.managers.ListProxy'>
    ani = FuncAnimation(plt.gcf(),animate,fargs= List, interval=1000) #passes List as an argument to Animate function  
    plt.show()

if __name__ == '__main__':
    manager = mp.Manager()
    List  =  manager.list()
    freeze_support()
    p1 = mp.Process(target = run,args =(List,))
    p2 = mp.Process(target = data,args=(List,))
    p2.start()
    p1.start()
    p2.join()
    p1.join()

