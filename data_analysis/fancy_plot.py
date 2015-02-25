from data_access import *
from data_preprocessing import *
from pylab import *

def boring_plot(subject, session):
    df = get_physio_data(subject, session)
    time = array(df['time'])
    ecg = array(df['ecg'])
    gsr = array(df['gsr'])
    print(gsr.dtype)
    print(len(gsr))
    #gsr = low_pass(gsr,'cos',100)
    #print(len(gsr))
    #plot(time,ecg)
    figure()
    title(str(subject)+'_'+str(session))
    plot(time,gsr)
    #savefig(str(subject)+'_'+str(session)+'.png')
    show()

    print(gsr)

"""
def plot_with_backcolors(x_axis_divisions, colors, graph_data, figure):
    import matplotlib.pyplot as plt
    import matplotlib.collections as collections

    figure = plt.figure()
    ax = figure.add_subplot(111)

    # Plot your own data here
    ax.plot(graph_data[0], graph_data[1])

    xad = list(copy(x_axis_divisions))
    #xad.append(graph_data[0][-1])
    xranges = [(xad[i],xad[i+1]-xad[i]) for i in xrange(len(xad)-1)]
    yrange = (0, 15)
    def color_choice(color_code):
        if color_code == 0:
            return 'purple'
        elif color_code == 1:
            return 'green'
        elif color_code == 2:
            return 'red'
        elif color_code == 3:
            return 'yellow'
        elif color_code == 4:
            return 'blue'
        elif color_code == 5:
            return 'grey'
        elif color_code == 6:
            return 'white'

    colors = [color_choice(color_code) for color_code in colors]

    for i in xrange(len(xranges)) :
        coll = collections.BrokenBarHCollection([xranges[i]], yrange, facecolor=colors[i], alpha=0.5)
        ax.add_collection(coll)

    return figure"""