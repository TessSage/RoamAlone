#!/usr/bin/env python
from threading import Lock
#import pandas as pd
import time
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import datetime
import RPi.GPIO as GPIO
import PWMClass


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
global url_index
url_index=0
def sensorCallback(channel):
  # Called if sensor output changes
  timestamp = time.time()
  global url_index
  stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
  if GPIO.input(channel):
    # No magnet
    pass
    #url_index+=1
  else:
    # Magnet
    url_index+=1
    global rotation_index, voltage
    global begin_time
    if rotation_index ==0:
         begin_time = time.time()
         voltage = 18
    rotation_index+=1

    
GPIO.setmode(GPIO.BCM)
GPIO.setup(17 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

global pwm
pwm = PWMClass.PWM(channel=19) # set up the output channel 
pwm.configure_PWM(5) #set frequency

global average_power, total_average_power
average_power = 0
global temp_power
temp_power = []
total_average_power = []
global distance
distance=0
global calories
calories=0
global duration
duration=0
global rotation_index
rotation_index=0
global voltage
voltage = 0
global begin_time
begin_time = time.time()
global file_change, url_file
file_change = False
url_file = '/home/pi/RoamAlone/Code/RoamAlone/testing_url_list.txt'

#import automationhat
import os, fnmatch
def get_routes():
    wd = r'/home/pi/RoamAlone/code1/RoamAlone/routes'
    available_routes = []
    route_str = ''
    index = 1
    for root, dirnames, filenames in os.walk(wd):
        for filename in fnmatch.filter(filenames, '*.txt'):
            #available_routes.append(filename)
            print(filename)
            socketio.emit('routes', {'routes':filename, 'count':index})
            index+=1
            #route_str += filename +'\n'
    
def update_power_data(reset=False):
    global average_power, total_average_power, temp_power, pwm
    if pwm.DutyCycle <= 1:
        resistance = 5e6
    else:
        resistance = (5e130)*pwm.DutyCycle**(-65.34)
    global voltage#automationhat.analog.two.read()
    temp_power.append(voltage*voltage/(resistance))
    if voltage ==0:
        average_power =0
    else:
        average_power = round(sum(temp_power)/len(temp_power),2)+ 14
    total_average_power.append(average_power)
    if reset:
        temp_power=[]

def update_trip_data():
    global calories, distance, duration, begin_time, rotation_index, total_average_power
    distance = round(3.14 * 2.2 * rotation_index/1600,2)
    duration = (round((time.time()-begin_time)/60,2)) 
    calories =  round(duration*60*sum(total_average_power)/(len(total_average_power)*4184),2)

def read_url_file(file='/home/pi/RoamAlone/Code/RoamAlone/testing_url_list.txt'):
    contentlist=[]
    with open(file,'r') as f:
        content = f.read()
        contentsplit = content.split('\n')
    for line in contentsplit:
        contentlist.append(line.split(';'))
    return contentlist

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    global url_index
    global pwm, file_change
    
    contentlist = read_url_file()

    time_index = 0
    while True:
        socketio.sleep(.05)
        if file_change:
            contentlist = read_url_file(url_file)
        time_index+=1
        if time_index <9:
            update_power_data()
        else:
            time_index =0
            update_power_data(reset=True)
        update_trip_data()
        pwm.change_PW_elevation_gain(float(contentlist[url_index][1]))
        #print(contentlist[url_index][1])
        #url_index += 1
        if url_index > len(contentlist)-1:
            url_index=0
        
        url = contentlist[url_index][0]
        if url == "":
            url_index += 1
            if url_index > len(contentlist)-1:
                url_index=0
            url = contentlist[url_index][0]
        #url = '"' + url + '"'
        #print('\n\nURLSENT: \n', url)
##        append = 'message ' +str(count)
        count += 1
        socketio.emit('image',{'data': (url), 'count': count},
                      namespace='/test')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('file_choose', namespace='/test')
def file_change(message):
    global file_change, url_file
    session['receive_count'] = session.get('receive_count', 0) + 1
    url_file = r'/home/pi/RoamAlone/code1/RoamAlone/routes/' + message['data'] + '.txt'
    file_change = True
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')

@socketio.on('my_trip_data', namespace='/test')
def trip_data():
    global average_power
    global distance
    global calories
    global duration
    emit('trip_data', {'power': str(average_power), 'distance': str(distance),'calories': str(calories), 'duration': str(duration)}, namespace='/test')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})
    get_routes()


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
