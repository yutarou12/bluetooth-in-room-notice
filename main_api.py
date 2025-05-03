import datetime
import json
import os

import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from libs.lineworks import LineWorksAPI
import libs.env as env

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class PostItem(BaseModel):
    room_in: bool


def verify_token(token: str = Depends(oauth2_scheme)):
    if token != env.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def post_lineworks_board(room_bool: bool):
    lineworks = LineWorksAPI()

    client_id = env.LW_API_20_CLIENT_ID
    client_secret = env.LW_API_20_CLIENT_SECRET
    service_account_id = env.LW_API_20_SERVICE_ACCOUNT_ID
    privatekey = lineworks.load_privkey("./key/private_20250503130913.key")
    scope = 'board board.read'

    # 画像のID取得
    photo_id = env.PHOTO_ID_OPEN if room_bool else env.PHOTO_ID_CLOSE

    # jwt生成
    jwttoken = lineworks.get_jwt(client_id, service_account_id, privatekey)

    # アクセストークン取得
    res = lineworks.get_access_token(client_id, client_secret, scope, jwttoken)

    access_token = res.get("access_token")
    if not access_token:
        print("Failed to get access token")
        return {"result": 500, "body": "Failed to get access token"}

    with open("./data/lineworks_id_list.json", "r", encoding="utf-8") as f:
        json_file_data = json.load(f)

    if json_file_data.get("RoomInfoBoardId") == 0:
        # 掲示板のIDを取得し保存する
        response = lineworks.save_board_of_room_info(access_token)
        with open("./data/lineworks_id_list.json", "r", encoding="utf-8") as f:
            json_file_data = json.load(f)

        # エラー処理
        if not response["response_code"] == 200:
            print(f"Failed to post to board: {response['body']}")
            return {"result": 500, "body": "Failed to save board of room"}

    if json_file_data.get("BoardPostId") == 0:
        # 掲示板に投稿
        board_id = json_file_data.get("RoomInfoBoardId")

        content = {
            "title": "委員会室・在室情報",
            "body": f'<img class="lnk_img _wh_img" src="https://lh3.googleusercontent.com/d/{photo_id}" border="0" data-file-type="png" width="400" data-image-ratio="0.71" data-image-scale="SCALE_SMALL" data-image-border="false" style="border:0px;max-width:100%;cursor:pointer;vertical-align:text-bottom">',
            "sendNotifications": False
        }
        response = lineworks.register_board_post(access_token, board_id, content)

        with open("./data/lineworks_id_list.json", "r", encoding="utf-8") as f:
            json_file_data = json.load(f)

        # エラー処理
        if not response["response_code"] == 201:
            print(f"Failed to post to board: {response['body']}")
            return {"result": 500, "body": "Failed to post to board"}

    # 掲示板の投稿を変更
    board_id = json_file_data.get("RoomInfoBoardId")
    post_id = json_file_data.get("BoardPostId")
    response = lineworks.get_board_post(access_token, board_id, post_id)

    content = {
        "title": "委員会室・在室情報",
        "body": f'<img class="lnk_img _wh_img" src="https://lh3.googleusercontent.com/d/{photo_id}" border="0" data-file-type="png" width="400" data-image-ratio="0.71" data-image-scale="SCALE_SMALL" data-image-border="false" style="border:0px;max-width:100%;cursor:pointer;vertical-align:text-bottom">',
        "sendNotifications": False
    }

    if response["response_code"] == 200:
        new_response = lineworks.edit_board_post(access_token, board_id, post_id, content)
        if not new_response["response_code"] == 200:
            print(f"Failed to post to board: {response['body']}")
            return {"result": 500, "body": "Failed to post to board"}
        else:
            print(f"Successfully posted to board")
            return {"result": 200, "body": "Success"}
    else:
        print(f"Failed to post to board: {response['body']}")
        return {"result": 500, "body": "Failed to get post"}


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
            multiple_files = [{"attachment", ("room-img.jpg", f)}]
            try:
                requests.post(env.DISCORD_WEBHOOK_URL, data={"payload_json": payload},
                              files=multiple_files)
            except Exception as e:
                print(f"Error sending debug image: {e}")

    # 0時から6時までの間は通知しない
    now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).hour
    if now_time in [22, 23, 0, 1, 2, 3, 4, 5, 6]:
        return {"message": "No notification during this time"}

    if item.room_in:
        if not data.get("RoomIn"):
            if not data.get("InRoomAlreadyNotice"):

                # Discordへ
                post_content = {
                    "username": "在室通知",
                    "content": "## 在室"
                }
                requests.post(env.DISCORD_WEBHOOK_URL, json=post_content)

                # LINEWORKSへ
                response = post_lineworks_board(True)
                if response["result"] != 200:
                    return {"message": "Failed to post to LineWorks board"}

                data["RoomIn"] = True
                data["InRoomAlreadyNotice"] = True
                data["NoRoomAlreadyNotice"] = False
                print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 書き込み前')
                try:
                    with open("./data/people_count.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error writing to file: {e}")
                print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 書き込み後')
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
                requests.post(env.DISCORD_WEBHOOK_URL, json=post_content)

                # LINEWORKSへ
                response = post_lineworks_board(False)
                if response["result"] != 200:
                    return {"message": "Failed to post to LineWorks board"}

                data["RoomIn"] = False
                data["InRoomAlreadyNotice"] = False
                data["NoRoomAlreadyNotice"] = True
                with open("./data/people_count.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                return {"message": "Already notified"}

if __name__ == "__main__":
    uvicorn.run("main_api:app", host=env.API_HOST, port=env.API_PORT, log_level="debug")
