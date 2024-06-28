import cv2
import math
import time

from matplotlib import image as mpimg


def estimate_speed(location1, location2):
    previous_time = 0
    distance_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    pixels_per_meter = 8.8
    distance_meters = distance_pixels / pixels_per_meter
    while True:
        current_time = time.time()
        fps = 1 / (current_time - previous_time)
        previous_time = current_time
        speed = distance_meters * fps * 3.6
        return speed


def process_in_while(image, car_id, car_bboxes):
    frame_counter = 0
    current_car_id = 0
    fps = 0

    car_tracker = {}
    car_number = {}
    car_location_1 = {}
    car_location_2 = {}

    speeds = [None] * 1000

    while True:
        start_time = time.time()

        if type(image) == type(None):
            break

        frame_counter += 1
        car_ids_to_delete = []

        for car_id in car_tracker.keys():
            tracking_quality = car_tracker[car_id].update(image)

            if tracking_quality < 7:
                car_ids_to_delete.append(car_id)

        for car_id in car_ids_to_delete:
            print("Removing carID " + str(car_id) + ' from list of trackers. ')
            print("Removing carID " + str(car_id) + ' previous location. ')
            print("Removing carID " + str(car_id) + ' current location. ')
            car_tracker.pop(car_id, None)
            car_location_1.pop(car_id, None)
            car_location_2.pop(car_id, None)

        if not (frame_counter % 10):
            for (_x, _y, _w, _h) in car_bboxes:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
            x_center = x + 0.5 * w
            y_center = y + 0.5 * h

            match_car_id = None

            for car_id in car_tracker.keys():
                tracked_position = car_tracker[car_id].get_position()

                # Continue implementing the rest of your logic here with the updated variable names