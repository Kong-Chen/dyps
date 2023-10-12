from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage
import os
import uuid
from psycopg2.extensions import adapt, register_adapter
import psycopg2
from datetime import datetime
import mysql.connector
import requests

app = Flask(__name__)

# 設置你的 LINE Bot 的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])


# 註冊 UUID 型別的適應器
def adapt_uuid(uuid):
    return adapt(str(uuid))
register_adapter(uuid.UUID, adapt_uuid)


@app.route("/callback", methods=['POST'])
def callback():
    # 取得 request headers 中的 X-Line-Signature 屬性
    signature = request.headers['X-Line-Signature']
    
    # 取得 request 的 body 內容
    body = request.get_data(as_text=True)
    
    try:
        # 驗證簽章
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    # 建立連接 (修改)
    connection = mysql.connector.connect(
        host="fortune.ckgadenebkdr.ap-northeast-3.rds.amazonaws.com",
        port="3306",
        database="members",
        user="admin",
        password="Aa123456"
    )
    
    # 收到使用者的訊息
    timestamp = datetime.now()
    user_message = event.message.text
    user_line_id = event.source.user_id
    user_id = None
    user_nickname = None
    
    cursor = connection.cursor()
    cursor.execute("SELECT member_name FROM member")
    existing_user = cursor.fetchone()



    if event.source.type == 'user':
        profile = line_bot_api.get_profile(user_line_id)
        user_nickname = profile.display_name

    try:
        if user_message =='Nasa':
            # API 密鑰
            api_key = "74K2SccksUYY9UL8P6FPb7oz3Vn0JFacjP5ZPdPh"

            # API 網址
            url = "https://api.nasa.gov/planetary/apod"

            # API 參數
            params = {
                "api_key": api_key
            }

            # 發送 API 請求
            response = requests.get(url, params=params)

            # 取得 API 的返回值
            data = response.json()

            # 顯示照片的網址
            print("Picture URL:", data["url"])
            line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=data["url"],
                preview_image_url=data["url"]
        )
    )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=existing_user[0])
        )
        
    except psycopg2.Error as e:
        # print("資料庫錯誤:", e)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="資料庫錯誤啦!")
        )

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # 在本地運行時才啟動伺服器
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))