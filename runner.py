import os
import sys
import argparse
from queuelib import FifoDiskQueue

class Runner:
    def __init__(self, motd, queue ='queue'):
        self.motd = motd
        self.queue = queue

    def should_cancel(self):
        with open(self.motd,'r') as motdfile:
            message = motdfile.read()
            return 'reboot' in message

    def add_job(self, s):
        queue = FifoDiskQueue(self.queue)
        queue.push(s.encode('latin1'))
        queue.close()

    def run(self):
        queue = FifoDiskQueue(self.queue)
        while True:
            if self.should_cancel():
                break
            qe = queue.pop()
            if qe == None:
                break
            task = qe.decode('latin1')
            os.system(task)
        queue.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Simple process queue')
    parser.add_argument('--queue', type = str, default = 'run_queue', help = 'Folder name for the queue')
    parser.add_argument('--motd', type = str, default = '/var/run/motd.dynamic', help = 'Location of the message of the day')
    parser.add_argument('--tasks', type = str, help = 'Read list of tasks from this file rather than from stdin')
    parser.add_argument('--no-run', action = 'store_true', help = 'Quit after adding tasks to queue')
    args = parser.parse_args()
    runner = Runner(motd = args.motd, queue = args.queue)
    try:
        with open(args.task,'r') as task_file:
            for line in task_file:
                runner.add_job(line)
    except AttributeError:
        for line in sys.stdin:
            runner.add_job(line)
    if not args.no_run:
        runner.run()

    


