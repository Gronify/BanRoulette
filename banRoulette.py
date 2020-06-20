from random import randrange, randint
import time
import sqlite3
import telebot

bot = telebot.TeleBot("1197680720:AAEpdcTDvhLD9NpYsz20jZ1zJRdwQxxvO3o")

membersId = []
members = []

bannedOne = None
banName = "никто"

isBan = False
isDay = False

print("Bot is started!")

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Create Table
def createDb():
    cursor.execute("""CREATE TABLE IF NOT EXISTS bannedUsers (
                      id            INTEGER PRIMARY KEY AUTOINCREMENT,
                      userId        INTEGER,
                      userFirstName STRING,
                      timesBanned   INTEGER,
                      points        integer
                      );
                   """)
    conn.commit()


# adding participants
@bot.message_handler(commands=['ihaveballs'])
def add(message):
    sql = "SELECT userId FROM bannedUsers"
    cursor.execute(sql)
    membersId = [row[0] for row in cursor.fetchall()]

    if message.from_user.id in membersId:
        bot.reply_to(message, message.from_user.first_name + ",ты уже участвуешь в бан рулетке! НЕЗАЕБУЙ!")
    else:
        bot.reply_to(message, message.from_user.first_name + " теперь участвует в бан рулетке!")
        data = [(message.from_user.id,message.from_user.first_name,0,1000)]
        cursor.executemany("INSERT INTO bannedUsers(userId, userFirstName, timesBanned, points) VALUES (?,?,?,?)", data)
        conn.commit()


# listing members
@bot.message_handler(commands=['list'])
def list(message):
    listOfMembers = "Список участвующих: \n"
    sql = "SELECT userFirstName FROM bannedUsers"
    cursor.execute(sql)
    members = [row[0] for row in cursor.fetchall()]
    
    for i in range(len(members)):
        listOfMembers = listOfMembers + str(i+1) + ". " + str(members[i]) + "\n"

    bot.send_message(message.chat.id, listOfMembers)


# Show who is banned
@bot.message_handler(commands=['nowbanned'])
def nowbanned(message):
    if bannedOne != None:
        now = "Пользователь " + str(banName) + " сейчас в бане"
        bot.send_message(message.chat.id, text=now)
    else:
        bot.send_message(message.chat.id, text="На данный момент никто не забанен")


# Ban
@bot.message_handler(commands=["ban"])
def baned(message):
    if not isDay:
        if not isBan:
            try:
                bot.restrict_chat_member(chat_id=message.chat.id, user_id=382353620, until_date=30, can_send_messages=False)
            except:
                getId = "SELECT userId FROM bannedUsers"
                getName = "SELECT userFirstName FROM bannedUsers WHERE userId=?"
                getPoints = "SELECT points FROM bannedUsers WHERE userId=?"
                cursor.execute(getId)
                membersId = [row[0] for row in cursor.fetchall()]

                if len(membersId) != 0:
                    userIntervals = []
                    pastPoints = 0

                    for id in membersId:
                        cursor.execute(getPoints, ([id]))
                        points = [row[0] for row in cursor.fetchall()]
                        userIntervals.append([id,pastPoints, pastPoints + int(points[0])])
                        print(userIntervals)
                        pastPoints += int(points[0])
                    randomNumber = randint(0, pastPoints)

                    for i in range(len(userIntervals)):
                        if int(userIntervals[i][1]) <= randomNumber and randomNumber < int(userIntervals[i][2]):
                            global bannedOne
                            bannedOne = int(userIntervals[i][0])

                    cursor.execute(getName, ([bannedOne]))
                    user = [row for row in cursor.fetchone()]
                    global banName
                    banName = user[0]
                    banInfo = "Пользователь " + str(user[0]) + " был забанен"
                    bot.send_message(message.chat.id, text=banInfo)
                else:
                    bot.send_message(message.chat.id, text="Ни один участник не был зарегестрирован")
                banTimer()
                dayTimer()
        else:
            now = "На данный момент пользователь " + str(banName) + " уже в бане"
            bot.send_message(message.chat.id, text=now)
    else:
        bot.send_message(message.chat.id, text="Сегодня уже был кто-то забанен")

# delete
@bot.message_handler(content_types=['sticker' ,'text' ,'audio', 'voice', 'video', 'animation', 'videoNote'])
def booling(message):
    if bannedOne != None:
        if bannedOne == message.from_user.id:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# timer for ban(now last only for 10 sec, later I will add random)
def banTimer():
    global banName, bannedOne, isBan
    t = 10
    isBan = True
    while t > 0:
        t -= 1
        print(t) 
        time.sleep(1)
    banName = "никто"
    bannedOne = None
    isBan = False
    

# 24h tomer(now last only for 10 sec)
def dayTimer():
    global isDay
    t = 5
    isDay = True
    while t > 0:
        t -= 1
        time.sleep(1)
    isDay = False


createDb()
bot.polling()
