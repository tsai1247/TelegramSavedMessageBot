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

def SendButton(update, msg, buttons, chat_id = None):
    if msg==None: msg = ''
    if chat_id == None:
        try:
            chat_id = update.message.chat_id
        except:
            pass
    return updater.bot.send_message(chat_id, msg, reply_markup = InlineKeyboardMarkup(buttons))

def Send(update, msg, force = False, chat_id = None):
    if msg == None or msg == '': return
    if chat_id == None:
        try:
            chat_id = update.message.chat_id
        except:
            pass

    if(force):
        return updater.bot.send_message(chat_id, msg, reply_markup = ForceReply(selective=force))
    else:
        return updater.bot.send_message(chat_id, msg)

def SendPhoto(update, photolink):
    if photolink == None or photolink == '': return
    updater.bot.send_photo(update.message.chat_id, photolink)

def ReplyPhoto(update, photolink):
    if photolink == None or photolink == '': return
    update.message.reply_photo(photolink)

def SendPhotoWithCaption(update, caption, photolink, reply_markup = None, chat_id = None):
    try:
        chat_id = update.message.chat_id
    except:
        pass
    
    if photolink == None or photolink == '': return
    return updater.bot.send_photo(chat_id, photolink, caption = caption, reply_markup = reply_markup)

def ReplyPhotoWithCaption(update, caption, photolink):
    if photolink == None or photolink == '': return
    update.message.reply_photo(photolink, caption = caption)


def SendResult(update, data, reply_markup = None, chat_id = None):
    ret = []
    for i in range(len(data)):
    # for data[i] in data:
        if data[i][0]!='':
            if reply_markup != None and i+1 == len(data):
                ret.append(SendPhotoWithCaption(update, data[i][1], data[i][0], reply_markup, chat_id))
            else:
                ret.append(SendPhotoWithCaption(update, data[i][1], data[i][0], chat_id = chat_id))
        else:
            SendPhoto(update, data[i][0])
            Send(update, data[i][1])
    if(len(data)==0):
        Send(update, "查無結果")
    return ret

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


def getUserID(update): 
    if update.message == None: return None
    return update.message.from_user.id

def getRoomID(update): 
    if update.message == None: return None
    return update.message.chat_id