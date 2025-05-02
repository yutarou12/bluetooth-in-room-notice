
Wi-Fiカメラのデータと物体検出アルゴリズム「YOLO」を用いた、在室通知サービスです。

Presence confirmation service using Wi-Fi cameras and AI.

## 機能
 - 在室時 : 
   - WiFiカメラの映像を元に、在室者数をカウントし、Discordに通知します。
   - 在室者数をカウントするために、YOLOv5を使用しています。
 - 不在時 :
   - WiFiカメラの映像を元に、在室者数をカウントし、5分間不在であれば、Discordに通知します。

## 対応連絡ツール
  - [x] Discord
  - [ ] LINEWORKS

## 環境変数
 - VIDEO_PATH : `WiFiカメラの映像のURL`
 - API_TOKEN : `任意の文字列`
 - DISCORD_WEBHOOK_URL : `Discordの通知先チャンネルのWebhookURL`