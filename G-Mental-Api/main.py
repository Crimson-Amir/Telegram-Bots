import telebot
import requests

bot = telebot.TeleBot("6264249600:AAE-VoCCNert1pQ1UEfRbd6nJUMpY_D9-SI", parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "yo\n/send_music to send a music.\n/say to send the words you want\n/find_firend to find a friend :)\n\nurl: https://gmental.pythonanywhere.com/")


@bot.message_handler(commands=['find_firend'])
def find_firend(message):
    bot.reply_to(message, "Tell about yourself and someone who looks like you send you a message\nYour username and name will be placed on the site.\nCurrently, there is no option to delete the post,\n although you can always message me to delete it")
    bot.register_next_step_handler(message, get_firend)

def get_firend(message):
    try:
        body = message.text
        user_name = ""
        name = message.from_user.first_name
        if message.from_user.username:
                user_name = message.from_user.username
        response = requests.post('https://gmental.pythonanywhere.com/send-firend', data={'username': user_name, 'name': name, 'body': body})
        bot.reply_to(message, f"({response}) - upload successfully. thanks <3")
    except Exception as e:
        print(e)
        bot.reply_to(message, f"oh, something went wrong!\n {e}")

@bot.message_handler(commands=['send_music', 'say'])
def first(message):
    text = "Nan"
    types = ""
    if message.text == "/send_music":
        text = "Send your music pls."
        types = 'music'
    else:
        text = "ok, send your topic title pls."
    bot.reply_to(message, text)
    bot.register_next_step_handler(message, get_first, types)


def get_first(message, types):

    try:
        text = "Nan"

        if types == "music":
            text = "Well, do you want to say something that will be displayed along with your music? (N if no)"
            music = message.audio
            file_info = bot.get_file(music.file_id)
            file_path = file_info.file_path
            end = bot.download_file(file_path)
        else:
            text = "ok, send your topic body pls."
            end = message.text

        bot.reply_to(message, text)
        bot.register_next_step_handler(message, get_text, end, types)
    except Exception as e:
        print(e)
        bot.reply_to(message, f"oh, something went wrong!\n {e}")

def get_text(message, end, types):
    try:
        say = message.text
        if say.lower() == "n":
            say = ""

        bot.reply_to(message, "Do you want your name And id to be displayed on the site? (Y, N)")
        bot.register_next_step_handler(message, send, end, say, types)
    except Exception as e:
        print(e)
        bot.reply_to(message, f"oh, somthing went wrong!\n {e}")


def send(message, end, say, types):
    try:
        user_say = message.text
        user_name = ""
        name = ""

        if user_say.lower() == "y":
            if message.from_user.username:
                user_name = message.from_user.username
            name = message.from_user.first_name

        if types == "music":
            response = requests.post('https://gmental.pythonanywhere.com/send-music', data={'username': user_name, 'name': name, 'about': say}, files={'music': end})
        else:
            response = requests.post('https://gmental.pythonanywhere.com/set-topic', data={'username': user_name, 'name': name, 'title': end, 'body': say})
        bot.reply_to(message, f"({response}) - upload successfully. thanks <3")

    except Exception as e:
        print(e)
        bot.reply_to(message, f"oh, somthing went wrong!\n {e}")

bot.infinity_polling()