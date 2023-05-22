import argparse
import msvcrt
import time
import os
import sys
from multiprocessing import Process, Queue, Event
from process2 import MyWorker

class MyProducer(Process):
    def __init__(self, queue, event, event_done, fno):
        Process.__init__(self)
        self.queue = queue
        self.event = event
        self.event_done = event_done
        self.fno = fno

    def run(self):
        parser = argparse.ArgumentParser(description='This tool test CS50 Web project Commerce.')
        parser.add_argument("--register", "-r", action="extend", nargs="+", type=str, metavar='username' ,help='Register User(s)')
        parser.add_argument("--login", "-li", nargs=1, type=str, metavar='username', help='Login')
        parser.add_argument("--start", "-s", action='store_const', const=True, default=None, help='Open Chrome Driver')
        parser.add_argument("--logout", "-lo", action='store_const', const=True, default=None, help='Logout')
        parser.add_argument("--end", action='store_const', const=True, default=None, help='Close Chrome Driver')
        parser.add_argument("--exit", action='store_const', const=True, default=None, help='Exit Tool')
        parser.add_argument("--test", "-t", action='store_const', const=True, default=None, help='Run Test')

        while True:    # Loop continuously
            sys.stdin = os.fdopen(self.fno)
            inp = input("\nEnter Command:")
            print(f"[{inp}]")

            if inp == "--exit":
                self.queue.put(inp)
                self.event.set()
                break
            elif inp == "-h" or inp == "--help":
                try:
                    parser.parse_args(f'{inp}'.split())
                except SystemExit as err:
                    #print(f"{err=}, {type(err)=}")
                    pass
            else:
                try:          
                    args = parser.parse_args(f'{inp}'.split())
                    #print(f"{args}")
                    self.queue.put(args)      # Pass command to worker
                    self.event.set()          # Notify worker
                    self.event_done.wait()    # Wait worker finish 
                    self.event_done.clear()
                except SystemExit as err:
                    #print(f"...{err=}, {type(err)=}")
                    pass

if __name__ == '__main__':
    state_queue = Queue()
    state_ready = Event()
    state_done = Event()
    producerprocess = MyProducer(state_queue, state_ready, state_done, sys.stdin.fileno())
    consumerprocess = MyWorker(state_queue, state_ready, state_done)
    producerprocess.start()
    consumerprocess.start()