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
model = load_model("5C_model.h5")
print("Model loaded...")
address = ('localhost', 6969)

class ServiceInstance(threading.Thread):
    def __init__(self,listener,connection):
        threading.Thread.__init__(self)
        self.listener = listener
        self.conn = connection
        print("New connection from : {}".format(self.listener.last_accepted))
    def run(self):
        while True:
            path = self.conn.recv()
            print(path)
            try:
                im = cv2.imread(path)
                im = cv2.resize(im,(224,224))
                im = np.reshape(im,(1,224,224,3))
                global model
                global graph
                global sess
                with graph.as_default():
                    set_session(sess)
                    pred = model.predict(im)
                print(pred)
                self.conn.send(np.argmax(pred[0])) 
            except:
                print("Issue with the image.")
            if path == '':
                self.conn.close()
        self.listener.close()

listener = Listener(address, authkey=b'dtoxd-data-incoming')
while True:
    conn = listener.accept()
    newInstance = ServiceInstance(listener,conn)
    newInstance.start()