import unittest
import sys
import subprocess
import shutil

class OldCocoTest(unittest.TestCase):

    def compile_extras(self):
        subprocess.check_call("coconut ./src/extras.coco ./bin",shell=True)

    def compile_runner(self):
        subprocess.check_call("coconut ./src/src/runner.coco ./bin",shell=True)

    def compile_agnostic(self):
        subprocess.check_call("coconut ./src/src/agnostic ./bin/cocotest",shell=True)

    def compile_2(self):
        subprocess.check_call("coconut --target 2 ./src/src/python2 ./bin/cocotest",shell=True)

    def compile_3(self):
        subprocess.check_call("coconut --target 3 ./src/src/python3 ./bin/cocotest",shell=True)

    def compile_35(self):
        subprocess.check_call("coconut --target 35 ./src/src/python35 ./bin/cocotest",shell=True)


    def compile_source(self):
        self.compile_extras()
        self.compile_runner()
        self.compile_agnostic()
        
        if sys.version_info >= (3,):
            self.compile_3()
        if sys.version_info >= (3,5):
            self.compile_35()
        if (sys.version_info >= (2,)) & (sys.version_info < (3,)):
            self.compile_2()

    def test_compile_and_run_src(self):
        self.compile_source()
        subprocess.check_call("python ./bin/runner.py")
        shutil.rmtree("./bin")

if __name__ == '__main__':
    unittest.main()