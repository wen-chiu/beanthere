import json
from datetime import datetime


class LineHelpers:
    def __init__(self):
        pass

    def create_main_menu_flex(self, liff_id):
        """建立主選單 Flex Message"""
        return {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://i.imgur.com/example-hero.jpg",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "BeanThere",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": "旅遊分帳日記系統",
                        "size": "sm",
                        "color": "#666666",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🧳",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": "管理你的旅行與分帳",
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 4
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💰",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": "智能 OCR 收據辨識",
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 4
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "📊",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": "自動分帳與統計分析",
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 4
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "開始使用",
                            "uri": f"https://liff.line.me/{liff_id}/dashboard"
                        }
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "flex": 1,
                                "action": {
                                    "type": "postback",
                                    "label": "新增旅行",
                                    "data": "action=create_trip"
                                }
                            },
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "flex": 1,
                                "action": {
                                    "type": "postback",
                                    "label": "我的旅行",
                                    "data": "action=my_trips"
                                }
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "flex": 1,
                                "action": {
                                    "type": "uri",
                                    "label": "記帳",
                                    "uri": f"https://liff.line.me/{liff_id}/expense"
                                }
                            },
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "flex": 1,
                                "action": {
                                    "type": "postback",
                                    "label": "分帳結果",
                                    "data": "action=settlement"
                                }
                            }
                        ]
                    }
                ]
            }
        }

    def create_trips_list_flex(self, trips, liff_id):
        """建立旅行列表 Flex Message"""
        contents = []

        for trip in trips[:10]:  # 最多顯示 10 個旅行
            trip_bubble = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": trip.get('name', '未命名旅行'),
                            "weight": "bold",
                            "size": "lg",
                            "wrap": True
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "📅",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": f"{trip.get('start_date', '')} - {trip.get('end_date', '')}",
                                    "size": "sm",
                                    "color": "#666666",
                                    "flex": 4,
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "👥",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": f"{trip.get('member_count', 0)} 位旅伴",
                                    "size": "sm",
                                    "color": "#666666",
                                    "flex": 4
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "💰",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": f"NT$ {trip.get('total_expense', 0):,}",
                                    "size": "sm",
                                    "color": "#666666",
                                    "flex": 4
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "height": "sm",
                            "flex": 1,
                            "action": {
                                "type": "uri",
                                "label": "查看詳情",
                                "uri": f"https://liff.line.me/{liff_id}/trip/{trip.get('id')}"
                            }
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "height": "sm",
                            "flex": 1,
                            "action": {
                                "type": "uri",
                                "label": "記帳",
                                "uri": f"https://liff.line.me/{liff_id}/expense?trip_id={trip.get('id')}"
                            }
                        }
                    ]
                }
            }
            contents.append(trip_bubble)

        return {
            "type": "carousel",
            "contents": contents
        }

    def create_settlement_flex(self, settlement_data):
        """建立分帳結果 Flex Message"""
        trip_name = settlement_data.get('trip_name', '未命名旅行')
        total_expense = settlement_data.get('total_expense', 0)
        settlements = settlement_data.get('settlements', [])

        # 建立結算項目
        settlement_contents = []
        for settlement in settlements:
            payer = settlement.get('payer_name', '')
            payee = settlement.get('payee_name', '')
            amount = settlement.get('amount', 0)

            settlement_item = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": payer,
                        "size": "sm",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": "→",
                        "size": "sm",
                        "align": "center",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": payee,
                        "size": "sm",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": f"NT$ {amount:,}",
                        "size": "sm",
                        "align": "end",
                        "weight": "bold",
                        "color": "#FF5551",
                        "flex": 2
                    }
                ],
                "margin": "md"
            }
            settlement_contents.append(settlement_item)

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "分帳結果",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "lg"
                    },
                    {
                        "type": "text",
                        "text": trip_name,
                        "size": "sm",
                        "color": "#666666",
                        "margin": "sm"
                    }
                ],
                "paddingBottom": "sm"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "總消費金額",
                                "size": "md",
                                "color": "#666666"
                            },
                            {
                                "type": "text",
                                "text": f"NT$ {total_expense:,}",
                                "size": "md",
                                "weight": "bold",
                                "align": "end"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "清算明細",
                        "weight": "bold",
                        "size": "md",
                        "margin": "lg"
                    }
                ] + settlement_contents
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "查看詳細報表",
                            "data": f"action=detailed_report&trip_id={settlement_data.get('trip_id')}"
                        }
                    }
                ]
            }
        }

    def create_expense_form_flex(self, trip_id, members):
        """建立記帳表單 Flex Message (簡化版)"""
        member_options = []
        for member in members:
            member_options.append({
                "type": "button",
                "style": "secondary",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": member.get('name', ''),
                    "data": f"action=select_payer&trip_id={trip_id}&member_id={member.get('id')}"
                }
            })

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "選擇付款人",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "lg"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": member_options
            }
        }
