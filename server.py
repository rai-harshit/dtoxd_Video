from multiprocessing.connection import Listener
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.compat.v1.keras.backend import set_session, get_session
import threading
import numpy
import cv2
import json

global model
global graph
global sess

sess = get_session()
graph = tf.compat.v1.get_default_graph()
with open("model\\5C_model.json","r") as fp:
    model_arch = json.load(fp)
model = model_from_json(json.dumps(model_arch))
model.load_weights("model\\5C_model_weights_tf")

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
                    im_data = numpy.reshape(im_data,(1,224,224,3))
                global model
                global graph
                global sess
                with graph.as_default():
                    set_session(sess)
                    pred = model.predict(im_data)[0]
                print(pred)
                self.conn.send(1 if numpy.argmax(pred) != 4 else 0) 
            except Exception as e:
                print("[ERROR] Issue with the image.")

listener = Listener(address, authkey=b'dtoxd-data-incoming')
exit = 0

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