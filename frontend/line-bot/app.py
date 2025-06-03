from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, URIAction
)
import requests
import json
import os

app = Flask(__name__)

# LINE Bot Configure
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
LIFF_URL = os.getenv('LIFF_URL', 'https://liff.line.me/your-liff-id')

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    if user_message == "開始記帳":
        # Showing menu
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="建立新旅行", text="建立新旅行")),
            QuickReplyButton(action=MessageAction(label="查看旅行", text="查看旅行")),
            QuickReplyButton(action=MessageAction(label="記帳", text="記帳")),
            QuickReplyButton(action=MessageAction(label="查看分帳", text="查看分帳"))
        ])
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請選擇功能：", quick_reply=quick_reply)
        )
    
    elif user_message == "建立新旅行":
        # Sending LIFF Link
        flex_message = create_trip_flex()
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif user_message == "記帳":
        # Sending expense LIFF Link
        flex_message = create_expense_flex()
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif user_message == "查看旅行":
        # Get trip list
        try:
            response = requests.get(f"{API_BASE_URL}/api/trips")
            trips = response.json()
            
            if trips:
                flex_message = create_trips_list_flex(trips)
                line_bot_api.reply_message(event.reply_token, flex_message)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="目前沒有任何旅行記錄")
                )
        except Exception as e:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="取得旅行資料時發生錯誤")
            )
    
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入「開始記帳」來使用功能")
        )

def create_trip_flex():
    bubble = BubbleContainer(
        header=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="建立新旅行", weight="bold", size="lg")
            ]
        ),
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="點擊下方按鈕開啟網頁版來建立新旅行", wrap=True)
            ]
        ),
        footer=BoxComponent(
            layout="vertical",
            contents=[
                ButtonComponent(
                    action=URIAction(uri=f"{LIFF_URL}/create-trip"),
                    text="建立旅行"
                )
            ]
        )
    )
    return FlexSendMessage(alt_text="建立新旅行", contents=bubble)

def create_expense_flex():
    bubble = BubbleContainer(
        header=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="記帳功能", weight="bold", size="lg")
            ]
        ),
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="點擊下方按鈕開啟網頁版來記帳", wrap=True)
            ]
        ),
        footer=BoxComponent(
            layout="vertical",
            contents=[
                ButtonComponent(
                    action=URIAction(uri=f"{LIFF_URL}/expense"),
                    text="開始記帳"
                )
            ]
        )
    )
    return FlexSendMessage(alt_text="記帳功能", contents=bubble)

def create_trips_list_flex(trips):
    contents = []
    for trip in trips[:5]:  # 最多顯示5個
        contents.append(
            TextComponent(
                text=f"🧳 {trip['name']}",
                action=URIAction(uri=f"{LIFF_URL}/trip/{trip['id']}")
            )
        )
    
    bubble = BubbleContainer(
        header=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="我的旅行", weight="bold", size="lg")
            ]
        ),
        body=BoxComponent(
            layout="vertical",
            contents=contents
        )
    )
    return FlexSendMessage(alt_text="旅行列表", contents=bubble)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
