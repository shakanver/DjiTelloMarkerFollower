import time

# TODO: move this to a config file? 

MAX_SPEED = 100
MIN_SPEED = -100

class FlightController:

	def __init__(self, k_p: int, k_i: int, k_d):
		self.k_p = k_p
		self.k_i = k_i
		self.k_d = k_d
		self.previous_error = 0
		self.error_i = 0
		self.error_d = 0
		self.error_p = 0

	def update(self, error, dt):
		self.error_i += error*dt*self.k_i
		self.error_d = ((error - self.previous_error) / dt) * self.k_d
		self.error_p = error * self.k_p

		speed = self.error_p + self.error_i + self.error_d
		speed = max(min(speed, MAX_SPEED), MIN_SPEED)
		return int(speed)
