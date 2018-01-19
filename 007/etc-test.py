import pygame
import pygame.gfxdraw

# used to import a file name from the command line
import importlib
import argparse

import os

parser = argparse.ArgumentParser(description="Critter and Guitari ETC program debug environment")
parser.add_argument('module', type=str, help="Filename of the Pygame program to test")
parser.add_argument('midi', type=int, help="input midi device to use")
parser.add_argument('-r', '--record', type=int, help="Record out to image sequence for ffmpeg")
args = parser.parse_args()

# imports the actual module we're loading
i = importlib.import_module(args.module.split('.py')[0])

import random
import math

import time

from pygame.color import THECOLORS

class MidiInputHandler(object):
    def __init__(self, port, freq):
        self.port = port
        self.base_freq = freq
        self._wallclock = time.time()
        self.knob_vals = [random.random() for i in range(7)]

    def __call__(self, event, data=None):
        global currentFrequency
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        if message[1] == 16:
            self.freq_vals[0] = (message[2] - 62) * .5
        elif message[1] == 17:
            self.freq_vals[1] = (message[2] - 62) * .01
        elif message[1] == 18:
            self.freq_vals[2] = (message[2] - 62) * .005
        elif message[1] == 19:
            self.freq_vals[3] = (message[2] - 62) * .0001 
        elif message[1] == 20:
            self.freq_vals[4] = (message[2] - 62) * .00001
        new_freq = self.base_freq
        for i in range(6):
            new_freq += self.freq_vals[i]
        currentFrequency = new_freq
        print(new_freq)

if args.midi:
    try:
        midiin, port_name = open_midiinput(port)
    except (EOFError, KeyboardInterrupt):
        exit()
    midiSettings = MidiInputHandler(port_name, 940.0)
    midiin.set_callback(midiSettings)


# initialize to ETC's resolution
screenWidth, screenHeight = 1280, 720
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))

# give ourselves some initial values
class ETC(object):
    def __init__(self):
        self.knob1 = random.random()
        self.knob2 = random.random()
        self.knob3 = random.random()
        self.knob4 = random.random()

        self.audio_in = [random.randint(-32768, 32767) for i in range(100)]
        self.bg_color = (0, 0, 0)
        self.audio_trig = False
        self.random_color = THECOLORS[random.choice(THECOLORS.keys())]
        self.midi_note_new = False

    def color_picker(self):
        self.random_color = THECOLORS[random.choice(THECOLORS.keys())]
        return self.random_color

etc = ETC()

i.setup(screen, etc)

running = True

recording = False
counter = -1

if args.record:
    recording = True

if recording:
    if not os.path.exists('imageseq'):
        os.makedirs('imageseq')
    counter = 0

while running:
    screen.fill(THECOLORS['black'])
    i.draw(screen, etc)

    key = pygame.key.get_pressed()
    if key[pygame.K_q]:
        exit()
    
    if key[pygame.K_SPACE]:
        etc.audio_trig = True
    if key[pygame.K_z]:
        etc.audio_trig = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # if you try to quit, let's leave this loop
            running = False
    pygame.display.flip()

    if recording and counter < args.record:
        pygame.image.save(screen, "imageseq/%05d.jpg" % counter)
        counter += 1
    elif recording and counter == args.record:
        exit()
