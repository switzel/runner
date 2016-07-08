import os
import sys
import argparse
import signal
from queuelib import FifoDiskQueue

class Runner:
    def __init__(self, cancel_command, queue ='queue'):
        self.cancel_command = cancel_command
        self.queue = queue
        self.cancel = False

    def query_cancel(self):
        if self.cancel:
            return True
        with os.popen(self.cancel_command,'r') as cancel_command:
            result = cancel_command.read(2)
        return result != ''

    def do_cancel(self):
        self.cancel = True

    def add_job(self, s):
        queue = FifoDiskQueue(self.queue)
        queue.push(s.encode('latin1'))
        queue.close()

    def run(self):
        queue = FifoDiskQueue(self.queue)
        while True:
            if self.query_cancel():
                break
            qe = queue.pop()
            if qe == None:
                break
            task = qe.decode('latin1')
            os.system(task)
        queue.close()

defaults = { 'queue' : 'run_queue',
             'cancel' : 'echo -n ""' }

if __name__ == '__main__':
    try:
        import config
        try:
            defaults['cancel'] = config.cancel
        except AttributeError:
            pass
        try:
            defaults['queue'] = config.queue
        except AttributeError:
            pass
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description = 'Simple process queue')
    parser.add_argument('--queue', type = str, default = defaults['queue'], help = 'Folder name for the queue')
    parser.add_argument('--cancel', type = str, default = defaults['cancel'], help = 'Command to determine when to cancel')
    parser.add_argument('--tasks', type = str, help = 'Read list of tasks from this file rather than from stdin')
    parser.add_argument('--no-run', action = 'store_true', help = 'Quit after adding tasks to queue')
    args = parser.parse_args()
    runner = Runner(cancel_command = args.cancel, queue = args.queue)
    if args.tasks:
        with open(args.tasks,'r') as task_file:
            for line in task_file:
                runner.add_job(line)
    else:
        for line in sys.stdin:
            runner.add_job(line)
    if not args.no_run:
        def handler(signum, frame):
            if signum == signal.SIGTERM:
                runner.do_cancel()
        signal.signal(signal.SIGTERM, handler)
        runner.run()
