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
    query = "SELECT mission_desc,mission_code FROM prod_dyps.mission"
    cursor.execute(query, ())
    aaa = cursor.fetchall()
    bbb ="關卡密碼如下:"
    for a in aaa:
        bbb += '\n' + a[0]+'的密碼是'+a[1]
    print (bbb)
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()