import asyncio
import os
import time

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
        ret, frame = cap.read()
        if not ret:
            break

        results = m(frame, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                if box.cls[0] == 0:
                    x1, y1, x2, y2 = box.xyxy[0]
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame,
                                text='people',
                                org=(int(x1), int(y1)),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=0.7,
                                color=(0, 255, 0),
                                thickness=2,
                                lineType=cv2.LINE_4)

        cv2.imshow('Video', frame)
        await asyncio.sleep(10)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

asyncio.run(detect_video(model, os.getenv('VIDEO_PATH')))
# detect_video(model, os.getenv('VIDEO_PATH'))
