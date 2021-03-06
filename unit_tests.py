import unittest
from unittest import skip
import tempfile
import runner
import os

class RunnerTest(unittest.TestCase):

    def setUp(self):
        self.queue = tempfile.mkdtemp()
        self.cancel_file = tempfile.NamedTemporaryFile(mode = 'w+')
        self.runner = runner.Runner(cancel = 'cat %s' % self.cancel_file.name, queue = self.queue)
    
    def tearDown(self):
        self.cancel_file.close()
        os.system('rm -r %s' % self.queue)

    def write_cancel(self, s):
        self.cancel_file.seek(0)
        self.cancel_file.truncate()
        self.cancel_file.file.write(s)
        self.cancel_file.seek(0)

    def cancel_at(self, r):
        count = 0
        def replacement_cancel():
            nonlocal count, r
            count += 1
            if count - 1 in r:
                return True
            return False
        return replacement_cancel

    def test_runs_job(self):
        with tempfile.NamedTemporaryFile(mode = 'r') as outfile:
            self.runner.should_cancel = self.cancel_at([])
            self.runner.add_job('echo "%d" >> %s' % (0, outfile.name))

            self.runner.run()

            result = outfile.read()
        self.assertEqual(result, '0\n')

    def test_recognizes_cancel(self):
        self.write_cancel('reboot')
        
        self.assertTrue(self.runner.should_cancel())

    def test_recognizes_no_cancel(self):
        self.write_cancel('')
        
        self.assertTrue(not self.runner.should_cancel())

    def test_does_cancel(self):
        with tempfile.NamedTemporaryFile(mode = 'r') as outfile:
            for i in range(4):
                self.runner.add_job('echo "%d" >> %s' % (i, outfile.name))
            self.runner.should_cancel = self.cancel_at([2,4])
            
            self.runner.run()
            
            outfile.seek(0)
            result = outfile.read()
        self.assertEqual(result, '0\n1\n')

    def test_does_not_repeat_jobs(self):
        with tempfile.NamedTemporaryFile(mode = 'r') as outfile:
            for i in range(4):
                self.runner.add_job('echo "%d" >> %s\n' % (i, outfile.name))
            self.runner.should_cancel = self.cancel_at([1,3])

            self.runner.run()
            self.runner.run()

            outfile.seek(0)
            result = outfile.read()
        self.assertEqual(result, '0\n1\n')

    def test_does_remember_jobs(self):
        with tempfile.NamedTemporaryFile(mode = 'r') as outfile:
            self.runner.add_job('echo "%d" >> %s\n' % (0, outfile.name))
            self.runner = runner.Runner(cancel = 'cat %s' % self.cancel_file.name, queue = self.queue)
            self.runner.should_cancel = self.cancel_at([])

            self.runner.run()

            result = outfile.read()
        self.assertEqual(result, '0\n')
            
if __name__ == '__main__':
    unittest.main(warnings = 'ignore')
