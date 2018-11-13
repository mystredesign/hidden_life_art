import RPi.GPIO as GPIO
import time
from collections import namedtuple
import numpy as np
import threading

GPIO_MODES = {'bcm': GPIO.BCM, 'board': GPIO.BOARD}

class LightController(object):
    def __init__(self, pinout, gpio_mode='bcm'):
        if gpio_mode not in GPIO_MODES.keys():
            msg = 'Mode {} not available in list of {}'.format(gpio_modes.keys())
            raise ValueError(msg)
        gpio_mode = GPIO_MODES[gpio_mode]
        GPIO.setmode(gpio_mode)
        self.pinout= pinout
        self.color_matrix = pinout * 0
        self.zero_mat = GPIO.LOW * np.ones(shape=pinout.shape, dtype=int)
        self.one_mat = GPIO.HIGH * np.ones(shape=pinout.shape, dtype=int)
        self.init_pinout()
        self.write_threads=True

    def init_pinout(self):
        for pin in iter(self.pinout.flat):
            GPIO.setup(pin, GPIO.OUT)
    
    def design_and_write(self):
        i=0
        while self.write_threads:
            try:
                #if i%1000==0:
                #    print(i)
                i+=1
                self.color_designer.run()
                self.gpio_writer()
            except KeyboardInterrupt:
                print("Interrupt in gpio writer")
                self.exit()
                return
    
    def gpio_writer(self):
        for pin, intensity in zip(self.pinout.flat, self.color_matrix.flat):
            GPIO.output(pin, intensity)

    def exit(self):
        print("Cleaning threads")
        self.write_threads = False
        print("Cleaning pins")
        time.sleep(0.1)
        self.color_matrix = self.zero_mat
        self.gpio_writer()
        time.sleep(0.1)
        GPIO.cleanup() 


class ColorFromGlobalWriter(LightController):
   
    def __init__(self, pinout, gpio_mode, 
                 color_designer=None, color_designer_args=None):
        super(ColorFromGlobalWriter, self).__init__(pinout, gpio_mode)
        if color_designer is None:
            msg = 'Nothing to do as no designer was none'
            raise ValueError(msg)
        self.color_designer = color_designer(color_mat=self.color_matrix)
        self.threads = []
        self.exception_checker_thread = None

    def initialize_threads(self):
        self.threads = []
        NO_ARGS = ()
        writer_thread = threading.Thread(name='designer and writer', 
               target=self.design_and_write, args=NO_ARGS)
        writer_thread.daemon=True
        self.threads.append(writer_thread)

    def start_threads(self):
        #self.exception_checker_thread.start()
        for t in self.threads:
            print("thread {} started".format(t.name))
            t.start()
        while True:
            try:
                pass
            except KeyboardInterrupt:
                print('interrupt in threads')
                self.write_threads = False
                return

    def color_designer(self):
        raise NotImplementedError
