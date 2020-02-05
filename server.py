from multiprocessing.connection import Listener
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.backend import set_session, get_session
import threading
import numpy as np
import cv2

global model
global graph
global sess

sess = get_session()
graph = tf.get_default_graph()
model = load_model("model.h5")
print("[INFO] Model loaded.")
address = ('localhost', 6969)

class ServiceInstance(threading.Thread):
    def __init__(self,listener,connection):
        threading.Thread.__init__(self)
        self.listener = listener
        self.conn = connection
        print("[INFO] New connection from : {}".format(self.listener.last_accepted))
    def run(self):
            msg = self.conn.recv()
            if exit == 1:
                self.conn.close()
            if msg is None:
                self.conn.close()
            flag, im_data = msg
            try:
                if flag == "p":
                    im_data = cv2.imread(im_data)
                    im_data = cv2.resize(im_data,(224,224))
                    im_data = cv2.cvtColor(im_data,cv2.COLOR_BGR2RGB)
                    im_data = np.reshape(im_data,(1,224,224,3))
                global model
                global graph
                global sess
                with graph.as_default():
                    set_session(sess)
                    pred = model.predict(im_data)[0]
                print(pred)
                self.conn.send(1 if pred[0]>pred[1] else 0) 
            except:
                print("[ERROR] Issue with the image.")

listener = Listener(address, authkey=b'dtoxd-data-incoming')

try:
    while True:
        print("[INFO] Waiting for new connection.")
        conn = listener.accept()
        newInstance = ServiceInstance(listener,conn)
        newInstance.start()
except KeyboardInterrupt:
    print("[INFO] Closing connection and exiting.")
    conn.close()
    listener.close()
    exit = 1