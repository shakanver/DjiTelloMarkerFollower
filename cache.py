import threading
from point import Point

class Cache:
	def __init__(self):
		self.frame_center = Point(0,0)
		self.aruco_center = Point(-1,-1)
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