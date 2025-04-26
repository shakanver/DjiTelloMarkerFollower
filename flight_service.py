from flight_controller import FlightController
from djitellopy import Tello
import time
from cache import Cache
from threading import Event

def start(stop_event: Event, tello: Tello, cache: Cache):

	# TODO: Make PID values configurable as well.
	roll_velocity_controller = FlightController(0.5,0.5,0.5)
	altitude_velocity_controller = FlightController(0.5,0.5,0.5)

	try:
		tello.takeoff()
		prev_time = time.time()
		while True:
			if stop_event.is_set():
				print("stop signal triggered, flight service is ending.")
				break

			print(f"Flight Controller alive, aruco pos: ({cache.get_aruco_center().x}, {cache.get_aruco_center().y}), frame pos: ({cache.get_frame_center().x}, {cache.get_frame_center().y})")
			curr_time = time.time()
			dt = curr_time - prev_time
			prev_time = curr_time

			aruco_center = cache.get_aruco_center()
			if aruco_center.x == -1 or aruco_center.y == -1:
				continue

			frame_center = cache.get_frame_center()

			x_error = aruco_center.x - frame_center.x
			y_error = aruco_center.y - frame_center.y

			roll_speed = roll_velocity_controller.update(x_error, dt)
			altitude_speed = altitude_velocity_controller.update(y_error, dt)

			# Send RC command to control the roll, pitch, altitude and yaw speeds respectively
			print(f"RC CONTROLS BEING TRANSMITTED: left/right: {roll_speed} forward/backward: {0} up/down: {altitude_speed} yaw: {0}")
			tello.send_rc_control(roll_speed, 0, altitude_speed, 0)

			time.sleep(1)
	finally:
		tello.land()
