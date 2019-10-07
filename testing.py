#!/usr/bin/env python
# coding: utf-8

# In[1]:


import vlc
import threading

i=vlc.Instance('--fullscreen')

i.get_log_verbosity

p=i.media_player_new()
m=i.media_new('a.mp4')

m.get_mrl()

p.set_media(m)



# In[2]:


import queue
import random
import time
pred_queue=queue.Queue()
def test1():
    pred=0
    while(pred!="End"):
        pred=input("Enter num")
        pred_queue.put(pred)
        time.sleep(10)
        
# def test1():
#     pred=random.randint(1,67)
#     last_rand=0
# #     print(pred)
#     if(last_rand<pred):
#         last_rand=pred
#         pred_queue.put(pred)
#         print(pred)
#     if(last_rand==67):
#         pred_queue.put("Stop")
        
def test2():
    p.play()
    last_blr=-1
    p.video_set_logo_string(1,"logo.jpg")
    while(str(p.get_state()) != 'State.Ended'):
        curr_tsp = p.get_time()
        curr_tsp = int(curr_tsp/1000)
        #print(curr_tsp)
        if(last_blr<curr_tsp):
            blr=pred_queue.get()
            if(blr!="End"):
                blr=int(blr)
                last_blr=blr
#         print(blr,curr_tsp)
        if(blr==curr_tsp):
#         if (curr_tsp>blur_timestamp[i][0]*1000 and curr_tsp<blur_timestamp[i][1]*1000):
    #         p.video_set_logo_string(vlc.VideoLogoOption.logo_x,"0")
    #         p.video_set_logo_string(vlc.VideoLogoOption.logo_y,"0")
    #         p.video_set_logo_string(vlc.VideoLogoOption.logo_repeat,"1")
            p.video_set_logo_int(vlc.VideoLogoOption.logo_opacity,300)
            p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,1)
            p.audio_set_mute(True)
        else:
            p.video_set_logo_int(vlc.VideoLogoOption.logo_enable,0)
            p.audio_set_mute(False)
#         if curr_tsp > blur_timestamp[i][1]*1000 and i<len_btsp-1:
#             i+=1
    p.stop()

t2=threading.Thread(target=test1)
t1=threading.Thread(target=test2)
t1.start()
t2.start()


# In[ ]:





# In[ ]:





# In[ ]:




