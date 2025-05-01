import asyncio
import os
import time

import cv2
import requests
import schedule
from ultralytics import YOLO
from dotenv import load_dotenv
load_dotenv()


def load_yolo_model(model_path='yolov5s.pt'):
    model = YOLO(model_path)
    return model


model = load_yolo_model()
print(f"モデルがロードされました: {model}")


cap = cv2.VideoCapture(os.getenv('VIDEO_PATH'))


def detect_video(m, z):
    ret, frame = cap.read()
    if not ret:
        print("no ret")
    else:
        try:
            results = m(frame)
            pople_count = 0
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    if box.cls[0] == 0:
                        pople_count += 1
                        x1, y1, x2, y2 = box.xyxy[0]
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            cv2.imwrite("./tmp/room-img.png", frame)
            headers = {
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                "Content-Type": "application/json"
            }
            url = f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/api/webhooks"
            if pople_count > 0:
                requests.post(url, json={"room_in": True}, headers=headers)
            else:
                if z == 5:
                    requests.post(url, json={"room_in": False}, headers=headers)

            print(f"人数: {pople_count}")
        except Exception as e:
            print(f"エラー：{e}")


async def loop_detect_video():
    zero_count = 0
    schedule.every(1).minutes.do(detect_video, m=model, z=zero_count)
    while True:
        schedule.run_pending()
        time.sleep(1)
        zero_count += 1
        if zero_count == 6:
            zero_count = 0

asyncio.run(loop_detect_video())
