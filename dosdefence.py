# from functions.variable import dos_defence, penalty, dos_maximum
from function import GetConfig
from dotenv import load_dotenv

load_dotenv()

dos_defence = {}
penalty = int(GetConfig('penalty'))
dos_maximum = int(GetConfig('dos_maximum'))

def reloadDosParam():
    penalty = int(GetConfig('penalty'))
    dos_maximum = int(GetConfig('dos_maximum'))

def isDos(update):
    chat_id = str(update.message.from_user.id)
    date = update.message.date

    if chat_id not in dos_defence:
        dos_defence[chat_id] = [1, date]
        return False
        
    count = dos_defence[chat_id][0]
    lasttime = dos_defence[chat_id][1]
    during = (date-lasttime).total_seconds()

    if count==-1:
        if during>penalty:
            dos_defence.update({chat_id : [1, date]})
            return False
        else:
            dos_defence.update({chat_id : [-1, date]})
            return True
    elif during>60:
        dos_defence.update({chat_id : [1, date]})
        return False
    elif count<dos_maximum:
        dos_defence.update({chat_id : [count+1, date]})
        return False
    else:
        dos_defence.update({chat_id : [-1, date]})
        return True