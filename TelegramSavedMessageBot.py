#!/usr/bin/env python3
# coding=utf-8
import os
from requests.api import delete
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from Command import *
from dotenv import load_dotenv

load_dotenv()

# Main function
def main():
    
    updater = Updater( os.getenv("TELEGRAM_TOKEN") )

# 一般指令

    # 開啟與幫助
    updater.dispatcher.add_handler(CommandHandler('start', startbot))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    
    # 新增 (可在 Database.db/Config 中，設定為管理員限定)
    updater.dispatcher.add_handler(CommandHandler('set', add))
    updater.dispatcher.add_handler(CommandHandler('add', add))
    updater.dispatcher.add_handler(CommandHandler('end', endAdd))
    
    # 刪除 (可在 Database.db/Config 中，設定為管理員限定)
    updater.dispatcher.add_handler(CommandHandler('del', delete))
    updater.dispatcher.add_handler(CommandHandler('delete', delete))
    
    # 搜尋
    updater.dispatcher.add_handler(CommandHandler('list', list))
    updater.dispatcher.add_handler(CommandHandler('find', finding))
    
    # 以 sqlite 語法設定參數 (必為管理員限定)
    updater.dispatcher.add_handler(CommandHandler('update', setVal))

    # 隨機回覆小助手
    updater.dispatcher.add_handler(CommandHandler('conch', getRandomReply))

    # 指令取消
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
    

# 其他類型回覆

    # 文字
    updater.dispatcher.add_handler(MessageHandler(Filters.text, getText))
    
    # 圖片(經 Telegram 壓縮)
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, getPhoto))
    
    # 檔案 或 未經壓縮圖片
    updater.dispatcher.add_handler(MessageHandler(Filters.document, getFile))
    
    # 按鈕
    updater.dispatcher.add_handler(CallbackQueryHandler(callback))


# Bot Start
    print("Bot Server Running...")

    updater.start_polling()
    updater.idle()


# HEAD OF PROGRAM
if __name__ == '__main__':
    main()

