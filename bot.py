from dotenv import load_dotenv
import os
from os.path import join, dirname
import telebot
from telebot import types
from currency_converter import CurrencyConverter

currency = CurrencyConverter()

def get_from_env(key):
    dotenv_path = join(dirname(__file__), 'token.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)

token = get_from_env('TG_BOT_TOKEN')
bot = telebot.TeleBot(token)


amount = 0

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Приветствуем Вас! Введите сумму для конвертации.")
    bot.register_next_step_handler(message, summa)

def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Введите число.")
        bot.register_next_step_handler(message, summa)
        return
    

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("USD/EUR", callback_data ="usd/eur")
        btn2 = types.InlineKeyboardButton("EUR/USD", callback_data ="eur/usd")
        btn3 = types.InlineKeyboardButton("USD/GBP", callback_data ="usd/gbp")
        btn4 = types.InlineKeyboardButton("Другое значение", callback_data ="else")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "Введите пару валют.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Число должно быть положительным. Попробуйте еще раз.")
        bot.register_next_step_handler(message, summa)

 


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f"Получается {round(res, 2)}. Можете ввести новую сумму.")
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, "Введите пару валют через /")
        bot.register_next_step_handler(call.message, my_currency)

def my_currency(message):
    try:
        values = message.text.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f"Получается {round(res, 2)}. Можете ввести новую сумму.")
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, 'Некорректная валюта. Попробуйте еще раз.')
        bot.register_next_step_handler(message, my_currency)
        







bot.polling(none_stop=True)
