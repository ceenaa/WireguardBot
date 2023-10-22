import os
import threading

import telebot
import functions
import auto
import db
import sheet

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)


def all_request(message):
    return message.text == "All"


@bot.message_handler(func=all_request)
def send_all(message):
    try:
        s = ""
        i = 0
        for peer in functions.sortedPeer:
            s += peer.show_string() + "\n----------------\n"
            i += 1
            if i % 20 == 0:
                bot.send_message(message.chat.id, s)
                s = ""
        if s != "":
            bot.send_message(message.chat.id, s)
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def count_request(message):
    return message.text == "Count"


def export_request(message):
    return message.text == "Export"


@bot.message_handler(func=export_request)
def send_export(message):
    try:
        functions.export()
        bot.send_message(message.chat.id, "Exported !")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


@bot.message_handler(func=count_request)
def send_count(message):
    try:
        bot.send_message(message.chat.id, functions.sortedPeer.__len__())
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def reload_request(message):
    return message.text == "Reload"


@bot.message_handler(func=reload_request)
def send_max(message):
    try:
        functions.reload()
        sheet.main()
        bot.send_message(message.chat.id, "Reloaded!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def pause_request(message):
    if "Pause" in message.text:
        name = message.text.split(" ")[1]
        if name in functions.peerMap.keys():
            return True
    return False


@bot.message_handler(func=pause_request)
def send_pause(message):
    try:
        name = message.text.split(" ")[1]
        functions.pause_user(name)
        bot.send_message(message.chat.id, "Paused!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def resume_request(message):
    if "Resume" in message.text:
        name = message.text.split(" ")[1]
        if name in functions.peerMap.keys():
            return True
    return False


@bot.message_handler(func=resume_request)
def send_resume(message):
    try:
        name = message.text.split(" ")[1]
        functions.resume_user(name)
        bot.send_message(message.chat.id, "Resumed!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def reset_user(message):
    if "Reset" in message.text:
        name = message.text.split(" ")[1]
        if name in functions.peerMap.keys():
            return True
    return False


@bot.message_handler(func=reset_user)
def send_reset(message):
    try:
        name = message.text.split(" ")[1]
        functions.pause_user(name)
        functions.resume_user(name)
        bot.send_message(message.chat.id, "Usage has been reset!")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def user_request(message):
    return message.text in functions.peerMap.keys()


@bot.message_handler(func=user_request)
def send_user(message):
    cid = message.chat.id
    message_text = message.text
    try:
        bot.send_message(cid, functions.peerMap[message_text].show_string())
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


def paused_users_request(message):
    return message.text == "Paused users"


@bot.message_handler(func=paused_users_request)
def send_paused_users(message):
    cid = message.chat.id
    try:
        connection = db.connect()
        paused_user = db.paused_users(connection)
        connection.close()
        s = ""
        i = 0
        for pu in paused_user:
            s += (functions.peerMap[pu[0]]).show_string() + "\n----------------\n"
            i += 1
            if i % 20 == 0:
                bot.send_message(message.chat.id, s)
                s = ""
        if s == "":
            bot.send_message(message.chat.id, "No paused user")
        if s != "":
            bot.send_message(message.chat.id, s)

    except Exception as err:
        bot.send_message(cid, type(err).__name__ + " " + str(err))


def usage_request(message):
    return message.text == "Usage"


@bot.message_handler(func=usage_request)
def send_usage(message):
    try:
        connection = db.connect()
        data = db.get_usage_for_name(connection, functions.conf_name)
        name = data[0]
        start_time = data[1]
        usage = functions.total
        connection.close()
        bot.send_message(message.chat.id,
                         "Name: " + name + "\nStart time: " + start_time + " : " + str(
                             functions.total_days()) + "days" + "\nUsage: " + str(usage) + " Gib")
    except Exception as err:
        bot.send_message(message.chat.id, type(err).__name__ + " " + str(err))


functions.reload()
sheet.main()
threading.Thread(target=lambda: auto.auto()).start()
bot.polling(none_stop=True, interval=0)
