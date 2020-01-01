from functools import partial
import math
import numpy as np
import matplotlib as mpl
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import strafevis.strafe_stats
from matplotlib import cm
from matplotlib.colors import Colormap
from matplotlib.widgets import Slider, Button, RadioButtons

class AngleMap(Colormap):
    def __init__(self, accels, max_accel=None, min_accel=None):
        self.accels = accels
        self.points = len(self.accels)
        if min_accel is not None:
            self.min_accel = min_accel
        else:
            self.min_accel = np.min(accels)
        if max_accel is not None:
            self.max_accel = max_accel
        else:
            self.max_accel = np.max(accels)
        Colormap.__init__(self, None, 255)

    def get_accel(self, val):
        val *= self.points
        val = int(val)
        return self.accels[val]

    def __call__(self, X, alpha=None, bytes=None):
        rgba = np.zeros(shape=(len(X), 4))

        for index, val in enumerate(X):
            accel = self.get_accel(val)
            rgba[index,3] = 1

            if accel < 0:
                accel = max(accel, self.min_accel)
                rgba[index,0] = accel / self.min_accel
            elif accel > 0:
                accel = min(accel, self.max_accel)
                rgba[index,1] = accel / self.max_accel

        return rgba

def animate_plot_to_pictures(min_speed, max_speed, pictures):
    axcolor = 'lightgoldenrodyellow'
    axspeed = plt.axes([0.125, 0.05, 0.65, 0.03], facecolor=axcolor)
    sspeed = Slider(axspeed, 'Speed', 0, max_speed, valinit=0, valstep=1)

    for i in range(pictures):
        speed = 1.0 * i / (pictures-1) * max_speed + min_speed
        accels, rads = strafevis.strafe_stats.get_stats(720, strafevis.strafe_stats.StatType.ACCEL, speed=speed)
        display_axes = plt.subplot(1, 1, 1, polar=True)
        norm = mpl.colors.Normalize(0.0, 2 * np.pi)
        cmap = AngleMap(accels)

        cb = mpl.colorbar.ColorbarBase(display_axes, cmap=cmap,
                                       norm=norm,
                                       orientation='horizontal')

        # aesthetics - get rid of border and axis labels
        cb.outline.set_visible(False)
        display_axes.set_axis_off()
        sspeed.set_val(speed)
        plt.savefig('pic_%04d.png' % i)

def plot():
    accels, rads = strafevis.strafe_stats.get_stats(1000, strafevis.strafe_stats.StatType.ACCEL, speed=100)
    display_axes = plt.subplot(1, 1, 1, polar=True)
    norm = mpl.colors.Normalize(0.0, 2 * np.pi)
    cmap = AngleMap(accels)

    cb = mpl.colorbar.ColorbarBase(display_axes, cmap=cmap,
                                   norm=norm,
                                   orientation='horizontal')

    # aesthetics - get rid of border and axis labels
    cb.outline.set_visible(False)
    display_axes.set_axis_off()

    def update(val):
        accels, rads = strafevis.strafe_stats.get_stats(1000, strafevis.strafe_stats.StatType.ACCEL, speed=sspeed.val)
        cmap = AngleMap(accels)
        cb = mpl.colorbar.ColorbarBase(display_axes, cmap=cmap,
                                       norm=norm,
                                       orientation='horizontal')

    axcolor = 'lightgoldenrodyellow'
    axspeed = plt.axes([0.125, 0.05, 0.65, 0.03], facecolor=axcolor)
    sspeed = Slider(axspeed, 'Speed', 0, 1000.0, valinit=320, valstep=1)
    sspeed.on_changed(update)

    plt.show()  # Replace with plt.savefig if you want to save a file
