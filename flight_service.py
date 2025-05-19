import time

from cache import Cache
from threading import Event
from flight_controller import FlightController
from djitellopy import Tello
from logger import logger

def start(stop_event: Event, tello: Tello, cache: Cache, k_p: float, k_i, k_d: float):

	roll_velocity_controller = FlightController(k_p=k_p, k_i=k_i, k_d=k_d)
	altitude_velocity_controller = FlightController(k_p=k_p, k_i=k_i, k_d=k_d)

	try:
		tello.takeoff()
		prev_time = time.time()
		t = 0
		while True:
			if stop_event.is_set():
				logger.info("stop signal triggered, flight service is ending.")
				break

			logger.debug(f"Flight Service alive, aruco pos: (%s, %s), frame pos: (%s, %s)", cache.get_aruco_center().x, cache.get_aruco_center().y, cache.get_frame_center().x, cache.get_frame_center().y)
			curr_time = time.time()
			dt = curr_time - prev_time
			prev_time = curr_time

			aruco_center = cache.get_aruco_center()
			if aruco_center.x == -1 or aruco_center.y == -1:
				continue

			frame_center = cache.get_frame_center()

			x_error = aruco_center.x - frame_center.x
			# reversing the subtraction order for y values because y values increase from top to bottom
			y_error =  frame_center.y - aruco_center.y

			roll_speed = roll_velocity_controller.update(x_error, dt)
			altitude_speed = altitude_velocity_controller.update(y_error, dt)

			"""Send RC command to control the roll, pitch, altitude and yaw speeds respectively"""
			logger.debug(f"RC CONTROLS BEING TRANSMITTED: left/right: %s forward/backward: 0 up/down: %s yaw: 0", roll_speed, altitude_speed)
			tello.send_rc_control(roll_speed, 0, altitude_speed, 0)

			cache.append_plot_data(t, x_error, y_error, roll_speed, altitude_speed)

			time.sleep(1)
			t += 1
	finally:
		logger.info("landing")
		tello.land()
