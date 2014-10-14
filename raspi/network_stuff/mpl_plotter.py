import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from udp_connection import BufferedClient

class AnimatedPlotter :

    def __init__(self, data_gen):
        self.data_gen = data_gen
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_xlim(0, 5)
        self.ax.grid()
        self.xdata, self.ydata = [], []

    #def data_gen(self):
    #    cnt = 0
    #    while cnt < 1000:
    #        cnt+=1
    #        self.t += 0.05
    #        yield self.t, np.sin(2*np.pi*self.t) * np.exp(-self.t/10.)

    def run(self, data):
        # update the data
        t,y = data
        self.xdata.append(t)
        self.ydata.append(y)
        xmin, xmax = self.ax.get_xlim()
        
        if t >= xmax:
            self.ax.set_xlim(xmin, 2*xmax)
            self.ax.figure.canvas.draw()
        self.line.set_data(self.xdata, self.ydata)
        
        return self.line,

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=True, interval=50, repeat=False)
        plt.show()

def plot_stream():
    client = BufferedClient()
    
    def data_gen():
        t = 0
        while True :
            line=client.read()
            if len(line) > 0 :
                yield (t,line[0].split()[1])
            else :
                yield (t,0)
            t+=1
    
    plotter = AnimatedPlotter(data_gen)
      
    client.start()
    plotter.start()
    print 'Exit plot_stream!'
    
        
 
if __name__=='__main__':
    plot_stream()
    