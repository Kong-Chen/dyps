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
import random
import string
from datetime import datetime

app = Flask(__name__)

# 設置你的 LINE Bot 的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

def generate_random_code(length):
    characters = string.ascii_lowercase + string.digits
    random_code = ''.join(random.choice(characters) for i in range(length))
    return random_code

# 註冊 UUID 型別的適應器
def adapt_uuid(uuid):
    return adapt(str(uuid))
register_adapter(uuid.UUID, adapt_uuid)


#發送line_notify
def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    token = 'RJhGOMUMHuvBGXM8vpi5IgoGuNLREF7bwKx6heTTQLK' #Group
    headers = {
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response


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
    connection = psycopg2.connect(
        host="dpg-cl490h1novjs73bvmclg-a.oregon-postgres.render.com",
        port="5432",
        database="dyps",
        user="admin",
        password="1tP8cSuVatmtgGQL4pOHMYEBGhnfPPQC"
    )
    
    # 建立使用者訊息
    # timestamp = datetime.now()
    user_message = event.message.text
    user_line_id = event.source.user_id
    #user_nickname = event.source.user_display_name
    response_word = ''
    is_admin = None
    if event.source.type == 'user':
        profile = line_bot_api.get_profile(user_line_id)
        user_nickname = profile.display_name
    
    try:
        #判斷身分
        cursor = connection.cursor()
        query = "SELECT admin_no FROM admin WHERE admin_id = %s"
        cursor.execute(query, (user_line_id,))
        is_admin = cursor.fetchone()

        if is_admin:
            if user_message =='1118報表':
                cursor = connection.cursor()
                query = "SELECT count(*) FROM user"
                cursor.execute(query, ())
                aaa = cursor.fetchone()
                user_count = aaa[0]
                query = "SELECT COUNT(distinct user_no) FROM user_mission WHERE mission_no = 1"
                cursor.execute(query, ())
                aaa = cursor.fetchone()
                mission1_count = aaa[0]
                query = "SELECT COUNT(distinct user_no) FROM user_mission WHERE mission_no = 2"
                cursor.execute(query, ())
                aaa = cursor.fetchone()
                mission2_count = aaa[0]
                query = "SELECT COUNT(distinct user_no) FROM user_mission WHERE mission_no = 3"
                cursor.execute(query, ())
                aaa = cursor.fetchone()
                mission3_count = aaa[0]
                query = "SELECT COUNT(distinct user_no) FROM user_mission WHERE mission_no = 4"
                cursor.execute(query, ())
                aaa = cursor.fetchone()
                mission4_count = aaa[0]
                response_word ='已參加遊戲人數:' + str(user_count) + '人' + '\n' + '第一關完成人數:' + str(mission1_count) + '人' + '\n' + '第二關完成人數:' + str(mission2_count) + '人' + '\n' + '第三關完成人數:' + str(mission3_count) + '人' + '\n' + '第四關完成人數:' + str(mission4_count) + '人'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=response_word)
                )

        else:   
            #判斷使用者資料
            query = "SELECT user_no FROM users WHERE user_id = %s"
            cursor.execute(query, (user_line_id,))
            user_no = cursor.fetchone()
            if not user_no:
                query = "INSERT INTO users (user_id, user_name) VALUES (%s, %s)"
                data = (user_line_id, user_nickname)  
                cursor.execute(query, data)
                connection.commit()
                query = "SELECT user_no FROM users WHERE user_id = %s"
                cursor.execute(query, (user_line_id,))
                user_no = cursor.fetchone()
        
            #判斷對話
            query = "SELECT mission_no,mission_desc FROM mission WHERE mission_code = %s"
            cursor.execute(query, (user_message,))
            mission = cursor.fetchone()
            if mission:
                #如果有中密碼
                query = "SELECT B.mission_desc FROM user_mission A join mission B ON A.mission_no=B.mission_no join users C ON A.user_no=C.user_no WHERE C.user_id =%s AND A.mission_no=%s"
                data = (user_line_id, mission[0])
                cursor.execute(query, data)
                mission_desc = cursor.fetchone()
                if not mission_desc:
                    #塞入獲獎紀錄
                    current_datetime = datetime.now()
                    query = "INSERT INTO user_mission (user_no, mission_no,mission_time) VALUES (%s, %s, %s)"
                    data = (user_no[0], mission[0],current_datetime)  # 您的資料
                    cursor.execute(query, data)
                    connection.commit()
                    # LINE 
                    message = '\n' +str(user_nickname)+'剛剛完成第'+ str(mission[0])+'關卡'
                    response = send_line_notify(message)
                    print(response)
    
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