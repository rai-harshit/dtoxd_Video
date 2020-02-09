#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import queue
from multiprocessing.connection import Client
import sys
import vlc
import subprocess
import threading
import time
import random
import os
import time
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.backend import clear_session
import cv2 as cv
from subprocess import Popen
from subprocess import PIPE
import numpy as np
from numpy.ma import frombuffer
from multiprocessing import Process
pred_queue=queue.Queue()
video_frame=queue.Queue()
global prediction
prediction=[]
global keyFrameTime
keyFrameTime=[]
global currentPredTime
currentPredTime=0
global start_vlc
start_vlc=0


def frame_extractor(filename):
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    cmd = 'ffmpeg -v error -skip_frame nokey -i "{}" -vsync vfr -f image2pipe -vcodec rawvideo -pix_fmt bgr24 -s 224x224 - '.format(filename)
    s1 = subprocess.Popen(cmd, stdout=subprocess.PIPE,stdin=subprocess.DEVNULL,startupinfo=startupinfo)
    while True:
        try:
            f = s1.stdout.read(150528)
            if(len(f)!=0):
                frame = frombuffer(f,dtype=np.uint8).reshape((1,224,224,3))

                video_frame.put(frame)
            else:
                break
        except ValueError as ve:
            print(ve)
            break
    video_frame.put("XOXO")


def server_get_prediction():
    x=""
    print("prediction started")
    count=0
    while(x!="XOXO"):
        x=video_frame.get()
        if(x!="" and x is not None):
            if(x=="XOXO"):
                img=None
            else:
                img = np.fromstring(x, np.uint8).reshape( 224, 224, 3 )
                # img = cv.cvtColor(image,cv.COLOR_BGR2RGB)
            # img=cv.imread(image)
            if(len(img)!=0):
                height, width = img.shape[:2]
                if(height>48 and width>48):
                    img=cv.resize(img,(224,224))
                    img=cv.resize(img,(224,224))
                    img=np.array(img)
                    image = np.reshape(img,(1,224,224,3))
                    address = ('localhost', 6969)
                    conn = Client(address, authkey=b'dtoxd-data-incoming')
                    print("Connection created")
                    try:
                        conn.send(['f',image])
                        pred = conn.recv()
                        # print(pred)
                        count+=1
                        if pred ==0:
                            prediction.append("0")
                        else:
                            prediction.append("1")
                    except:
                        print("Server Issue")
                global start_vlc
                if(len(prediction)>=20 and start_vlc==0):
                    time.sleep(10)
    print("*************",count)


def keyFrameTime_Exctraction(filename):
    command = "ffprobe -select_streams v -skip_frame nokey -show_frames -show_entries frame=pkt_pts_time,pict_type {}".format(filename)
    pipe = Popen(command,shell=True,stdout=PIPE,stderr=PIPE)    
    while True:         
        line = pipe.stdout.readline()
        if line: 
            line1=str(line)
            numbers = re.findall('\d*\.?\d+',line1)            
            if(len(numbers)==1):
                global keyFrameTime
                keyFrameTime.append(numbers[0])
        else:
            break

        
def vlc_player(filename):
    global keyFrameTime
    i=vlc.Instance('--fullscreen')
    # i.get_log_verbosity
    p=i.media_player_new()
    m=i.media_new(filename)
    m.get_mrl() 
    p.set_media(m)
    count=-1
    maxCount=len(keyFrameTime)
    while(len(keyFrameTime)<1):
        time.sleep(1)
    global prediction
    if(len(keyFrameTime)>=20):
        while(len(prediction)<20):
            time.sleep(1)
    else:
        while(len(prediction)<len(keyFrameTime)):
            time.sleep(1)

    count+=1
    if(int(float(keyFrameTime[0]))==0):
        while(len(prediction)<count):
            time.sleep(10)
            # print("Sleeping")
        if(int(prediction[count])==0):
            # print("Clear count:",count)
            p.video_set_logo_string(1,"logo.jpg")
            # p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,224)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
            p.play()
        else:
            p.video_set_logo_string(1,"logo.jpg")
            # print("blurry count:",count)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,500)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,1)
            p.play()
        # print("1st inncrement",count)
    else:
        p.video_set_logo_string(1,"logo.jpg")
        p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
        p.play()
    global start_vlc
    start_vlc=1
    while(str(p.get_state())!='State.Ended'):
        curr_tsp=p.get_time()
        curr_tsp=int(curr_tsp/1000)
        if(len(keyFrameTime)==count):
            pass 
        else:
            p.pause()
            while(len(prediction)<count):
                # print("Prediction less than count")
                pass
            loop=int(float(keyFrameTime[count]))
            # print("Count, KeyFrameTime length,prediction,curr_tsp,loo[]",count,len(keyFrameTime),prediction[count],curr_tsp,loop)
            if(int(prediction[count-1])==0):
                p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
            else:
                p.video_set_logo_string(1,"logo.jpg")
                p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,500)
                p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,1)
            while(curr_tsp<=loop):
                # print("Inside count curr_TSP",count,curr_tsp)
                curr_tsp=p.get_time()
                curr_tsp=int(curr_tsp/1000)
                p.play()
            count+=1




if __name__ == "__main__":
    filename=sys.argv[1]
    t0=threading.Thread(target=keyFrameTime_Exctraction,args=(filename,))
    t4=threading.Thread(target=frame_extractor,args=(filename,))
    t1=threading.Thread(target=vlc_player,args=(filename,))
    t3=threading.Thread(target=server_get_prediction)
    t0.start()
    time.sleep(2)
    t3.start()
    t4.start()
    t1.start()

    
