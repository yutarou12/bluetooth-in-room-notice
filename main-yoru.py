import asyncio
import datetime
import json
import time

import cv2
import requests
import schedule
from ultralytics import YOLO

import libs.env as env


def load_yolo_model(model_path='yolov8s.pt'):
    model = YOLO(model_path)
    return model


model = load_yolo_model()
print(f"モデルがロードされました: {model}")


def detect_video(m):
    date_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("./data/room_count.json", encoding="utf-8") as f:
        data = json.load(f)

    room_count = data.get("RoomCount")
    cap = cv2.VideoCapture(env.VIDEO_PATH)
    ret, frame = cap.read()
    if not ret:
        print(f"[{date_now}] no ret")
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
                "Authorization": f"Bearer {env.API_TOKEN}",
                "Content-Type": "application/json"
            }
            url = f"http://{env.API_HOST}:{env.API_PORT}/api/webhooks"
            if pople_count > 0:
                requests.post(url, json={"room_in": True}, headers=headers)
                room_count = 0
            else:
                if room_count == 5:
                    requests.post(url, json={"room_in": False}, headers=headers)
                    room_count = 0
                else:
                    room_count += 1

            with open("./data/room_count.json", "w", encoding="utf-8") as f:
                data["RoomCount"] = room_count
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"[{date_now}] 人数: {pople_count}")
        except Exception as e:
            print(f"[{date_now}] エラー：{e}")


async def loop_detect_video():
    schedule.every(1).minutes.do(detect_video, m=model)
    while True:
        schedule.run_pending()
        time.sleep(1)

asyncio.run(loop_detect_video())
