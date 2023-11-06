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


def main():
    
    # 建立連接 (修改)
    connection = psycopg2.connect(
        host="dpg-cl490h1novjs73bvmclg-a.oregon-postgres.render.com",
        port="5432",
        database="dyps",
        user="admin",
        password="1tP8cSuVatmtgGQL4pOHMYEBGhnfPPQC"
    )
    cursor = connection.cursor()


    user_message='111'
    user_line_id='222'
    user_nickname='333333'
    
# 建立使用者訊息
    # timestamp = datetime.now()
    #user_nickname = event.source.user_display_name
    response_word = ''
    
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
                print(response_word)

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
                query = "SELECT B.mission_desc FROM user_mission A join mission B ON A.mission_no=B.mission_no join user C ON A.user_no=C.user_no WHERE C.user_id =%s AND A.mission_no=%s"
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
    
    except psycopg2.Error as e:
        print("資料庫錯誤:", e)
        #print("資料庫錯誤啦!")

    finally:
        cursor.close()
        connection.close()
if __name__ == "__main__":
    main()