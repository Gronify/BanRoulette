from random import randrange
import telebot

bot = telebot.TeleBot("1197680720:AAEpdcTDvhLD9NpYsz20jZ1zJRdwQxxvO3o")
membersId = []
members = []
bannedOne = []
print("Bot is started!")


@bot.message_handler(commands=['ihaveballs'])
def add(message):
    if str(message.from_user.id) in membersId:
        bot.reply_to(message, message.from_user.first_name + ",ты уже участвуешь в бан рулетке! НЕЗАЕБУЙ!")
    else:
        bot.reply_to(message, message.from_user.first_name + " теперь участвует в бан рулетке!")
        membersId.append(message.from_user.id)
        members.append(str(message.from_user.first_name))
        print(str(message.from_user.id) + " " + str(message.from_user.username) + " " +  str(message.from_user.first_name))


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


@bot.message_handler(commands=["ban"])
def baned(message):
    try: 
        bot.restrict_chat_member(chat_id=message.chat.id, user_id=382353620, until_date=30, can_send_messages=False)
    except:
        print(len(membersId))
        print(membersId)
        if len(membersId) != 0:
            bot.send_message(chat_id=message.chat.id, text="Banned")
            bannedOne.append(membersId[randrange(len(membersId))])
            print(f"we {bannedOne[0]} is banned")
        else:
            bot.send_message(message.chat.id, text="no participants in this shit")
        

@bot.message_handler(content_types=['sticker' ,'text' ,'audio', 'voice', 'video', 'animation', 'videoNote'])
def booling(message):
    if len(bannedOne) != 0:
        if int(bannedOne[0]) == message.from_user.id:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

bot.polling()
