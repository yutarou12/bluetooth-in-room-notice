import datetime
import json
import os

import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class PostItem(BaseModel):
    room_in: bool


def verify_token(token: str = Depends(oauth2_scheme)):
    if token != os.getenv('API_TOKEN'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# POSTエンドポイントを定義
@app.post("/api/webhooks")
async def notice_room(item: PostItem, token: str = Depends(verify_token)):
    with open("./data/people_count.json", encoding="utf-8") as f:
        data = json.load(f)

    # debug
    if os.path.exists("./tmp/room-img.png"):
        payload = json.dumps({
            "username": "[DEBUG] 在室確認",
            "content": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open("./tmp/room-img.png", "rb") as f:
            multiple_files = {"attachment", ("room-img.jpg", f)}
            debug_res = requests.post(os.getenv("DISCORD_WEBHOOK_URL"), json={"payload_json": payload}, files=multiple_files)
            print(debug_res.status_code)

    if item.room_in:
        if not data.get("RoomIn"):
            if not data.get("InRoomAlreadyNotice"):

                # Discordへ
                post_content = {
                    "username": "在室通知",
                    "content": "## 在室"
                }
                requests.post(os.getenv('DISCORD_WEBHOOK_URL'), json=post_content)

                data["RoomIn"] = True
                data["InRoomAlreadyNotice"] = True
                data["NoRoomAlreadyNotice"] = False
                with open("./data/people_count.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                return {"message": "Already notified"}
    else:
        if data.get("RoomIn"):
            if not data.get("NoRoomAlreadyNotice"):

                # Discordへ
                post_content = {
                    "username": "在室通知",
                    "content": "## 空室"
                }
                requests.post(os.getenv('DISCORD_WEBHOOK_URL'), json=post_content)

                data["RoomIn"] = False
                data["InRoomAlreadyNotice"] = False
                data["NoRoomAlreadyNotice"] = True
                with open("./data/people_count.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                return {"message": "Already notified"}

if __name__ == "__main__":
    uvicorn.run("main_api:app", host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", "9000")), log_level="debug", reload=True)
