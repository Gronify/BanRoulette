from random import randrange, randint
import time
import sqlite3
import telebot


bot = telebot.TeleBot("")

banT = 0
dayT = 0

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
                      chatId        INTEGER,
                      userFirstName STRING,
                      timesBanned   INTEGER,
                      points        integer
                      );
                   """)
    conn.commit()


# adding participants
@bot.message_handler(commands=['ihaveballs'])
def iHaveBalls(message):
    sql = "SELECT userId FROM bannedUsers WHERE chatId=?"
    cursor.execute(sql, ([message.chat.id]))
    membersId = [row[0] for row in cursor.fetchall()]

    if message.from_user.id in membersId:
        bot.reply_to(message, message.from_user.first_name + ",ты уже участвуешь в бан рулетке! НЕЗАЕБУЙ!")
    else:
        bot.reply_to(message, message.from_user.first_name + " теперь участвует в бан рулетке!")
        data = [(message.from_user.id,message.chat.id,message.from_user.first_name,0,1000)]
        cursor.executemany("INSERT INTO bannedUsers(userId, chatId, userFirstName, timesBanned, points) VALUES (?,?,?,?,?)", data)
        conn.commit()


# listing members
@bot.message_handler(commands=['list'])
def list(message):
    listOfMembers = "Список участвующих: \n"
    sql = "SELECT userFirstName FROM bannedUsers WHERE chatId=?"
    cursor.execute(sql, ([message.chat.id]))
    members = [row[0] for row in cursor.fetchall()]

    for i in range(len(members)):
        listOfMembers = listOfMembers + str(i+1) + ". " + str(members[i]) + "\n"

    bot.send_message(message.chat.id, listOfMembers)


# Show who is banned
@bot.message_handler(commands=['nowbanned'])
def nowbanned(message):
    global banT
    if bannedOne != None and banT != 0:
        now = "Пользователь " + str(banName) + " сейчас в бане\nКонец бана через " + str(banT) + " секунд"
        bot.send_message(message.chat.id, text=now)
    else:
        bot.send_message(message.chat.id, text="На данный момент никто не забанен")


# Ban
@bot.message_handler(commands=['ban'])
def baned(message):
    if not isDay:
        if not isBan:
            cursor.execute("SELECT userFirstName FROM bannedUsers WHERE userId=? AND chatId=?", (message.from_user.id,message.chat.id))
            check = cursor.fetchall()
            if len(check)==0:
                err = "Пользователь " + str(message.from_user.first_name) + " не был зарегестрирован в игре"
                bot.send_message(message.chat.id, err)
            else:
                getId = "SELECT userId FROM bannedUsers WHERE chatId=?"
                getName = "SELECT userFirstName FROM bannedUsers WHERE userId=? AND chatId=?"
                getPoints = "SELECT points FROM bannedUsers WHERE userId=? AND chatId=?"
                getTimes = "SELECT timesBanned FROM bannedUsers WHERE userId=? AND chatId=?"
                cursor.execute(getId, ([message.chat.id]))
                membersId = [row[0] for row in cursor.fetchall()]

                if len(membersId) != 0:
                    userIntervals = []
                    pastPoints = 0

                    for id in membersId:
                        cursor.execute(getPoints, (id,message.chat.id))
                        points = [row[0] for row in cursor.fetchall()]
                        userIntervals.append([id,pastPoints, pastPoints + int(points[0])])
                        print(userIntervals)
                        pastPoints += int(points[0])
                    randomNumber = randint(0, pastPoints)

                    for i in range(len(userIntervals)):
                        if int(userIntervals[i][1]) <= randomNumber and randomNumber < int(userIntervals[i][2]):
                            global bannedOne
                            bannedOne = int(userIntervals[i][0])

                    cursor.execute(getName, (bannedOne, message.chat.id))
                    user = [row for row in cursor.fetchone()]
                    global banName
                    banName = user[0]

                    cursor.execute(getTimes, (bannedOne, message.chat.id))
                    times = [row for row in cursor.fetchone()]
                    newT = times[0] + 1
                    times.append(newT)
                    cursor.execute(getPoints, (bannedOne, message.chat.id))
                    points = [row[0] for row in cursor.fetchall()]
                    newP = points[0] + randint(-100, 150)
                    data = [(times[1], newP, bannedOne, message.chat.id)]
                    sql = "UPDATE bannedUsers SET timesBanned=?, points=? WHERE userId=? AND chatId=?"
                    cursor.executemany(sql, data)
                    conn.commit()

                    randomTime = randint(100, 1200) # ban from 100 sec to 20 minutes 
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
        global dayT
        m = "Сегодня уже был кто-то забанен\nСледующий бан можно сделать через " + str(dayT)+ " секунд"
        bot.send_message(message.chat.id, text=m)


# Shows staistics
@bot.message_handler(commands=['stat'])
def stat(message):
    banned = "SELECT timesBanned FROM bannedUsers WHERE chatId=?"
    users = "SELECT userFirstName FROM bannedUsers WHERE chatId=?"
    p = "SELECT points FROM bannedUsers WHERE chatId=?"

    cursor.execute(banned, ([message.chat.id]))
    times = [row[0] for row in cursor.fetchall()]
    cursor.execute(users, ([message.chat.id]))
    us = [row[0] for row in cursor.fetchall()]
    cursor.execute(p, ([message.chat.id]))
    points = [row[0] for row in cursor.fetchall()]

    staistics = "Статистика банов(пользователь - баны - очки): \n"
    for i in range(len(us)):
        staistics = staistics + str(i+1) + ". " + str(us[i]) + " - " + str(times[i]) + " - " +  str(points[i]) + "\n"

    bot.send_message(message.chat.id, text=staistics)


# Unreg users
@bot.message_handler(commands=['unregister'])
def unregister(message):
    cursor.execute("SELECT userFirstName FROM bannedUsers WHERE userId=? AND chatId=?", (message.from_user.id,message.chat.id))
    data = cursor.fetchall()
    if len(data)==0:
        err = "Пользователь " + str(message.from_user.first_name) + " не был зарегестрирован в игре"
        bot.send_message(message.chat.id, err)
    else:
        sql = "DELETE FROM bannedUsers WHERE userId=? AND chatId=?"
        cursor.execute(sql, (message.from_user.id, message.chat.id))
        conn.commit()
        m = "Пользователь " + str(message.from_user.first_name) + " вышел из игры"
        bot.send_message(message.chat.id, text=m)


# drop timesBanned
@bot.message_handler(commands=['drop'])
def drop(message):
    if message.from_user.id == "id" or message.from_user.id == "id":
        sql = "UPDATE bannedUsers SET timesBanned=0, points=1000 WHERE chatId=?"
        cursor.execute(sql, ([message.chat.id]))
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
    global banName, bannedOne, isBan, banT
    banT = randomTime
    #banT = 10 # ban for 10 sec(for development)
    isBan = True
    while banT > 0:
        banT -= 1
        time.sleep(1)
    banName = "никто"
    bannedOne = None
    isBan = False


# 30 minutes timer
def dayTimer():
    global isDay, dayT
    dayT = 1800 # you can make 1 ban per 30 minutes 
    #dayT = 5 # 1 ban per 5 sec(for development)
    isDay = True
    while dayT > 0:
        dayT -= 1
        time.sleep(1)
    isDay = False


createDb()
bot.polling()
