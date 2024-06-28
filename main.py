from FunctionLibrary import EuclideanDistTracker, SpeedEstimator
import cv2
import time
import json
import os

# File path to store max speeds
MAX_SPEEDS_FILE = "max_speeds.json"


def main():
    tracker = EuclideanDistTracker()
    PTime = 0
    obj_det = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
    cap = cv2.VideoCapture("highway.mp4")

    max_speeds = {}

    while True:
        _, img = cap.read()
        if img is None:
            break

        h, w, _ = img.shape
        roi = img[340:720, 500:w]
        mask = obj_det.apply(roi)
        mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)[1]

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append([x, y, w, h])

        CTime = time.time()
        fps = 1 / (CTime - PTime)
        PTime = CTime

        boxes_ids = tracker.update(detections)
        for box in boxes_ids:
            x, y, w, h, id = box
            speed_estimator = SpeedEstimator([x, y], fps)
            speed = speed_estimator.estimateSpeed()
            cv2.putText(roi, f"{id}: {speed} Km/h", (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

            # Determine if speed is allowed or not allowed
            if speed < 60:
                allowed_status = "allowed"
            else:
                allowed_status = "notallowed"

            # Update max_speeds dictionary with id, max_speed, and allowed status
            if id in max_speeds:
                if speed > max_speeds[id]["max_speed"]:
                    max_speeds[id] = {"max_speed": speed, "allowed": allowed_status}
            else:
                max_speeds[id] = {"max_speed": speed, "allowed": allowed_status}

            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0) if allowed_status == "allowed" else (0, 0, 255), 3)

        # Write max speeds to file after each frame
        with open(MAX_SPEEDS_FILE, 'w') as file:
            json.dump(max_speeds, file, indent=4)  # Use indent for pretty formatting

        cv2.imshow("img", img)
        key = cv2.waitKey(30)
        if key == 113:  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
