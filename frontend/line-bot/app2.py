import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent,
    FlexSendMessage, QuickReply, QuickReplyButton, PostbackAction,
    URIAction, MessageAction
)

from handlers.message_handler import MessageHandler
from handlers.postback_handler import PostbackHandler
from utils.line_helpers import LineHelpers

app = Flask(__name__)

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
LIFF_ID = os.getenv('LIFF_ID', '')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化處理器
message_handler = MessageHandler(line_bot_api, LIFF_ID)
postback_handler = PostbackHandler(line_bot_api, LIFF_ID)
line_helpers = LineHelpers()


@app.route("/callback", methods=['POST'])
def callback():
    """LINE Bot Webhook callback"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except LineBotApiError as e:
        print(f"LINE Bot API Error: {e}")
        abort(500)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """處理文字訊息"""
    message_handler.handle_text_message(event)


@handler.add(PostbackEvent)
def handle_postback(event):
    """處理 Postback 事件"""
    postback_handler.handle_postback(event)


@app.route("/", methods=['GET'])
def health_check():
    """健康檢查"""
    return {
        "status": "ok",
        "service": "BeanThere LINE Bot",
        "version": "1.0.0"
    }


@app.route("/menu", methods=['GET'])
def get_menu():
    """取得主選單 Flex Message"""
    user_id = request.args.get('user_id')
    if not user_id:
        return {"error": "user_id is required"}, 400

    menu_flex = line_helpers.create_main_menu_flex(LIFF_ID)
    return {"flex_message": menu_flex}


if __name__ == "__main__":
    # 開發環境設定
    app.run(host='0.0.0.0', port=5000, debug=True)
