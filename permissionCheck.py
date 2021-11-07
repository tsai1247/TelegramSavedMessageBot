from os import getenv
from function import getUserID
import sqlite3

def GetPermission(keyword):
    if keyword in getenv("DEVELOPER_ID").split(','):
        return 9

    sql = sqlite3.connect( 'Permission.db' )
    cur = sql.cursor()
    
    cur.execute("Select level from Data where key = '{}'".format(keyword))

    data = cur.fetchall()
    
    cur.close()
    sql.close()

    if len(data)==0:
        try:
            return int(getenv("DEFAULTLEVEL"))
        except:
            return 1
    else:
        return data[0][0]


def IsCommandAllowed(update, command = ''):
    if command == '':
        command = update.message.text
    command = command.split(' ')[0].split('@')[0].split('/')[1]

    userId = str(getUserID(update))

    if GetPermission(userId)>=GetPermission(command):
        return True
    else:
        return False

def Compare(useridUp, useridDown, diff = 2):
    if ( GetPermission(useridUp) - GetPermission(useridDown) ) >= diff:
        return True
    else:
        return False
