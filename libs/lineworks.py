import json

import jwt
from datetime import datetime

import requests

BASE_API_URL = "https://www.worksapis.com/v1.0"
BASE_AUTH_URL = "https://auth.worksmobile.com/oauth2/v2.0"


class LineWorksAPI:
    def __init__(self):
        super().__init__()

    def get_jwt(self, client_id, service_account_id, privatekey):
        """アクセストークンのためのJWT取得
        """
        current_time = datetime.now().timestamp()
        iss = client_id
        sub = service_account_id
        iat = current_time
        exp = current_time + (60 * 60)  # 1時間

        jws = jwt.encode(
            {
                "iss": iss,
                "sub": sub,
                "iat": iat,
                "exp": exp
            }, key=privatekey, algorithm="RS256")

        return jws

    def get_access_token(self, client_id, client_secret, scope, jws):
        """アクセストークン取得"""
        url = '{}/token'.format(BASE_AUTH_URL)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params = {
            "assertion": f"{jws}",
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": f"{client_id}",
            "client_secret": f"{client_secret}",
            "scope": scope
        }
        form_data = params
        r = requests.post(url=url, data=form_data, headers=headers)
        body = json.loads(r.text)
        return body

    def refresh_access_token(self, client_id, client_secret, refresh_token):
        """アクセストークン更新"""
        url = '{}/token'.format(BASE_AUTH_URL)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        form_data = params
        r = requests.post(url=url, data=form_data, headers=headers)
        body = json.loads(r.text)

        return body

    def get_list_boards(self, access_token):
        """掲示板の一覧を取得する"""
        url = "{}/boards".format(BASE_API_URL)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token)
        }
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            return {"response_code": r.status_code, "body": r.json()}
        else:
            return {"response_code": r.status_code, "body": r.content.decode("utf-8")}

    def save_board_of_room_info(self, access_token):
        """掲示板のIDを取得し保存する"""

        r = self.get_list_boards(access_token)
        if not r["response_code"] == 200:
            print(r["body"])
            raise Exception("掲示板の取得に失敗しました")

        with open("./data/lineworks_id_list.json", "r", encoding="utf-8") as f:
            json_file_data = json.load(f)

        board_name = json_file_data.get("boardName")

        data = r["body"]
        boards = data["boards"]
        for board in boards:
            if board["boardName"] == board_name:
                with open("./data/lineworks_id_list.json", "w", encoding="utf-8") as f:
                    json_file_data["RoomInfoBoardId"] = board["boardId"]
                    json.dump(json_file_data, f, ensure_ascii=False, indent=4)

        return True

    def register_board_post(self, access_token, board_id, content):
        """掲示板に投稿を登録する"""
        with open("./data/lineworks_id_list.json", "r", encoding="utf-8") as f:
            json_file_data = json.load(f)

        url = "{}/boards/{}/posts".format(BASE_API_URL, board_id)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token)
        }
        params = content
        form_data = json.dumps(params)
        r = requests.post(url=url, data=form_data, headers=headers)
        if r.status_code == 201:
            res_json = r.json()
            json_file_data["BoardPostId"] = res_json.get("postId")
            with open("./data/lineworks_id_list.json", "w", encoding="utf-8") as f:
                json.dump(json_file_data, f, ensure_ascii=False, indent=4)
            return {"response_code": r.status_code, "body": r.json()}
        else:
            return {"response_code": r.status_code, "body": r.content.decode("utf-8")}

    def get_board_post(self, access_token, board_id, post_id):
        """掲示板の投稿を取得する"""
        url = "{}/boards/{}/posts/{}".format(BASE_API_URL, board_id, post_id)
        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            return {"response_code": r.status_code, "body": r.json()}
        else:
            return {"response_code": r.status_code, "body": r.content.decode("utf-8")}

    def edit_board_post(self, access_token, board_id, post_id, content):
        """掲示板の投稿を編集する"""
        url = "{}/boards/{}/posts/{}".format(BASE_API_URL, board_id, post_id)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token)
        }

        params = content
        form_data = json.dumps(params)
        r = requests.put(url=url, data=form_data, headers=headers)

        if r.status_code == 200:
            return {"response_code": r.status_code, "body": r.json()}
        else:
            return {"response_code": r.status_code, "body": r.content.decode("utf-8")}
