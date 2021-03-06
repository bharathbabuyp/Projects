#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 15:59:33 2018

@author: pi
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 15:53:16 2018

@author: JACK
"""
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import time
import datetime
class FPS:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()
    
    
    
class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32,rotation=0,b=50,c=50):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.rotation=rotation
        self.camera.brightness=b
        self.camera.contrast=c
#        self.camera.image_effect='sketch'
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
    def read(self):
        # return the frame most recently read
        return self.frame
 
    def release(self):
        # indicate that the thread should be stopped
        self.stopped = True    
#        self.camera.close()
        
        
if __name__=='__main__':            
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 32
    
    rawCapture = PiRGBArray(camera, size=(320, 240))
    stream = camera.capture_continuous(rawCapture, format="bgr",use_video_port=True)
    # allow the camera to warmup and start the FPS counter
    print("[INFO] sampling frames from `picamera` module...")
    time.sleep(2.0)
    fps = FPS().start()
     
    # loop over some frames
    for (i, f) in enumerate(stream):
        # grab the frame from the stream and resize it to have a maximum
        # width of 400 pixels
        frame = f.array
    #    frame = imutils.resize(frame, width=400)
     
        # check to see if the frame should be displayed to our screen
    
        cv2.imshow("Frame", frame)
        k = cv2.waitKey(1) & 0xFF
     
        # clear the stream in preparation for the next frame and update
        # the FPS counter
        rawCapture.truncate(0)
        fps.update()
     
        # check to see if the desired number of frames have been reached
        if k==27:
            break
     
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
     
    # do a bit of cleanup
    cv2.destroyAllWindows()
    stream.close()
    rawCapture.close()
    camera.close()
    
    
    
    print("[INFO] sampling THREADED frames from `picamera` module...")
    vs = PiVideoStream().start()
    time.sleep(2.0)
    fps = FPS().start()
     
    # loop over some frames...this time using the threaded stream
    while (1):
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
    #    frame = imutils.resize(frame, width=400)
     
        # check to see if the frame should be displayed to our screen
        cv2.imshow("Frame", frame)
        k = cv2.waitKey(1) & 0xFF
        if k==27:
            break
        # update the FPS counter
        fps.update()
     
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
     
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()