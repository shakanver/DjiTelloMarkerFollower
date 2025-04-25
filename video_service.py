from djitellopy import Tello
from cache import Cache
import cv2
import cv2.aruco as aruco
from threading import Event

def start(stop_event: Event, tello: Tello, cache: Cache):
	while True:
		if stop_event.is_set():
			print("stop signal triggered, video service is ending.")

		"""
		Frame has the shape width x height x 3.
		Each pixel is an array of length 3 represending RGB colour values
		"""
		frame = tello.get_frame_read().frame
		# TODO: I think the current frame is in BGR, need to figure out how to convert it to RGB.

		"""Draw the center of the frame as a circle"""
		height, width = frame.shape[:2]
		frame_center_x = width//2
		frame_center_y = height//2
		frame_center_colour = (0,255,0)
		cv2.circle(img=frame, center=(frame_center_x, frame_center_y), radius=10, color=frame_center_colour, thickness=-1)

		cache.set_frame_center(frame_center_x, frame_center_y)

		dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
		detector_params = aruco.DetectorParameters()
		
		detector = aruco.ArucoDetector(dictionary, detector_params)

		marker_corners, marker_ids, _ = detector.detectMarkers(frame)

		"""If the aruco marker was found then draw a circle on the frame to represent its center"""
		if marker_corners:
			marker_corners_array = marker_corners[0][0]
			aruco_center_x = int((marker_corners_array[0][0] + marker_corners_array[1][0])/2)
			aruco_center_y = int((marker_corners_array[0][1] + marker_corners_array[2][1])/2)
			cache.set_aruco_center(aruco_center_x, aruco_center_y)
			aruco_color = (0, 0 ,255)

			cv2.circle(img=frame, center=(aruco_center_x, aruco_center_y), radius=10, color=aruco_color, thickness=-1)
		else:
			cache.set_aruco_center(-1, -1)

		if marker_ids is not None:
			aruco.drawDetectedMarkers(frame, marker_corners, marker_ids)

		cache.set_frame(frame)
