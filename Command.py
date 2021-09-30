from dosdefence import *
from os import getenv
from function import *
import sqlite3
from interact_with_imgur import uploadAndGetPhoto
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random

# preparation
userStatus = {}
addName = {}
addImg = {}
addWord = {}

userUpdate = {}

def startbot(update, bot):
    if(isDos(update)): return
    Send(update, "hihi, 我是{0}".format(GetConfig("name")))
    Send(update, "按 /help 取得說明")

def help(update, bot):
    if(isDos(update)): return
    Send(update, GetConfig("helpText"))

def list(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    sql = sqlite3.connect( getenv("DATABASENAME") )
    cur = sql.cursor()
    
    cur.execute("Select Name from Data")

    text = []
    allPhoto = cur.fetchall()
    cur.close()
    sql.close()

    for result in allPhoto:
        if result[0] not in text:
            text.append( result[0])


    if(len(allPhoto)==0):
        Send(update, "目前沒有東西喔，請使用 /add 來新增")
    else:
        userUpdate.update({userID: update})
        buttons = []
        for i in range(0, len(text), 3):
            buttons.append([InlineKeyboardButton(s, callback_data = "{0} {1}".format(s, userID)) for s in text[i:min(i+3, len(text))]])

        update.message.reply_text("現在有：", reply_markup = InlineKeyboardMarkup(buttons))

def setVal(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    
    if str(userID) not in getenv('DEVELOPER_ID'): return
    
    text = ' '.join(update.message.text.split(' ')[1:])

    try:
        sql = sqlite3.connect( getenv("DATABASENAME") )
        sql.execute(text)
        sql.commit()
        sql.close()
        
        reloadDosParam()
        Send(update, "指令完成")
    except:
        Send(update, "指令似乎哪裡錯了")
    return

def add(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    
    if str(userID) not in getenv('DEVELOPER_ID') and GetConfig('isAddDeleteOpen')=='0': return
    
    userStatus.update({userID:"waitName"})
    Send(update, "輸入名字", force=True)

def getRandomReply(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    text = update.message.text.split(' ')
    if len(text)==1:
        userStatus.update({userID:"waitDetail"})
        Send(update, "輸入問題", force=True)
    else:
        randomReply(update)

def randomReply(update):
    userID = update.message.from_user.id

    againRange = float(GetConfig('askAgainRange'))
    probability = random.random()
    successful = random.random()-probability

    if(successful<-againRange):
        Send(update, "Yes")
    elif (successful>againRange):
        Send(update, "No")
    else:
        userStatus.update({userID:"waitDetail"})
        Send(update, "Ask me again", True)
        return
        
    if userID in userStatus:
        del userStatus[userID]

def finding(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    text = update.message.text.split(' ')
    if(len(text)==1):
        userStatus.update({userID:"findName"})
        Send(update, "輸入名字", force=True)
        return
    text = ' '.join(text[1:])
    findBody(update, text)

def findBody(update, text):
    userID = update.message.from_user.id
    text = pureString(text)

    sql = sqlite3.connect( getenv("DATABASENAME") )
    cur = sql.cursor()
    command = "Select Name, Image, Word from Data where Name GLOB '*{0}*'".format(text)
    print(command)
    cur.execute(command)
    allData = cur.fetchall()
    cur.close()
    sql.close()
    
    if(len(allData)==0):
        Send(update, "查無結果")
        return

    foundPhoto = False
    for result in allData:
        if result[0] == text:
            SendPhoto(update, result[1])
            Send(update, result[2])
            foundPhoto = True

    if foundPhoto: return
    nameList = []
    for result in allData:
        if result[0] not in nameList:
            nameList.append( result[0] )

    userUpdate.update({userID: update})
    buttons = []
    for i in range(0, len(nameList), 3):
        buttons.append([InlineKeyboardButton(s, callback_data = "{0} {1}".format(s, userID)) for s in nameList[i:min(i+3, len(nameList))]])

    update.message.reply_text("猜你想查：",
    reply_markup = InlineKeyboardMarkup(buttons))

def delete(update, bot):
    if(isDos(update)): 
        print(dos_defence)
        return
    userID = update.message.from_user.id
    if str(userID) == getenv('DEVELOPER_ID'):
        userStatus.update({userID:"delName"})
        Send(update, "輸入名字", force=True)

def callback(update, bot):
    replyText = update.callback_query.data.split(" ")
    userID = int(replyText[-1])
    if userID not in userUpdate:
        update.callback_query.edit_message_text('按鈕已過期')
        return
    
    text = ' '.join(replyText[:-1])

    
    update2 = userUpdate[userID]
    del userUpdate[userID]
    if(isDos(update2)): return
    update.callback_query.edit_message_text(text)

    sql = sqlite3.connect( getenv("DATABASENAME") )
    cur = sql.cursor()
    cur.execute("Select Image, Word from Data where Name = '{0}'".format(text))
    allPhoto = cur.fetchall()
    cur.close()
    sql.close()
    print(text)
    for result in allPhoto:
        SendPhoto(update2, result[0])
        Send(update2, result[1])
    if(len(allPhoto)==0):
        Send(update2, "查無結果")

def cancel(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    if userID in userStatus:
        del userStatus[userID]
    if userID in addName:
        del addName[userID]
    if userID in addImg:
        del addImg[userID]
    if userID in addWord:
        del addWord[userID]
    if userID in userUpdate:
        del userUpdate[userID]

    Send(update, "指令取消。")

def getText(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    text = update.message.text
    print(text)

    if userID in userStatus:
        state = userStatus[userID]
        print(state)
        if state == 'waitName':
            addName.update({userID:text})
            Send(update, '名字為：{0}'.format(text))
            Send(update, '請輸入內文或傳送未壓縮照片', force=True)
            userStatus.update({userID:"waitContent"})
            

        elif state == 'waitContent':
            addWord.update({userID:text})
            print(addWord[userID])
            if(userID not in addImg):
                Send(update, '內文新增完成, 可以重打內文或使用 /end 完成新增', True)
            else:
                Send(update, '內文新增完成, 請傳送未壓縮照片或使用 /end 完成新增', True)

        elif state == 'delName':
            sql = sqlite3.connect( getenv("DATABASENAME") ) 
            cur = sql.cursor()
            cur.execute("delete from Data where Name = '{0}'".format(text))
            sql.commit()
            cur.close()
            sql.close()
            Send(update, "刪除 {0}".format(text))
            del userStatus[userID]
        elif state == 'findName':
            findBody(update, text)

            del userStatus[userID]
        elif state == 'waitDetail':
            randomReply(update)
        
def getPhoto(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    
    if(userStatus[userID]=='waitContent'):
        Send(update, '不要壓縮，傳檔案', True)

def getFile(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id

    if(userStatus[userID]=='waitContent' and userID not in addImg):
        Send(update, '上傳中...')
        path = uploadAndGetPhoto(update.message.document.file_id)
        addImg[userID] = path

        Send(update, '照片上傳成功。')
        Send(update, '可以輸入描述或使用 /end 結束', True)
    
def endAdd(update, bot):
    if(isDos(update)): return
    userID = update.message.from_user.id
    if(userStatus[userID]=='waitContent'):
        sql = sqlite3.connect( getenv("DATABASENAME") ) 
        cur = sql.cursor()
        if(userID not in addImg):
            addImg[userID] = ''
        if(userID not in addWord):
            addWord[userID] = ''
        if addImg[userID] == '' and addWord[userID] == '':
            Send(update, '得先輸入內文或傳送未壓縮圖片', True)
            return

        command = "insert into Data values('{0}', '{1}', '{2}')".format(addName[userID], addImg[userID], addWord[userID])

        cur.execute(command)
        sql.commit()

        cur.close()
        sql.close()

        Send(update, "新增 {0}".format(addName[userID]))

        del userStatus[userID]
        del addName[userID]
        del addImg[userID]
        del addWord[userID]
