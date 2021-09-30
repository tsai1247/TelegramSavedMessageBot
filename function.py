from os import getenv
import sqlite3
from telegram import ForceReply

def Send(update, msg, force = False):
    if msg == None or msg == '': return
    if(force):
        update.message.reply_text(msg, reply_markup = ForceReply(selective=force))
    else:
        update.message.reply_text(msg)
        
def SendPhoto(update, photolink):
    if photolink == None or photolink == '': return
    update.message.reply_photo(photolink)

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