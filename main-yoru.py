from ultralytics import YOLO


def load_yolo_model(model_path='yolov5s.pt'):
    model = YOLO(model_path)
    return model

# 使用例
model = load_yolo_model()
print(f"モデルがロードされました: {model}")

def detect_video(model, video_source):
    cap = cv2.VideoCapture(video_source)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 使用例
detect_video(model, "")
