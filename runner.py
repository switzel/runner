import os
from queuelib import FifoDiskQueue

class Runner:
    def __init__(self, motd, queue_file ='queue'):
        self.motd = motd
        self.queue_file = queue_file

    def should_cancel(self):
        with open(self.motd,'r') as motdfile:
            message = motdfile.read()
            return 'reboot' in message

    def add_job(self, s):
        queue = FifoDiskQueue(self.queue_file)
        queue.push(s.encode('latin1'))
        queue.close()

    def run(self):
        queue = FifoDiskQueue(self.queue_file)
        while True:
            if self.should_cancel():
                break
            qe = queue.pop()
            if qe == None:
                break
            task = qe.decode('latin1')
            os.system(task)
        queue.close()
