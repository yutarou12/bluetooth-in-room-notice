import asyncio
import os

import cv2
from ultralytics import YOLO
from dotenv import load_dotenv
load_dotenv()


def load_yolo_model(model_path='yolov5s.pt'):
    model = YOLO(model_path)
    return model


# 使用例
model = load_yolo_model()
print(f"モデルがロードされました: {model}")


async def detect_video(m, video_source):
    cap = cv2.VideoCapture(video_source)
    while True:
        await asyncio.sleep(5)
        ret, frame = cap.read()
        if not ret:
            break
        results = m(frame)
        pople_count = 0
        for r in results:
            boxes = r.boxes
            for box in boxes:
                if box.cls[0] == 0:
                    pople_count += 1
                    x1, y1, x2, y2 = box.xyxy[0]
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        print(f"人数: {pople_count}")
    cap.release()

asyncio.run(detect_video(model, os.getenv('VIDEO_PATH')))
# detect_video(model, os.getenv('VIDEO_PATH'))
