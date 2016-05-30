import os
import sys
import argparse
from queuelib import FifoDiskQueue

class Runner:
    def __init__(self, cancel, queue ='queue'):
        self.cancel = cancel
        self.queue = queue

    def should_cancel(self):
        with os.popen(self.cancel,'r') as cancel:
            result = cancel.read(2)
        return result != ''

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
    parser.add_argument('--cancel', type = str, default = 'echo ""', help = 'Command to determine when to cancel')
    parser.add_argument('--tasks', type = str, help = 'Read list of tasks from this file rather than from stdin')
    parser.add_argument('--no-run', action = 'store_true', help = 'Quit after adding tasks to queue')
    args = parser.parse_args()
    runner = Runner(cancel = args.cancel, queue = args.queue)
    try:
        with open(args.task,'r') as task_file:
            for line in task_file:
                runner.add_job(line)
    except AttributeError:
        for line in sys.stdin:
            runner.add_job(line)
    if not args.no_run:
        runner.run()

    


