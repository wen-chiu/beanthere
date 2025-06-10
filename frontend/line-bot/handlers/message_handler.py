import json
import requests
from linebot.models import (
    TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton,
    PostbackAction, URIAction, MessageAction
)
from utils.line_helpers import LineHelpers


class MessageHandler:
    def __init__(self, line_bot_api, liff_id):
        self.line_bot_api = line_bot_api
        self.liff_id = liff_id
        self.line_helpers = LineHelpers()
        self.backend_api = "http://localhost:8000/api/v1"  # 後端 API 位址

    def handle_text_message(self, event):
        """處理文字訊息"""
        user_id = event.source.user_id
        message_text = event.message.text.strip()

        # 指令映射
        command_handlers = {
            "選單": self._send_main_menu,
            "menu": self._send_main_menu,
            "新增旅行": self._create_new_trip,
            "我的旅行": self._show_my_trips,
            "記帳": self._start_expense_entry,
            "分帳": self._show_settlement,
            "幫助": self._send_help,
            "help": self._send_help
        }

        # 檢查是否為特定指令
        if message_text.lower() in command_handlers:
            command_handlers[message_text.lower()](event)
        else:
            # 嘗試智能回應
            self._handle_smart_response(event, message_text)

    def _send_main_menu(self, event):
        """發送主選單"""
        try:
            main_menu_flex = self.line_helpers.create_main_menu_flex(
                self.liff_id)
            flex_message = FlexSendMessage(
                alt_text="BeanThere 主選單",
                contents=main_menu_flex
            )
            self.line_bot_api.reply_message(event.reply_token, flex_message)
        except Exception as e:
            print(f"Error sending main menu: {e}")
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="選單載入失敗，請稍後再試。")
            )

    def _create_new_trip(self, event):
        """建立新旅行"""
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=URIAction(
                label="開始建立旅行",
                uri=f"https://liff.line.me/{self.liff_id}/create-trip"
            )),
            QuickReplyButton(action=MessageAction(
                label="取消",
                text="選單"
            ))
        ])

        message = TextSendMessage(
            text="🧳 準備開始新的旅行嗎？\n\n點選下方按鈕開始建立旅行，或輸入「選單」返回主選單。",
            quick_reply=quick_reply
        )
        self.line_bot_api.reply_message(event.reply_token, message)

    def _show_my_trips(self, event):
        """顯示我的旅行列表"""
        user_id = event.source.user_id

        try:
            # 從後端獲取用戶旅行列表
            response = requests.get(f"{self.backend_api}/trips/user/{user_id}")

            if response.status_code == 200:
                trips = response.json()
                if trips:
                    trips_flex = self.line_helpers.create_trips_list_flex(
                        trips, self.liff_id)
                    flex_message = FlexSendMessage(
                        alt_text="我的旅行列表",
                        contents=trips_flex
                    )
                    self.line_bot_api.reply_message(
                        event.reply_token, flex_message)
                else:
                    message = TextSendMessage(
                        text="您還沒有任何旅行記錄\n\n輸入「新增旅行」開始第一趟旅程！")
                    self.line_bot_api.reply_message(event.reply_token, message)
            else:
                raise Exception("Backend API error")

        except Exception as e:
            print(f"Error fetching trips: {e}")
            message = TextSendMessage(text="載入旅行列表失敗，請稍後再試。")
            self.line_bot_api.reply_message(event.reply_token, message)

    def _start_expense_entry(self, event):
        """開始記帳"""
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=URIAction(
                label="手動記帳",
                uri=f"https://liff.line.me/{self.liff_id}/expense/manual"
            )),
            QuickReplyButton(action=URIAction(
                label="拍照記帳",
                uri=f"https://liff.line.me/{self.liff_id}/expense/ocr"
            )),
            QuickReplyButton(action=MessageAction(
                label="返回選單",
                text="選單"
            ))
        ])

        message = TextSendMessage(
            text="💰 選擇記帳方式：\n\n• 手動記帳：自己輸入消費資訊\n• 拍照記帳：AI 自動辨識收據",
            quick_reply=quick_reply
        )
        self.line_bot_api.reply_message(event.reply_token, message)

    def _show_settlement(self, event):
        """顯示分帳結果"""
        user_id = event.source.user_id

        try:
            # 獲取用戶最新旅行的分帳結果
            response = requests.get(
                f"{self.backend_api}/settlement/user/{user_id}/latest")

            if response.status_code == 200:
                settlement_data = response.json()
                settlement_flex = self.line_helpers.create_settlement_flex(
                    settlement_data)
                flex_message = FlexSendMessage(
                    alt_text="分帳結果",
                    contents=settlement_flex
                )
                self.line_bot_api.reply_message(
                    event.reply_token, flex_message)
            else:
                message = TextSendMessage(text="目前沒有需要分帳的項目")
                self.line_bot_api.reply_message(event.reply_token, message)

        except Exception as e:
            print(f"Error fetching settlement: {e}")
            message = TextSendMessage(text="載入分帳資料失敗，請稍後再試。")
            self.line_bot_api.reply_message(event.reply_token, message)

    def _send_help(self, event):
        """發送幫助訊息"""
        help_text = """🤖 BeanThere 使用說明

📝 基本指令：
• 選單 - 顯示主選單
• 新增旅行 - 建立新的旅行
• 我的旅行 - 查看旅行列表
• 記帳 - 開始新增消費記錄
• 分帳 - 查看分帳結果

💡 功能特色：
• 支援 OCR 收據辨識
• 自動分帳計算
• 多種消費分類
• 旅行日記功能

❓ 需要更多幫助請輸入「選單」開始使用"""

        message = TextSendMessage(text=help_text)
        self.line_bot_api.reply_message(event.reply_token, message)

    def _handle_smart_response(self, event, message_text):
        """智能回應處理"""
        # 簡單的關鍵字匹配
        if any(keyword in message_text for keyword in ["錢", "分帳", "費用", "帳單"]):
            self._start_expense_entry(event)
        elif any(keyword in message_text for keyword in ["旅行", "旅遊", "出遊"]):
            self._show_my_trips(event)
        elif any(keyword in message_text for keyword in ["你好", "哈囉", "hi", "hello"]):
            welcome_message = "Hi！歡迎使用 BeanThere 旅遊分帳系統 🧳\n\n輸入「選單」查看所有功能，或「幫助」了解使用方式。"
            self.line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=welcome_message))
        else:
            # 預設回應
            default_message = "我不太理解您的意思 🤔\n\n請輸入「選單」查看可用功能，或「幫助」了解使用方式。"
            self.line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=default_message))
