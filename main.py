"""
Entry Point
"""
import argparse
import cv2
import flight_service
import matplotlib.pyplot as plt
import logging
import os
import threading
import time
import video_service

from djitellopy import Tello
from cache import Cache
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument('--flight_time', type=int, default=10, help='Duration of the flight time in seconds')
parser.add_argument('--disable_flight', type=bool, default=False, help='toggle to disable flight')
parser.add_argument('--kp', type=float, required=True, help='PID proportional gain')
parser.add_argument('--ki', type=float, required=True, help='PID integral gain')
parser.add_argument('--kd', type=float, required=True, help='PID differential gain')
args = parser.parse_args()

FLIGHT_TIME = args.flight_time
K_P = args.kp
K_I = args.ki
K_D = args.kd

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

video_file_path = os.path.join(recordings_dir, f'output_{datetime.now().strftime("%d%m%Y_%H%M%S")}.mp4')
video_out = cv2.VideoWriter(video_file_path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 20.0, (frame_width, frame_height))

try:
	stop_event = threading.Event()

	video_thread = threading.Thread(target=video_service.start, args=(stop_event, tello, cache))
	flight_thread = threading.Thread(target=flight_service.start, args=(stop_event, tello, cache, K_P, K_I, K_D))

	video_thread.start()
	if not args.disable_flight:
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

except KeyboardInterrupt:
	print("Early termination from the user.")
	stop_event.set()
	video_thread.join(3)
	flight_thread.join(3)

	data_dir = './data'
	if not os.path.exists(data_dir):
		os.makedirs(data_dir)

	# Plot error data
	plt.figure()
	plt.plot(cache.time_data, cache.x_error_data, label='X Error')
	plt.plot(cache.time_data, cache.y_error_data, label='Y Error')
	plt.xlabel('Time (s)')
	plt.ylabel('Error')
	plt.title('Tracking Errors Over Time')
	plt.legend()
	plt.grid(True)
	plt.savefig(os.path.join(data_dir, f'xy_error_{datetime.now().strftime("%d%m%Y_%H%M%S")}.png'))
	plt.close()

	plt.figure()
	plt.plot(cache.time_data, cache.x_speed_data, label='X/Roll Speed')
	plt.plot(cache.time_data, cache.y_speed_data, label='Y/Roll Speed')
	plt.xlabel('Time (s)')
	plt.ylabel('Speed')
	plt.title('Speed Values Over Time')
	plt.legend()
	plt.grid(True)
	plt.savefig(os.path.join(data_dir, f'xy_speed_{datetime.now().strftime("%d%m%Y_%H%M%S")}.png'))
	plt.close()

finally:
	print("Freeing all resources")
	video_out.release()
	tello.streamoff()
	tello.end()


	data_dir = './data'
	if not os.path.exists(data_dir):
		os.makedirs(data_dir)

	plt.figure()
	plt.plot(cache.time_data, cache.x_error_data, label='X Error')
	plt.plot(cache.time_data, cache.y_error_data, label='Y Error')
	plt.xlabel('Time (s)')
	plt.ylabel('Error')
	plt.title(f'Tracking Errors Over Time kp: {K_P} ki: {K_I} kd: {K_D}')
	plt.legend()
	plt.grid(True)
	plt.savefig(os.path.join(data_dir, f'xy_error_{datetime.now().strftime("%d%m%Y_%H%M%S")}.png'))
	plt.close()

	plt.figure()
	plt.plot(cache.time_data, cache.x_speed_data, label='X/Roll Speed')
	plt.plot(cache.time_data, cache.y_speed_data, label='Y/Roll Speed')
	plt.xlabel('Time (s)')
	plt.ylabel('Speed')
	plt.title('Speed Values Over Time')
	plt.legend()
	plt.grid(True)
	plt.savefig(os.path.join(data_dir, f'xy_speed_{datetime.now().strftime("%d%m%Y_%H%M%S")}.png'))
	plt.close()

