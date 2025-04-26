"""
Entry Point
"""

import cv2
import flight_service
import os
import threading
import time
import video_service

from djitellopy import Tello
from cache import Cache
from datetime import datetime

# TODO; find a way to gracefully handle keyboard interrupts.

FLIGHT_TIME = 60 #TODO: make this a command line argument and set default flight time to 60
cache = Cache()

"""Create a Tello instance, connect to it and enable video streaming services"""
tello = Tello()
tello.connect()
tello.streamon()

"""Create a video writer so that video stream can be saved to file for debugging and analysis purposes"""
frame_width = 960
frame_height = 720
recordings_dir = './recordings'
if not os.path.exists(recordings_dir):
	os.makedirs(recordings_dir)

video_out = cv2.VideoWriter(f'recordings/output_{datetime.now().strftime("%d%m%Y_%H%M%S")}.mp4', cv2.VideoWriter_fourcc(*'XVID'), 20.0, (frame_width, frame_height))

try:
	stop_event = threading.Event()

	video_thread = threading.Thread(target=video_service.start, args=(stop_event, tello, cache))
	flight_thread = threading.Thread(target=flight_service.start, args=(stop_event, tello, cache))

	video_thread.start()
	flight_thread.start()

	"""cv2 requires that only the main thread streams images and videos."""
	start_time = time.time()
	while time.time() - start_time < FLIGHT_TIME:
		frame = cache.get_frame()
		if frame is not None:
			cv2.imshow("Frame", frame)
			video_out.write(cv2.resize(frame, (frame_width, frame_height)))

		if cv2.waitKey(1) and 0xFF == ord('q'):
			break

	print(f"Flight time of {FLIGHT_TIME} exceeded preparing to stop the flight.")

	stop_event.set()
	video_thread.join(3)
	flight_thread.join(3)

	if video_thread.is_alive() or flight_thread.is_alive():
		raise Exception("One of the service threads failed to stop, force quitting")
	
finally:
	video_out.release()
	tello.streamoff()
	tello.end()





