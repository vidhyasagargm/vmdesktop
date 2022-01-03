from os import stat
from flask import Flask
from flask.templating import render_template
from flask_socketio import SocketIO
import csv
import pyautogui as pg

import eventlet
eventlet.monkey_patch()

pg.FAILSAFE = False

app = Flask(__name__)

socket = SocketIO(app, async_mode='eventlet', cors_allowed_origins = "*")

with open('readings.csv', 'w', newline='') as readings:
    writer = csv.DictWriter(readings, fieldnames=['kal_x', 'vel_x', 'dis_x'])
    writer.writeheader()

class State():

    # Gravity state
    gx = 0
    gy =0 

    # Filter prev acceleration
    xfilt = 0
    yfilt = 0

    # Prev acceleration
    prev_x = 0
    prev_y = 0

    # Uncertainity in estimate
    p_acc = 0.05
    p_vel = 0.05
    p_dis = 0.05

    # Init displacement
    disi = 0
    disinit = 0

    # Kalman gain
    k_acc = 0
    k_vel = 0
    k_dis = 0

    # States of system
    acc = 0
    vel = 0
    veli = 0
    dis = 0

    # Time interval
    t = 0

    # Variance of measurement
    r = 3

    # Process Noise variance
    q = 0.003

@socket.on('move_event', namespace='/')
def move(x, y, z, timestamp):
    """ Your code goes here """
    # Timestamp
    dt = 0
    if State.t != 0:
        dt = (timestamp - State.t) * (10 ** (-9))
    # print("time:", dt, "Timestamp:", timestamp, "Prev Timestamp:", State.t)

    # low pass Filter
    State.gx = 0.9 * State.gx + 0.1 * float(x)
    State.gy = 0.9 * State.gy + 0.1 * float(y)
    fil_x = float(x) - State.gx
    fil_y = float(y) - State.gy

    # """ Time update """

    # # State Extrapolation
    # State.vel += State.acc * dt
    # State.dis += State.vel * dt + State.acc * (0.5 * (dt ** 2))

    # # Covariance Extrapolation
    # State.p_acc += State.q
    # State.p_vel += State.p_acc * dt + State.q
    # State.p_dis += State.p_vel * dt + State.p_acc * (0.5 * (dt ** 2)) 
    

    # """ Measurement update """

    # # Kalman Gain
    # State.k_acc = State.p_acc / (State.p_acc + State.r)
    # State.k_vel = State.p_vel / (State.p_vel + State.r)
    # State.k_dis = State.p_dis / (State.p_dis + State.r)

    # # State update equation
    # State.acc += State.k_acc * (fil_x - State.acc)
    # State.vel += State.k_vel * (x - State.acc) * dt
    # State.dis += State.k_dis * (x - State.acc) * (0.5 * (dt ** 2))

    # # Covariance update equation
    # State.p_acc = (1 - State.k_acc) * State.p_acc
    # State.p_vel = (1 - State.k_vel) * State.p_vel
    # State.p_dis = (1 - State.k_dis) * State.p_dis

    # fil_x = round(fil_x, 3)
    # State.dis += 0.5 * fil_x * (dt ** 2)
    # s = round(State.dis * 100, 2)
    # print(s)    

    # Kalman filter for dummies
    State.p_acc += State.q

    State.k_acc = (State.p_acc)  / (State.p_acc + State.r)

    State.acc += State.k_acc * (fil_x - State.acc)

    State.p_acc = (1 - State.k_acc) * State.p_acc

    # Timestamp Update
    State.t = timestamp

    State.vel = State.veli + (fil_x * dt)


    dis = State.veli * dt + (0.5 * fil_x * (dt ** 2))
    
    if abs(State.vel) < 0.07:
        dis = 0

    if dis != State.disi:
        State.dis += dis

    if State.dis == State.disinit:
        State.dis = 0
    State.disi = dis
    State.disinit = State.dis    
    # if abs(dis) > (2 * (10 ** (-6))): 
    #     State.dis += dis


    # State.dis += 0.5 * State.acc * (dt ** 2)

    # State.dis += State.acc * 0.5 * (dt ** 2)
    # print(round(State.dis * 100, 4))
    # print(State.dis)
    # try:
    #     if(State.dis != State.disi):
    #         pg.moveRel((State.dis * (10 ** 5)), 0)
    #     else:
    #         State.dis = 0    

    #     # pg.moveRel(S, 0)   
    # except Exception as e:
    #     print('Error pg move', e)
    # State.disi = State.dis  
    State.veli = State.vel
    
    with open('readings.csv', 'a', newline='') as readings:
        writer = csv.DictWriter(readings, fieldnames=['kal_x', 'vel_x', 'dis_x'])
        writer.writerow({'kal_x':fil_x, 'vel_x': State.vel, 'dis_x': State.dis})
    print("Read")

@socket.on('connect', namespace='/')
def launch():
    print('Connected')

@socket.on('disconnect', namespace='/')
def close():
    print('Disconnected')

def serve():
    socket.run(app, host='0.0.0.0', port='8080', debug=True, use_reloader=False)
    

if __name__ == '__main__':
    serve()
    
