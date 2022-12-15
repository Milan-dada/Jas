import logging
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import traceback

NumberOfPlot:  int = 3

CANVAS_WIDTH:  int = 8
CANVAS_HEIGHT: int = 8

images = []
prev_images = []

def draw_plot():

    portfile = os.getcwd() + '\\Log\\' + "Ports.txt"
    portlist = np.loadtxt(portfile, dtype = str,delimiter=",")
    ax = {}

    print("current port list:")
    print(portlist)

    if portlist.shape == (2,):
        portlist = portlist[np.argsort(portlist)]
        numofport = 1
    else:
        portlist = portlist[np.argsort(portlist[:, 0])]
        numofport = len(portlist)    
  
    SCREEN_NUMBER_X: int = 1
    SCREEN_NUMBER_Y: int = len(portlist)

    xlable = ['y[0]','y[1]','y[2]','y[3]','y[4]','y[5]','y[6]','y[7]']
    ylable = ['x[7]','x[6]','x[5]','x[4]','x[3]','x[2]','x[1]','x[0]']
    init_list = [0,1,2,3,4,5,6,7]
    CANVAS_HEIGHT: int = 8

    if numofport > NumberOfPlot:
        SCREEN_NUMBER_X = int(SCREEN_NUMBER_Y/NumberOfPlot) + 1
        SCREEN_NUMBER_Y = int(SCREEN_NUMBER_Y/SCREEN_NUMBER_X) + 1

    fig = plt.figure(figsize=(5*SCREEN_NUMBER_Y+2,SCREEN_NUMBER_X*5), clear=True)

    if numofport == 1:
        ax[0] = fig.add_subplot(SCREEN_NUMBER_X,SCREEN_NUMBER_Y,1)
        ax[0].title.set_text('ID:' + portlist[0][0] + ' ;Ports:' + portlist[0][1])
        ax[0].pcolormesh(np.zeros((CANVAS_WIDTH, CANVAS_HEIGHT)),cmap = "turbo", vmin = 21, vmax = 28)
        plt.xticks(init_list,xlable)
        plt.yticks(init_list,ylable)
    elif numofport > 1:    
        for port in portlist:
            # add every single subplot to the figure with a for loop
            index = np.where(portlist == port)[0][0] + 1            
            ax[index-1] = fig.add_subplot(SCREEN_NUMBER_X,SCREEN_NUMBER_Y,index)
            ax[index-1].title.set_text('ID:' + portlist[index-1][0] + ' ;Ports:' + portlist[index-1][1])
            ax[index-1].pcolormesh(np.zeros((CANVAS_WIDTH, CANVAS_HEIGHT)),cmap = "turbo", vmin = 21, vmax = 28)
            plt.xticks(init_list,xlable)
            plt.yticks(init_list,ylable)
    fig.canvas.draw()
    fig.show()

    while True:
        for i in range(len(ax)):
            if numofport == 1:
                filename = os.getcwd() + '\\Log\\Sensor' + portlist[1] + ".txt"
            elif numofport > 1:
                filename = os.getcwd() + '\\Log\\Sensor' + portlist[i][1] + ".txt"
            File_data = []
            while True:
                f = open(filename, "r")                        
                line = f.readline()
                index = 0
                while line:
                    line = line.strip("\n")
                    line = line.split(",")
                    File_data.append([])
                    for item in line:
                        File_data[index].append(float(item))
                    line = f.readline()
                    index += 1
                f.close()
                if len(File_data) > 0:
                    break
            
            if not File_data:
                print("-----------------------------No File data-----------------------------")

            File_data.reverse()
            t_start = time.time()
            heatmap = ax[i].pcolormesh(File_data,cmap = "turbo", vmin = 21, vmax = 28)
            ax[i].draw_artist(ax[i].patch)
            ax[i].draw_artist(heatmap)
            fig.canvas.blit(ax[i].bbox)
            
            t_end = time.time()
            logging.debug("fps_draw = {0}".format(999 if t_end == t_start else 1/(t_end-t_start)))
        fig.canvas.flush_events()
        time.sleep(0.1)

def main():
    try:
        draw_plot()
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()