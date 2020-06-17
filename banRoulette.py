
import sqlite3
import telebot

bot = telebot.TeleBot("")
membersId = []
members = []
print("Bot is started!")
conn = sqlite3.connect("database.db", check_same_thread=False) # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

'''# Создание таблицы
cursor.execute("""CREATE TABLE bannedUsers (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    userId        INTEGER,
                    userName      STRING,
                    userFirstName STRING,
                    timesBanned   INTEGER,
                    points        INTEGER,
                    multiply      REAL
                    );
                """)
conn.commit()'''
@bot.message_handler(commands=['ihaveballs'])
def add(message):
    if str(message.from_user.id) in membersId:
        bot.reply_to(message, message.from_user.first_name + ",ты уже участвуешь в бан рулетке! НЕЗАЕБУЙ!")
    else:
        bot.reply_to(message, message.from_user.first_name + " теперь участвует в бан рулетке!")
        membersId.append(str(message.from_user.id))
        members.append(str(message.from_user.first_name))
        print(str(message.from_user.id) + " " + str(message.from_user.username) + " " +  str(message.from_user.first_name))
        if 1==1:
            data = [(message.from_user.id,message.from_user.username,message.from_user.first_name,0,100,2.0)]
            cursor.executemany("INSERT INTO bannedUsers(userId, userName, userFirstName, timesBanned, points, multiply) VALUES (?,?,?,?,?,?)", data)
            conn.commit()




@bot.message_handler(commands=['list'])
def list(message):
    listOfMembers = "Список участвующих: \n"
    for i in range(len(members)):
        listOfMembers = listOfMembers + str(i+1) + ". " +members[i] + "\n"
    bot.send_message(message.chat.id, listOfMembers)
    print(membersId)

@bot.message_handler(commands=['nowbanned'])
def nowbanned(message):

    print(membersId)


bot.polling()
