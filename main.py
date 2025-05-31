import argparse
import multiprocessing
import cv2
import flight_service
import os
import multiprocessing
import time
import video_processor

from djitellopy import Tello
from cache import Cache
from datetime import datetime
from logger import logger
from process_manager import ProcessManager

if __name__ == '__main__':

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

	"""Create a video writer so that video stream can be saved to file for debugging and analysis purposes"""
	frame_width = 960
	frame_height = 720
	recordings_dir = './recordings'
	if not os.path.exists(recordings_dir):
		os.makedirs(recordings_dir)

	video_file_path = os.path.join(recordings_dir, f'output_{datetime.now().strftime("%d%m%Y_%H%M%S")}.mp4')
	video_out = cv2.VideoWriter(video_file_path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 20.0, (frame_width, frame_height))

	ProcessManager.register('Cache', Cache)

	with ProcessManager(address=('', 50000)) as manager:
		"""Create a Tello instance, connect to it and enable video streaming services"""
		tello = Tello()
		tello.connect()
		tello.streamon()

		cache = manager.Cache()
		stop_event = multiprocessing.Event()
		flight_process = multiprocessing.Process(target=flight_service.start, args=(stop_event, tello, cache, K_P, K_I, K_D))

		try:
			if not args.disable_flight:
				flight_process.start()

			start_time = time.time()
			frame_read = tello.get_frame_read()
			while time.time() - start_time < FLIGHT_TIME:
				frame = frame_read.frame
				if frame is not None:
					processed_frame = video_processor.process(frame, cache)
					cv2.imshow("Frame", processed_frame)
					video_out.write(cv2.resize(processed_frame, (frame_width, frame_height)))

				if cv2.waitKey(1) and 0xFF == ord('q'):
					break

			logger.info(f"Flight time of %s exceeded preparing to stop the flight.", FLIGHT_TIME)

			stop_event.set()
			flight_process.join(3)

		except KeyboardInterrupt:
			logger.info("Early termination from the user.")
			stop_event.set()
			flight_process.join(3)

		finally:
			logger.info("Freeing all resources")

			video_out.release()
			tello.streamoff()
			tello.end()

			data_dir = './data'
			if not os.path.exists(data_dir):
				os.makedirs(data_dir)

			cache.plot_data(data_dir)
