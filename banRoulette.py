from random import randrange, randint
import time
import sqlite3
import telebot


bot = telebot.TeleBot("")

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
@bot.message_handler(commands=['ban'])
def baned(message):
    if not isDay:
        if not isBan:
            cursor.execute("SELECT userFirstName FROM bannedUsers WHERE userId=?", (str(message.from_user.id),))
            check = cursor.fetchall()
            if len(check)==0:
                err = "Пользователь " + str(message.from_user.first_name) + " не был зарегестрирован в игре"
                bot.send_message(message.chat.id, err)
            else:
                getId = "SELECT userId FROM bannedUsers"
                getName = "SELECT userFirstName FROM bannedUsers WHERE userId=?"
                getPoints = "SELECT points FROM bannedUsers WHERE userId=?"
                getTimes = "SELECT timesBanned FROM bannedUsers WHERE userId=?"
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

                    cursor.execute(getTimes, ([bannedOne]))
                    times = [row for row in cursor.fetchone()]
                    newT = times[0] + 1
                    times.append(newT)
                    cursor.execute(getPoints, ([bannedOne]))
                    points = [row[0] for row in cursor.fetchall()]
                    newP = points[0] + randint(-100, 150)
                    data = [(times[1], newP, bannedOne)]
                    sql = "UPDATE bannedUsers SET timesBanned=?, points=? WHERE userId=?"
                    cursor.executemany(sql, data)
                    conn.commit()

                    randomTime = randint(100, 1800) # банит от 100 секунд до 30 минут(юзать на проде)
                    banInfo = "Пользователь " + str(user[0]) + " был забанен на " + str(randomTime) + " секунд"
                    bot.send_message(message.chat.id, text=banInfo)
                    try:
                        day = message.date + randomTime
                        bot.restrict_chat_member(message.chat.id, bannedOne, until_date=day, can_send_messages=False)
                        bannedOne = None
                    except:
                        print("Пользователь является админом чата")

                    banTimer(randomTime)
                    dayTimer()
                else:
                    bot.send_message(message.chat.id, text="Ни один участник не был зарегестрирован")
        else:
            now = "На данный момент пользователь " + str(banName) + " уже в бане"
            bot.send_message(message.chat.id, text=now)
    else:
        bot.send_message(message.chat.id, text="Сегодня уже был кто-то забанен")


# Shows staistics
@bot.message_handler(commands=['stat'])
def stat(message):
    banned = "SELECT timesBanned FROM bannedUsers"
    users = "SELECT userFirstName FROM bannedUsers"
    cursor.execute(banned)
    times = [row[0] for row in cursor.fetchall()]
    cursor.execute(users)
    us = [row[0] for row in cursor.fetchall()]
    staistics = "Статистика банов: \n"
    for i in range(len(us)):
        staistics = staistics + str(us[i]) + " - " +str(times[i]) + "\n"

    bot.send_message(message.chat.id, text=staistics)


# Unreg users
@bot.message_handler(commands=['unregister'])
def unregister(message):
    cursor.execute("SELECT userFirstName FROM bannedUsers WHERE userId=?", (str(message.from_user.id),))
    data = cursor.fetchall()
    if len(data)==0:
        err = "Пользователь " + str(message.from_user.first_name) + " не был зарегестрирован в игре"
        bot.send_message(message.chat.id, err)
    else:
        sql = "DELETE FROM bannedUsers WHERE userId=?"
        cursor.execute(sql, [(message.from_user.id)])
        conn.commit()
        m = "Пользователь " + str(message.from_user.first_name) + " вышел из игры"
        bot.send_message(message.chat.id, text=m)


# drop timesBanned
@bot.message_handler(commands=['drop'])
def drop(message):
    if message.from_user.id == 382353620 or message.from_user.id == 973532944:
        sql = "UPDATE bannedUsers SET timesBanned=0"
        cursor.execute(sql)
        conn.commit()
        bot.send_message(message.chat.id, text="Статистика была сброшена")
    else:
        bot.send_message(message.chat.id, text="Вы не можете использовать эту комманду")


# delete
@bot.message_handler(content_types=['audio', 'location', 'contact', 'sticker' ,'text' , 'voice', 'video', 'document', 'video_note'])
def booling(message):
    if bannedOne != None:
        if bannedOne == message.from_user.id:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# timer for ban(now last only for 10 sec, later I will add random)
def banTimer(randomTime):
    global banName, bannedOne, isBan
    #t = randomTime # прод
    t = 10 # банит на 10 сек, сделано для разработки
    isBan = True
    while t > 0:
        t -= 1
        print(t)
        time.sleep(1)
    banName = "никто"
    bannedOne = None
    isBan = False


# 24h timer(now last only for 10 sec)
def dayTimer():
    global isDay
    #t = 7200 # банить можно только раз в 2 часа использовать это для прода
    t = 5 # банить можно раз в 5 секунд, для разработки сделано
    isDay = True
    while t > 0:
        t -= 1
        time.sleep(1)
    isDay = False


createDb()
bot.polling()
