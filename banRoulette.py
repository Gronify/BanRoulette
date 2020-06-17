from random import randrange
import sqlite3
import telebot

bot = telebot.TeleBot("1197680720:AAEpdcTDvhLD9NpYsz20jZ1zJRdwQxxvO3o")

membersId = []
members = []
bannedOne = []

# TODO Исправить ошибку, которая появляется при комманде /nowbanned
#      Постоянно висит значение "никто"
banName = "никто"

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
                      points        integer,
                      multiply      REAL
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
        data = [(message.from_user.id,message.from_user.first_name,0,100,2.0)]
        cursor.executemany("INSERT INTO bannedUsers(userId, userFirstName, timesBanned, points, multiply) VALUES (?,?,?,?,?)", data)
        conn.commit()


# listing members
@bot.message_handler(commands=['list'])
def list(message):
    listOfMembers = "Список участвующих: \n"
    sql = "SELECT userFirstName FROM bannedUsers"
    cursor.execute(sql)
    # Именно так надо брать данные с бд, чтоб запятых не было
    members = [row[0] for row in cursor.fetchall()]
    for i in range(len(members)):
        listOfMembers = listOfMembers + str(i+1) + ". " + str(members[i]) + "\n"
    bot.send_message(message.chat.id, listOfMembers)


# Show who is banned
@bot.message_handler(commands=['nowbanned'])
def nowbanned(message):
    if len(bannedOne) != 0:
        now = "Пользователь " + str(banName) + " сейчас в бане"
        bot.send_message(message.chat.id, text=now)
    else:
        bot.send_message(message.chat.id, text="На данный момент никто не забанен")

# Ban
@bot.message_handler(commands=["ban"])
def baned(message):
    try: 
        bot.restrict_chat_member(chat_id=message.chat.id, user_id=382353620, until_date=30, can_send_messages=False)
    except:
        getId = "SELECT userId FROM bannedUsers"
        getName = "SELECT userFirstName FROM bannedUsers WHERE userId=?"
        cursor.execute(getId)
        membersId = [row[0] for row in cursor.fetchall()]
        if len(membersId) != 0:
            randomId = randrange(len(membersId))
            bannedOne.append(membersId[randomId])
            cursor.execute(getName, ([bannedOne[0]]))
            user = [row[0] for row in cursor.fetchone()]
            print(user)
            banInfo = "Пользователь " + str(user) + " был забанен"
            bot.send_message(message.chat.id, text=banInfo)
            print(f"user {bannedOne[0]} was banned")
        else:
            bot.send_message(message.chat.id, text="Ни один участник не был зарегестрирован")
        

# delete
@bot.message_handler(content_types=['sticker' ,'text' ,'audio', 'voice', 'video', 'animation', 'videoNote'])
def booling(message):
    if len(bannedOne) != 0:
        if bannedOne[0] == message.from_user.id:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


createDb()
bot.polling()
