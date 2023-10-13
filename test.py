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
    connection = mysql.connector.connect(
        host="fortune.ckgadenebkdr.ap-northeast-3.rds.amazonaws.com",
        port="3306",
        database="prod_dyps",
        user="admin",
        password="Aa123456"
    )
    cursor = connection.cursor()


    user_message='111'
    user_line_id='222'
    
    query = "SELECT mission_no,mission_desc FROM prod_dyps.mission WHERE mission_code = %s"
    cursor.execute(query, (user_message,))
    mission = cursor.fetchone()
    if mission[0]:
        #如果有中密碼
        query = "SELECT B.mission_desc FROM prod_dyps.user_mission A join prod_dyps.mission B ON A.mission_no=B.mission_no join prod_dyps.user C ON A.user_no=C.user_no WHERE C.user_id =%s AND A.mission_no=%s"
        data = (user_line_id, mission[0])  # 您的資料
        cursor.execute(query, data)
        mission_desc = cursor.fetchone()
        if mission_desc:
            print ("你已經玩過:" + mission_desc)
        else:
            #塞入獲獎紀錄
            current_datetime = datetime.now()
            query = "INSERT INTO prod_dyps.user_mission (user_no, mission_no,mission_time) VALUES (%s, %s, %s)"
            data = (1, mission[0],current_datetime)  # 您的資料
            cursor.execute(query, data)
            connection.commit()
            print ("恭喜你成功完成:"+mission[1])
    else:
        print ("你是普通人不要亂講話!!!!")
    cursor.close()
    connection.close()
if __name__ == "__main__":
    main()