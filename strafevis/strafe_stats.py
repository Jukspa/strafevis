import copy
from enum import Enum
import math
import numpy as np
import strafevis.strafe

class StatType(Enum):
    ACCEL = 0
    ANGLE = 1

def get_ang_accel(data, angle):
    copy_data = copy.deepcopy(data)
    strafevis.strafe.strafe(copy_data, angle)
    diff = math.abs(copy_data.yaw() - data.yaw())
    return diff / data.frametime

def get_accel(data, angle):
    copy_data = copy.deepcopy(data)
    strafevis.strafe.strafe(copy_data, angle)
    diff = copy_data.speed_2d() - data.speed_2d()
    return diff / data.frametime


def get_stats(points, stat_type, **kwargs):
    accels = np.zeros(points)
    rads = np.zeros(points)

    min_angle = 0
    max_angle = 360 - 1.0 / points
    increment = (max_angle - min_angle) / points
    data = strafevis.strafe.StrafeData(**kwargs)
    for i in range(points):
        angle = i * increment + min_angle
        if stat_type == StatType.ACCEL:
            accels[i] = get_accel(data, angle)
        else:
            accels[i] = get_ang_accel(data, angle)
        rads[i] = strafevis.strafe.deg2rad(angle)
    return accels, rads
