import pygame
import serial
import sys
import time
import traceback

from constants import *
from engine_hat import analyzeSpeech, UserSession
from speech_to_text import initRecogs, getSpeech2Text, getRecognizer

SONG_END = pygame.USEREVENT + 1

def pauseAWhile():
    time.sleep(SLEEP_TIME)

def playSpeech(dialog_box):
    #start speaking
    dialog_box.play()
    if ISARDUINO:
        SERL.write(START_HAT)

def pauseSpeech():
    notdone = True
    while notdone:
        for event in pygame.event.get():
            if event.type == SONG_END:
                print("The hat has spoken!")  #TODO: add what the hat spoke
                if ISARDUINO:
                    SERL.write(END_HAT)
                notdone = False
    return None

def readSerial():
    # if SERL.inWaiting()>0:
    #   print "entered loop"
    #   mydata = SERL.readline()
    #   print mydata, len(mydata)
    return None

def loadDialog(dialog_box,dialog):
    #load first dialog
    dialog_box.load(dialog)
    pauseAWhile()
    dialog_box.set_endevent(SONG_END)
    
def loadAndPlayDialogs(dialog_box,dialogs):
    
    #stop speech
    dialog_box.stop()
    # print "stopped hat speech"
    
    n = len(dialogs)

    loadDialog(dialogs[0])
    # pygame.mixer.music.set_volume(0.5)
    playSpeech(dialog_box)

    if n > 1:
        for i in range(1,n):
            dialog_box.queue(dialogs[i])

    #wait for speech to stop
    pauseSpeech()
    
    return None

def startConv(dialog_box,recog):

    #load and play welcome speech
    loadDialog(dialog_box,SP_PATHS[WELCOME2])  #TODO - add multiple random welcome speeches
    print("Loaded Welcome2")
    pauseAWhile()
    playSpeech(dialog_box)
    pauseSpeech()

    session = UserSession()
    
    while not session.decisionMade:
        
        #py2.7 console input
        # reply = input("Press enter to speak")

        #get speech from user and convert to text
        print "What do you say?..."
        text = getSpeech2Text(recog)

        if not text:
            #TODO - add error handling hat reply
            continue

        #get list of audio files to play - single file!
        resp = analyzeSpeech(text,count)

        loadAndPlayDialogs(dialog_box,resp)

def main(argv):

    #check for arduino port number argument else exit
    if len(argv) < 1:
        print "Provide 2 arguments: True if arduino is connected (else False) and its corresponding port number!"
        exit()

    #set arduino port number and and initialize serial
    ISARDUINO = (argv[0] == "True")
    if ISARDUINO:
        port = "/dev/ttyACM"+argv[1]
        SERL = serial.Serial(port)

    #init GCP recognizer
    try:
        initRecogs()
    except Exception:
        print "Error reading GCP file containing credentials"
        traceback.print_exc()

    #initialize pygame for playing speech
    pygame.init()
    pauseAWhile()
    print("Initialized pygame")
    dialog_box = pygame.mixer.music

    #initialize recognizer
    recog = getRecognizer()
    print("Got recognizer")
    
    try:
        while True:
            reply = raw_input("Press enter to talk to the hat!")

            #startconversation
            startConv(dialog_box,recog)

    except KeyboardInterrupt:
        print "Closing port and exiting"
        if ISARDUINO:
            SERL.close()
        dialog_box.stop()
        exit()

if __name__ == "__main__":
   main(sys.argv[1:])