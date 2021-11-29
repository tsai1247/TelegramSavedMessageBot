from logging import exception
from typing import List

from telegram.utils.helpers import escape_markdown
from dosdefence import *
from os import getenv
from function import *
import sqlite3
from interact_with_imgur import uploadAndGetPhoto
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random
from permissionCheck import Compare, IsCommandAllowed

# preparation
userStatus = {}
addName = {}
addImg = {}
addWord = {}
randomData = {}
userUpdate = {}

def GetBackupID():
    sql = sqlite3.connect( "AutoBackUp.db" )
    cur = sql.cursor()
    cur.execute("Select * from Data")
    data = cur.fetchall()
    BackupID = data[0][0]
    if BackupID == '':
        BackupID = None
    cur.close()
    sql.close()
    return BackupID

def startbot(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    Send(update, "hihi, 我是{0}".format(GetConfig("name")))
    Send(update, "按 /help 取得說明")

def help(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    Send(update, GetConfig("helpText"))

def report(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
    userStatus.update({userID:"waitReport"})
    Reply(update, "輸入回報", force=True)

def getReport(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
    
    sql = sqlite3.connect( 'Report.db' )
    cur = sql.cursor()
    cur.execute("Select * from reports")
    allReport = cur.fetchall()
    for text in allReport:
        Send(update, text[0])

def list(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
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
        Reply(update, "目前沒有東西喔，請使用 /add 新增")
    else:
        userUpdate.update({userID: update})
        buttons = []
        for i in range(0, len(text), 3):
            buttons.append([InlineKeyboardButton(s, callback_data = "{0} {1}".format(s, userID)) for s in text[i:min(i+3, len(text))]])

        SendButton(update, "現在有：", buttons)

def setVal(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)

    text = ' '.join(update.message.text.split(' ')[1:])

    try:
        sql = sqlite3.connect( getenv("DATABASENAME") )
        sql.execute(text)
        sql.commit()
        sql.close()
        
        reloadDosParam()
        Send(update, "指令完成")
        
        if GetBackupID() != None:
            dump(update, bot, auto = True)
    except:
        Send(update, "指令似乎哪裡錯了")
    return

def add(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
    
    userStatus.update({userID:"waitName"})
    Reply(update, "輸入名字", force=True)

def getRandomReply(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
    text = update.message.text.split(' ')
    if len(text)==1:
        userStatus.update({userID:"waitDetail"})
        Reply(update, "輸入問題", force=True)
    else:
        randomReply(update, text[1])

def randomList(update, bot, userid = None):
    if(isDos(update)): return
    # if(not IsCommandAllowed(update)): return
    if userid == None:
        userid = getUserID(update)
        roomid = getRoomID(update)
    else:
        roomid = randomData[userid][2]
        del randomData[userid]

    sql = sqlite3.connect( getenv("DATABASENAME") )
    cur = sql.cursor()
    
    cur.execute("Select Name from Data")

    NameList = cur.fetchall()

    if(len(NameList)<1):
        Send(update, '目前沒有資料，請使用 /add 來新增')
    else:
        targetNum = random.randint(0, len(NameList)-1)
        Name = NameList[targetNum][0]
        print("Select * from Data where Name = '{0}'".format(Name))
        cur.execute("Select Image, Word from Data where Name = '{0}'".format(Name))
        DataList = cur.fetchall()
        # Send(update, Name)
        messages = []
        
        buttons = []
        buttons.append([InlineKeyboardButton(s[0], callback_data = "{0} {1}".format(s[1], userid)) for s in [ ("換一個", "random"), ("就這個了", "endRandom") ]])

        messages.append(Send(update, Name, chat_id = roomid))
        messages.append(SendResult(update, DataList, reply_markup = InlineKeyboardMarkup(buttons), chat_id = roomid))
        messages.append(roomid)
        print(messages)
        

        randomData.update({userid:messages})

    cur.close()
    sql.close()


def randomReply(update, text):
    userID = getUserID(update)
    print(text)
    if '?' in text and ':' in '?'.join(text.split('?')[1:]):

        answers = '?'.join(text.split('?')[1:]).split(':')
        retIndex = random.randint(0, len(answers)-1)
        Reply(update, answers[retIndex])

    else:
        againRange = float(GetConfig('askAgainRange'))
        probability = random.random()
        successful = random.random()-probability

        if(successful<-againRange):
            Reply(update, "Yes")
        elif (successful>againRange):
            Reply(update, "No")
        else:
            userStatus.update({userID:"waitDetail"})
            Reply(update, "Ask me again", True)
            return
            
    if userID in userStatus:
        del userStatus[userID]

def finding(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
    text = update.message.text.split(' ')
    if(len(text)==1):
        userStatus.update({userID:"findName"})
        Reply(update, "輸入名字", force=True)
        return
    text = ' '.join(text[1:])
    findBody(update, text)

def findBody(update, text):
    userID = getUserID(update)
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
    SendButton(update, "猜你想查：", buttons)

def delete(update, bot):
    if(isDos(update)): 
        print(dos_defence)
        return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)

    userStatus.update({userID:"delName"})
    Reply(update, "輸入名字", force=True)

def callback(update, bot):
    replyText = update.callback_query.data.split(" ")
    try:
        userID = int(replyText[-1])
    except:
        buttonTimeOUt(update)
        return

    if replyText[0] == 'random' and userID in randomData:
        if randomData[userID][2] != update.callback_query.message.chat_id:
            buttonTimeOUt(update)
            return

        updater.bot.delete_message(chat_id = randomData[userID][0].chat_id, message_id = randomData[userID][0].message_id) # delete text
        for i in randomData[userID][1]: # delete photo
            updater.bot.delete_message(chat_id = i.chat_id, message_id = i.message_id)

        randomList(update, bot, userID)
        return
    elif replyText[0] == 'endRandom' and userID in randomData:
        if randomData[userID][2] != update.callback_query.message.chat_id:
            buttonTimeOUt(update)
            return
        randomData[userID][1][-1].edit_reply_markup(None)
        return

    if userID not in userUpdate:
        buttonTimeOUt(update)
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
        if result[0]!='':
            SendPhotoWithCaption(update2, result[1], result[0])
        else:
            SendPhoto(update2, result[0])
            Send(update2, result[1])
    if(len(allPhoto)==0):
        Send(update2, "查無結果")
        
    # SendResult(update, allPhoto)

def buttonTimeOUt(update):
    if update.callback_query.message.text == None:
        update.callback_query.edit_message_caption('按鈕已過期')
    else:
        update.callback_query.edit_message_text('按鈕已過期')

def cancel(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
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

    Reply(update, "指令取消。")

def getText(update, bot):
    if update.message == None:
        try:
            update.edited_message.reply_text("偷改，抓")
        except:
            pass
        return
    if(isDos(update)): return
    userID = getUserID(update)
    text = update.message.text
    print(text)

    if userID in userStatus:
        state = userStatus[userID]
        print(state)
        if state == 'waitName':
            addName.update({userID:text})
            Reply(update, '名字為：{0}\n請輸入內文或傳送未壓縮照片'.format(text), True)
            userStatus.update({userID:"waitContent"})
            

        elif state == 'waitContent':
            addWord.update({userID:text})
            print(addWord[userID])
            if(userID not in addImg):
                Reply(update, '內文新增完成, \n可以重打內文或 /end 完成新增', True)
            else:
                Reply(update, '內文新增完成,\n 請傳送未壓縮照片或 /end 完成新增', True)

        elif state == 'delName':
            sql = sqlite3.connect( getenv("DATABASENAME") ) 
            cur = sql.cursor()
            cur.execute("select * from Data where Name = '{}'".format(text))
            data = cur.fetchall()
            if len(data)==0:
                Send(update, "查無資料")
            else:
                cur.execute("delete from Data where Name = '{0}' and Image = '{1}' and Word = '{2}'".format(text, data[0][1], data[0][2]))
                sql.commit()
                Send(update, "刪除最舊一筆內容")
            cur.close()
            sql.close()
            del userStatus[userID]
            
            if GetBackupID() != None:
                dump(update, bot, auto = True)

        elif state == 'findName':
            findBody(update, text)

            del userStatus[userID]
        elif state == 'waitDetail':
            randomReply(update, text)

        elif state == 'waitReport':
            sql = sqlite3.connect( 'Report.db' ) 
            cur = sql.cursor()
            cur.execute("Insert into reports values('{0}')".format(text))
            sql.commit()
            cur.close()
            sql.close()
            Reply(update, "完成回報")
            if userID in userStatus:
                del userStatus[userID]

        elif state == 'waitLoad':
            try:
                tmpdata = text.split(',')
                data = []
                i = 0
                while i < len(tmpdata):
                    if tmpdata[i][0:2] =='\n\n':
                        break
                    data.append(tmpdata[i: i+3])
                    i += 3

                config = []
                while i < len(tmpdata):
                    config.append(tmpdata[i: i+2])
                    i += 2

                            
                for i in range(len(data)):
                    for j in range(len(data[i])):
                        while len(data[i][j])!=0 and data[i][j][0] == '\n':
                            data[i][j] = data[i][j][1:]
                            
                for i in range(len(config)):
                    for j in range(len(config[i])):
                        while len(config[i][j])!=0 and config[i][j][0] == '\n':
                            config[i][j] = config[i][j][1:]
                config = config[:-1]

                for i in data:
                    if len(i)!=3:
                        raise exception
                for i in config:
                    if len(i)!=2:
                        raise exception

                sql = sqlite3.connect(getenv("DATABASENAME"))
                sql.execute('delete from Data')
                sql.commit()
                sql.execute('delete from Config')
                sql.commit()
                for i in data:
                    sql.execute("insert into Data values('{0}', '{1}', '{2}')".format(i[0], i[1], i[2]))
                    sql.commit()
                    
                for i in config:
                    sql.execute("insert into Config values('{0}', '{1}')".format(i[0], i[1]))
                    sql.commit()
                sql.close()

                Send(update, '還原完成')
            except:
                Send(update, '未能成功還原，也許是哪裡出問題了')


def getPhoto(update, bot):
    if(isDos(update)): return
    userID = getUserID(update)
    
    if(userStatus[userID]=='waitContent'):
        Reply(update, '不要壓縮，傳檔案', True)

def getFile(update, bot):
    if(isDos(update)): return
    userID = getUserID(update)

    if(userStatus[userID]=='waitContent'):
        Send(update, '上傳中...')
        path = uploadAndGetPhoto(update.message.document.file_id)
        if userID in addImg:
            addImg[userID].append(path)
        else:
            addImg[userID] = [path]

        Reply(update, '照片上傳成功。\n可以輸入描述或使用 /end 結束', True)
    
def endAdd(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)
    if(userStatus[userID]=='waitContent'):
        sql = sqlite3.connect( getenv("DATABASENAME") ) 
        cur = sql.cursor()
        if(userID not in addImg):
            addImg[userID] = []
        if(userID not in addWord):
            addWord[userID] = ''
        if addImg[userID] == [] and addWord[userID] == '':
            Reply(update, '得先輸入內文或傳送未壓縮圖片', True)
            return
        
        if addWord[userID] != '':
            command = "insert into Data values('{0}', '{1}', '{2}')".format(addName[userID], '', addWord[userID])
            cur.execute(command)
        for i in addImg[userID]:
            command = "insert into Data values('{0}', '{1}', '{2}')".format(addName[userID], i,'')
            cur.execute(command)

        sql.commit()

        cur.close()
        sql.close()

        Send(update, "新增 {0}".format(addName[userID]))

        del userStatus[userID]
        del addName[userID]
        del addImg[userID]
        del addWord[userID]
    
    if GetBackupID() != None:
        dump(update, bot, auto = True)

def dump(update, bot, auto = False):
    if(isDos(update)): return
    if(not auto and not IsCommandAllowed(update)): return

    if(auto):
        userID = GetBackupID()
        Send(update, "自動備份檔：", chat_id=userID)
    else:
        userID = getUserID(update)
    
    sql = sqlite3.connect( getenv("DATABASENAME") ) 
    cur = sql.cursor()
    cur.execute('select * from Data')
    data = cur.fetchall()
    ret = ''
    for i in data:
        for j in i:
            ret += j + ','
        ret += '\n'
    cur.close()

    cur = sql.cursor()
    cur.execute('select * from Config')
    data = cur.fetchall()
    ret += '\n'
    for i in data:
        for j in i:
            ret += j + ','
        ret += '\n'
    cur.close()
    sql.close()

    Send(update, ret, chat_id=userID)
    Send(update, '請妥善保管上則訊息\n使用 /load 可以還原備份檔', chat_id=userID)

def load(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userID = getUserID(update)

    userStatus.update({userID:"waitLoad"})
    Reply(update, '請輸入還原訊息', True)

def auto_backup(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return

    text = update.message.text.split(' ')
    
    if len(text) > 1 and (text[1] == '0' or text[1].lower()=='null'):
        sql = sqlite3.connect( "AutoBackUp.db" ) 
        cur = sql.cursor()
        cur.execute("Update Data set TargetID = NULL")
        sql.commit()
        sql.close()
        Send(update, "已停止自動備份")
    else:
        roomID = getRoomID(update)
        sql = sqlite3.connect( "AutoBackUp.db" ) 
        cur = sql.cursor()
        cur.execute("Update Data set TargetID = '{}'".format(roomID))
        sql.commit()
        sql.close()
        Send(update, "將會在此聊天室自動備份")

def promote(update, bot):
    print('promoting')
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userIDUp = str(getUserID(update))
    userIDDown = update.message.text.split(' ')
    if len(userIDDown)<2:
        Reply(update, '未輸入對象')
        return
    userIDDown = userIDDown[1]

    if(Compare(userIDUp, userIDDown)):
        increase(update, userIDDown)
    else:
        Reply(update, '權限不足')

def demote(update, bot):
    if(isDos(update)): return
    if(not IsCommandAllowed(update)): return
    userIDUp = str(getUserID(update))
    userIDDown = update.message.text.split(' ')
    if len(userIDDown)<2:
        Reply(update, '未輸入對象')
        return
    userIDDown = userIDDown[1]

    if(Compare(userIDUp, userIDDown)):
        increase(update, userIDDown, -1)
    else:
        Reply(update, '權限不足')

        
def increase(update, userID, num = 1):
    sql = sqlite3.connect( 'Permission.db' )
    cur = sql.cursor()
    cur.execute("Select level from Data where key = '{}'".format(userID))
    data = cur.fetchall()

    goalLevel = 1
    if len(data)==1:
        goalLevel = data[0][0] + num
        if goalLevel<1:
            goalLevel = 1
        cur.execute("Update Data set level = {} where key = '{}'".format(goalLevel, userID))
    else:
        goalLevel = goalLevel + num
        if goalLevel<1:
            goalLevel = 1
        cur.execute("Insert into Data values('{}', {}, 'P')".format(userID, goalLevel))

    sql.commit()
    cur.close()
    sql.close()
    Send(update, '現在 {} 階級為 {}'.format(userID, goalLevel))
