from os import getenv
import sqlite3
from telegram import ForceReply, InlineKeyboardMarkup
from updater import updater

def Reply(update, msg, force = False):
    if msg == None or msg == '': return
    if(force):
        update.message.reply_text(msg, reply_markup = ForceReply(selective=force))
    else:
        update.message.reply_text(msg)

def SendButton(update, msg, buttons):
    if msg==None: msg = ''
    updater.bot.send_message(update.message.chat_id, "現在有：", reply_markup = InlineKeyboardMarkup(buttons))

def Send(update, msg, force = False):
    if msg == None or msg == '': return
    if(force):
        updater.bot.send_message(update.message.chat_id, msg, reply_markup = ForceReply(selective=force))
    else:
        updater.bot.send_message(update.message.chat_id, msg)

def SendPhoto(update, photolink):
    if photolink == None or photolink == '': return
    updater.bot.send_photo(update.message.chat_id, photolink)

def ReplyPhoto(update, photolink):
    if photolink == None or photolink == '': return
    update.message.reply_photo(photolink)

def SendPhotoWithCaption(update, bot, caption, photolink):
    if photolink == None or photolink == '': return
    updater.bot.send_photo(update.message.chat_id, photolink, caption = caption)

def ReplyPhotoWithCaption(update, bot, caption, photolink):
    if photolink == None or photolink == '': return
    update.message.reply_photo(photolink, caption = caption)

# sql injection defense
def pureString(text: str):
    text = text.replace("'", "''")
    text = text.replace("[", "[[]")
    text = text.replace("%", "[%]")
    text = text.replace("*", "[*]")

    return text

def GetConfig(name: str):
    sql = sqlite3.connect(getenv("DATABASENAME"))
    cur = sql.cursor()
    cur.execute("select Val from Config where Name = '{0}'".format(name))
    data = cur.fetchone()
    if(data == None or len(data)==0 ):  # init
        initVal = '20'
        cur.close()
        cur = sql.cursor()
        cur.execute("insert into Config values('{0}', {1})".format(name, initVal))
        sql.commit()
        data = initVal
    else:
        data = data[0]
    cur.close()
    sql.close()

    return data

def isDeveloper(userID, allowOpen = True):
    developer = getenv('DEVELOPER_ID')
    if(allowOpen):
        return str(userID) in developer or developer == '' or developer == '*' or GetConfig('isAddDeleteOpen')=='1'
    else:
        return str(userID) in developer or developer == '' or developer == '*'

def getUserID(update):
    return update.message.from_user.id