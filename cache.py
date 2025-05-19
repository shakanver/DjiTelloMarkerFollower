import numpy as np
import threading
from point import Point
import matplotlib.pyplot as plt
import os
from logger import logger

from datetime import datetime

class Cache:
	def __init__(self):
		self.frame_center = Point(0,0)
		self.aruco_center = Point(-1,-1)
		self.x_error_data = np.array([])
		self.y_error_data = np.array([])
		self.x_speed_data = np.array([])
		self.y_speed_data = np.array([])
		self.time_data = np.array([])
		self.frame = None
		self.lock = threading.Lock()

	def get_frame(self):
		with self.lock:
			return self.frame

	def set_frame(self, frame: any):
		with self.lock:
			self.frame = frame

	def get_frame_center(self):
		with self.lock:
			return self.frame_center

	def set_frame_center(self, x: int, y: int):
		with self.lock:
			self.frame_center.x = x
			self.frame_center.y = y

	def get_aruco_center(self):
		with self.lock:
			return self.aruco_center

	def set_aruco_center(self, x: int, y: int):
		with self.lock:
			self.aruco_center.x = x
			self.aruco_center.y = y

	def append_plot_data(self, time: int, x_error: int, y_error: int, x_speed: int, y_speed: int):
		with self.lock:
			self.x_error_data = np.append(self.x_error_data, x_error)
			self.y_error_data = np.append(self.y_error_data, y_error)
			self.x_speed_data = np.append(self.x_speed_data, x_speed)
			self.y_speed_data = np.append(self.y_speed_data, y_speed)
			self.time_data = np.append(self.time_data, time)

	def plot_data(self, data_dir: str):
		logger.debug("Saving plots")

		figure, axis = plt.subplots(nrows=2, ncols=1)
		error_plot = axis[0]
		speed_plot = axis[1]

		# Plot error data
		error_plot.plot(self.time_data, self.x_error_data, marker='o', label='X Error')
		error_plot.plot(self.time_data, self.y_error_data, marker='o', label='Y Error')
		error_plot.set_xlabel('Time (s)')
		error_plot.set_ylabel('Error')
		error_plot.set_title('Tracking Errors Over Time')
		error_plot.legend()
		error_plot.grid(True)

		# Plot speed data
		speed_plot.plot(self.time_data, self.x_speed_data, marker='o', label='Xl Speed')
		speed_plot.plot(self.time_data, self.y_speed_data, marker='o', label='Y Speed')
		speed_plot.set_xlabel('Time (s)')
		speed_plot.set_ylabel('Speed')
		speed_plot.set_title('Speed Values Over Time')
		speed_plot.legend()
		speed_plot.grid(True)

		figure.tight_layout()
		plt.savefig(os.path.join(data_dir, f'plot_{datetime.now().strftime("%d%m%Y_%H%M%S")}.png'))
		plt.close()

