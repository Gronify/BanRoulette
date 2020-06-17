
import sqlite3
import telebot

bot = telebot.TeleBot("")
membersId = []
members = []
print("Bot is started!")

@bot.message_handler(commands=['ihaveballs'])
def add(message):
	if str(message.from_user.id) in membersId:
		bot.reply_to(message, message.from_user.first_name + ",ты уже участвуешь в бан рулетке! НЕЗАЕБУЙ!")
	else:
		bot.reply_to(message, message.from_user.first_name + " теперь участвует в бан рулетке!")
		membersId.append(str(message.from_user.id))
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


bot.polling()
