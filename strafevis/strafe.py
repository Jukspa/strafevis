import math
import numpy as np
from enum import Enum


PITCH = 0
YAW = 1
ROLL = 2


class Engine(Enum):
    QUAKE = 0
    GOLDSRC = 1
    SOURCE = 2


def normalize(vec):
    length = np.linalg.norm(vec)
    if length > 0:
        vec /= length


def xy_length(vec):
    return math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2))


def rad2deg(rad):
    return rad * 180 / math.pi


def deg2rad(deg):
    return deg * math.pi / 180

def normalize_deg(deg):
    a = math.fmod(deg, 360)
    if a >= 180:
        a -= 360
    elif a < -180:
        a += 360
    return a

def vector_angles(forward):
    pseudoup = np.zeros(3)
    pseudoup[2] = 1
    angles = np.zeros(3)

    left = np.cross(pseudoup, forward)
    normalize(left)
    xy = xy_length(forward)

    if xy > 0.001:
        angles[YAW] = rad2deg(math.atan2(forward[1], forward[0]))
    else:
        angles[YAW] = rad2deg(math.atan2(-left[1], left[0]))
    angles[PITCH] = rad2deg(math.atan2(-forward[2], xy))
    # roll = kek
    return angles

class StrafeData:
    def __init__(self, speed=0, surfacefriction=1, friction=4, accel=10, airaccel=10, frametime=0.01,
                maxspeed=320, wishspeed_cap=30, stopspeed=100, ground=False, engine=Engine.GOLDSRC):
        self.velocity = np.zeros(3)
        self.velocity[0] = -speed
        self.surfacefriction = surfacefriction
        self.friction = friction
        self.accel = accel
        self.airaccel = airaccel
        self.frametime = frametime
        self.maxspeed = maxspeed
        self.wishspeed_cap = wishspeed_cap
        self.stopspeed = stopspeed
        self.ground = ground
        self.engine = engine

    @staticmethod
    def calc_weighted_average(data1, data2, ratio):
        if ratio < 0 or ratio > 1:
            raise Exception("Ratio is not valid")
        elif data1.ground != data2.ground:
            raise Exception("data1.ground != data2.ground")
        elif data1.engine != data2.engine:
            raise Exception("data1.engine != data2.engine")

        ratio2 = 1 - ratio
        out = StrafeData()
        out.ground = data1.ground
        out.engine = data1.engine
        out.velocity = ratio * data1.velocity + ratio2 * data2.velocity
        out.surfacefriction = ratio * data1.surfacefriction + ratio2 * data2.surfacefriction
        out.friction = ratio * data1.friction + ratio2 * data2.friction
        out.accel = ratio * data1.accel + ratio2 * data2.accel
        out.airaccel = ratio * data1.airaccel + ratio2 * data2.airaccel
        out.frametime = ratio * data1.frametime + ratio2 * data2.frametime
        out.maxspeed = ratio * data1.maxspeed + ratio2 * data2.maxspeed
        out.wishspeed_cap = ratio * data1.wishspeed_cap + ratio2 * data2.wishspeed_cap
        out.stopspeed = ratio * data1.stopspeed + ratio2 * data2.stopspeed

        return out

    def speed_2d(self):
        return xy_length(self.velocity)

    def yaw(self):
        angles = vector_angles(self.velocity)
        return angles[YAW]


def gm_friction(data):
    speed = data.speed_2d()
    if speed < 0.1:
        return
    drop = 0

    if data.ground:
        friction = data.friction * data.surfacefriction
        control = max(speed, data.stopspeed)
        drop += control * friction * data.frametime

    newspeed = max(speed - drop, 0)
    if newspeed != speed:
        newspeed /= speed
        data.velocity /= newspeed

def gm_accelerate(data, angle):
    if data.ground:
        wishspeed = data.maxspeed
    else:
        wishspeed = data.wishspeed_cap
    currentspeed = data.speed_2d() * math.cos(deg2rad(angle))
    addspeed = wishspeed - currentspeed

    if addspeed <= 0:
        return

    if data.ground and data.engine == Engine.GOLDSRC:
        accelspeed = data.accelerate * data.frametime * wishspeed * data.surfacefriction
    elif data.ground:
        accelspeed = data.accelerate * data.frametime * wishspeed
    else:
        accelspeed = data.airaccel * data.frametime * wishspeed

    theta = deg2rad(data.yaw() + angle)
    wishdir = [math.cos(theta), math.sin(theta)]
    accelspeed = min(addspeed, accelspeed)

    data.velocity[0] += wishdir[0] * accelspeed
    data.velocity[1] += wishdir[1] * accelspeed

def strafe(data, angle):
    angle = normalize_deg(angle)
    gm_friction(data)
    gm_accelerate(data, angle)
