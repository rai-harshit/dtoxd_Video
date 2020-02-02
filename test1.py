#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import queue
import vlc
import subprocess
import threading
import time
import random
import os
import time
import keras
import re
from keras.models import load_model
from keras.backend import clear_session
import cv2 as cv
import numpy as np
from numpy.ma import frombuffer
pred_queue=queue.Queue()
video_frame=queue.Queue()
global prediction
prediction=[]
global keyFrameTime
keyFrameTime=""
global currentPredTime
currentPredTime=0
def time_extractor():
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    filename="C:\\Users\\vishw\\Documents\\dtoxd\\dtoxd_Video\\test.mp4"
    cmd ="ffprobe -select_streams v -skip_frame nokey -show_frames -show_entries frame=pkt_pts_time,pict_type "+filename
    print("test121")
    # cmd ="ffprobe -select_streams v -skip_frame nokey -show_frames -show_entries frame=pkt_pts_time,pict_type test.mp4"
    s1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,stdin=subprocess.DEVNULL,startupinfo=startupinfo)
    try:
        f = s1.stdout.read()
        f=f.decode('ascii')
        f=re.findall(r'\d+\.\d+',f)
        global keyFrameTime
        keyFrameTime=f
    except ValueError as e:
        print("Error")
    filename="test.mp4"
    s1.kill()
    print(keyFrameTime)


def frame_extractor():
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    filename="C:\\Users\\vishw\\Documents\\dtoxd\\dtoxd_Video\\test.mp4"
    print(keyFrameTime)
    cmd = 'ffmpeg -v error -skip_frame nokey -i "{}" -vsync vfr -f image2pipe -vcodec rawvideo -pix_fmt bgr24 -s 300x300 - '.format(filename)
    s1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,stdin=subprocess.DEVNULL,startupinfo=startupinfo)
    while True:
        try:
            f = s1.stdout.read(270000)
            frame = frombuffer(f,dtype=np.uint8).reshape((1,300,300,3))
            video_frame.put(frame)
        except ValueError as ve:
            print(ve)
            break
    print("done frame extraction")
    video_frame.put("XOXO")
    print("pipe size",video_frame.qsize())


def predictor():
    clear_session()
    model=load_model("model.h5")
    x=""
    print("prediction started")
    while(x!="XOXO"):
        x=video_frame.get()
        if(x!="" and x is not None):
            if(x=="XOXO"):
                img=None
            else:
                img = np.fromstring(x, np.uint8).reshape( 300, 300, 3 )
                # img = cv.cvtColor(image,cv.COLOR_BGR2RGB)
            # img=cv.imread(image)
            if(img is not None):
                height, width = img.shape[:2]
                if(height>48 and width>48):
                    img=cv.resize(img,(300,300))
                    img=cv.resize(img,(300,300))
                    img=np.array(img)
                    image = np.reshape(img,(1,300,300,3))
                    l=model.predict(image)
                    global prediction
                    if(l[0][0]>l[0][1]):
                        prediction.append("1")
                    else:
                        prediction.append("0")
                print("Predicting")
    # print(prediction)
                    

        
def vlc_player():
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    filename="C:\\Users\\vishw\\Documents\\dtoxd\\dtoxd_Video\\test.mp4"
    cmd ="ffprobe -select_streams v -skip_frame nokey -show_frames -show_entries frame=pkt_pts_time,pict_type test.mp4"
    s1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,stdin=subprocess.DEVNULL,startupinfo=startupinfo)
    try:
        f = s1.stdout.read()
        f=f.decode('ascii')
        f=re.findall(r'\d+\.\d+',f)
        global keyFrameTime
        keyFrameTime=f
    except ValueError as e:
        print("Error")
    s1.kill()
    print(keyFrameTime)
    i=vlc.Instance('--fullscreen')
    # i.get_log_verbosity
    p=i.media_player_new()
    m=i.media_new('test.mp4')
    m.get_mrl() 
    p.set_media(m)
    count=-1
    print("Inside VLC")
    # global keyFrameTime
    maxCount=len(keyFrameTime)
    while(len(keyFrameTime)<1):
        pass
    global prediction
    count+=1
    if(int(float(keyFrameTime[0]))==0):
        while(len(prediction)<count):
            time.sleep(10)
            print("Sleeping")
            pass
        if(int(prediction[count])==0):
            print("Clear count:",count)
            p.video_set_logo_string(1,"logo.jpg")
            # p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,300)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
            p.play()
        else:
            p.video_set_logo_string(1,"logo.jpg")
            print("blurry count:",count)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,500)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,1)
            p.play()
        print("1st inncrement",count)
    else:
        p.video_set_logo_string(1,"logo.jpg")
        p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
        p.play()
    while(str(p.get_state())!='State.Ended'):
        curr_tsp=p.get_time()
        curr_tsp=int(curr_tsp/1000)
        if(len(keyFrameTime)==count):
            pass 
        else:
            p.pause()
            while(len(prediction)<count):
                print("Prediction less than count")
                pass
            loop=int(float(keyFrameTime[count]))
            print("Count, KeyFrameTime length,prediction,curr_tsp,loo[]",count,len(keyFrameTime),prediction[count],curr_tsp,loop)
            if(int(prediction[count-1])==0):
                p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
            else:
                p.video_set_logo_string(1,"logo.jpg")
                p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,500)
                p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,1)
            while(curr_tsp<=loop):
                print("Inside count curr_TSP",count,curr_tsp)
                curr_tsp=p.get_time()
                curr_tsp=int(curr_tsp/1000)
                p.play()
            count+=1
    # print(keyFrameTime)
    # print(prediction)
    # print("Exited")

t4=threading.Thread(target=frame_extractor)
t1=threading.Thread(target=vlc_player)
t3=threading.Thread(target=predictor)
# t2.start()
t3.start()
t4.start()
t3.join()

t1.start()

