"""
Entry Point
"""

import threading
import video_service
import flight_service
import cv2
import time

from djitellopy import Tello
from cache import Cache

# TODO; find a way to gracefully handle keyboard interrupts.

FLIGHT_TIME = 60 #TODO: make this a command line argument and set default flight time to 60
cache = Cache()

tello = Tello()
tello.connect()
tello.streamon()

try:
	stop_event = threading.Event()

	video_thread = threading.Thread(target=video_service.start, args=(stop_event, tello, cache))
	flight_thread = threading.Thread(target=flight_service.start, args=(stop_event, tello, cache))

	video_thread.start()
	flight_thread.start()

	start_time = time.time()
	while time.time() - start_time < FLIGHT_TIME:
		frame = cache.get_frame()
		if frame is not None:
			cv2.imshow("Frame", frame)

		if cv2.waitKey(1) and 0xFF == ord('q'):
			break

	print(f"Flight time of {FLIGHT_TIME} exceeded preparing to stop the flight.")

	stop_event.set()
	video_thread.join(3)
	flight_thread.join(3)

	if video_thread.is_alive() or flight_thread.is_alive():
		raise Exception("One of the service threads failed to stop, force quitting")
	
finally:
	tello.streamoff()
	tello.end()





