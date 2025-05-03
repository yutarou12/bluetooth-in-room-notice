import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数の読み込み
API_TOKEN: str = os.getenv("API_TOKEN")
API_HOST: str = os.getenv("API_HOST")
API_PORT: int = int(os.getenv("API_PORT", "9000"))
VIDEO_PATH: str = os.getenv("VIDEO_PATH")
DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL")

LW_API_20_CLIENT_ID: str = os.getenv("LW_API_20_CLIENT_ID")
LW_API_20_CLIENT_SECRET: str = os.getenv("LW_API_20_CLIENT_SECRET")
LW_API_20_SERVICE_ACCOUNT_ID: str = os.getenv("LW_API_20_SERVICE_ACCOUNT_ID")
LW_API_20_PRIVATEKEY: str = os.getenv("LW_API_20_PRIVATEKEY")
LW_API_20_BOT_ID: str = os.getenv("LW_API_20_BOT_ID")
LW_API_20_BOT_SECRET: str = os.getenv("LW_API_20_BOT_SECRET")
LW_API_20_CHANNEL_ID: str = os.getenv("LW_API_20_CHANNEL_ID")

PHOTO_ID_OPEN: str = os.getenv("PHOTO_ID_OPEN")
PHOTO_ID_CLOSE: str = os.getenv("PHOTO_ID_CLOSE")
