import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Plotter :

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_xlim(0, 5)
        self.ax.grid()
        self.xdata, self.ydata = [], []
        self.t = 0

    def data_gen(self):
        cnt = 0
        while cnt < 1000:
            cnt+=1
            self.t += 0.05
            yield self.t, np.sin(2*np.pi*self.t) * np.exp(-self.t/10.)

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
        ani = animation.FuncAnimation(self.fig, self.run, self.data_gen, blit=True, interval=10, repeat=False)
        plt.show()
 
if __name__=='__main__':
    Plotter().start()