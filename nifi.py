from time import sleep
import tellopy
import datetime
import os
import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time

file = None
write_header = True

def handler(event, sender, data, **args):
    global file
    global write_header
    drone = sender
    if event is drone.EVENT_LOG_DATA:
        if file == None:
            path = '/Volumes/TSPANN/projects/nifi-drone/logs/tello-%s.csv' % (
                datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
            file = open(path, 'w')
        if write_header:
            file.write('%s\n' % data.format_cvs_header())
            write_header = False
        file.write('%s\n' % data.format_cvs())
    if event is drone.EVENT_FLIGHT_DATA or event is drone.EVENT_LOG_DATA:
        print('record_log: %s: %s' % (event.name, str(data)))

def test():
    drone = tellopy.Tello()
    try:
        drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
        drone.subscribe(drone.EVENT_LOG_DATA, handler)
        drone.record_log_data()

        drone.connect()
        drone.wait_for_connection(60.0)

        container = av.open(drone.get_video_stream())
        frame_skip = 1 
        
        drone.takeoff()
        sleep(5)
        drone.up(50) 
        counter = 0
 
        while counter < 600:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                uuid2 = '{0}'.format(strftime("%Y%m%d%H%M%S",gmtime()))
                filename = '/Volumes/TSPANN/projects/nifi-drone/images/fly_image_{0}.jpg'.format(uuid2)
                cv2.imwrite(filename, image)
                #cv2.imshow('Original', image)
                #cv2.waitKey(1)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)
            sleep(1)
            counter = counter + 1    
        sleep(1)
        drone.land()
    except Exception as ex:
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    test()        
