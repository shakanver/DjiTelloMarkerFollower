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

# TODO: REMOVE
	# def hover(self, desired_height:int, hover_time: int):
	# 	error_i = 0
	# 	prev_error = 0
	# 	prev_time = time.time()
	# 	for _ in range(hover_time):
	# 		curr_time = time.time()
	# 		dt = curr_time - prev_time
	# 		prev_time = curr_time

	# 		curr_height = self.tello_connection.get_height()
	# 		curr_error = desired_height - curr_height
			
	# 		error_i += curr_error*dt
	# 		error_d = (curr_error - prev_error)/ dt

	# 		prev_error = curr_error
			
	# 		speed = self.k_p*curr_error + self.k_i*error_i + self.k_d*error_d
	# 		speed = max(min(speed, MAX_SPEED), MIN_SPEED)
	# 		self.tello_connection.send_rc_control(0, 0, int(speed), 0)
	# 		print(f"height: {curr_height} error: {curr_error}")

	# 		time.sleep(1)


