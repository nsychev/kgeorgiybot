#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, Updater
import logging
import random
import yaml

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

message_cache = {}

with open("config.yaml") as f:
    config = yaml.safe_load(f.read())

def get_user(user):
    if user.username:
        full_name = f"@{user.username}"
    else:
        full_name = f"({user.first_name}"
        if user.last_name:
            full_name += f" {user.last_name}"
        full_name += ")"
    return f"{user.id} {full_name}"


def get_chat(chat):
    chat_name = f"{chat.id} ({chat.title}"
    if chat.username:
        chat_name += f" / {chat.username}"
    chat_name += ")"
    return chat_name


def logged_query(func):
    def wrapper(update: Update, context: CallbackContext):
        if update.message:
            message = update.message

            user = message.from_user
            chat = message.chat

            sender_info = get_user(user)
            if chat.id != user.id:
                sender_info += f", chat {get_chat(chat)}"

            content = message.text
            if message.pinned_message:
                content = f"<pin> {message.pinned_message.text}"

            if content:
                logger.info(f"{sender_info}: {content}")

        func(update, context)

    return wrapper


def send_file(filename: str):
    @logged_query
    def func(update: Update, context: CallbackContext):
        chat_id = update.message.chat.id
        last_message = message_cache.get(chat_id, {}).get(filename)

        if last_message:
            try:
                context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=last_message
                )
            except:
                pass

        with open(f"{filename}.txt") as f:
            text = f.read()

        message = update.message.reply_text(
            text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
        message_cache.setdefault(chat_id, {})[filename] = message.message_id

    return func


@logged_query
def okey(update: Update, context: CallbackContext):
    if random.randint(0, 1):
        update.message.reply_text("Окэй")
    else:
        update.message.reply_sticker(sticker=random.choice(config['stickers']))


def error(update: Update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def loop():
    updater = Updater(config['token'], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("y2017", send_file("y2017")))
    dp.add_handler(CommandHandler("y2018", send_file("y2018")))
    dp.add_handler(CommandHandler("y2019", send_file("y2019")))
    dp.add_handler(CommandHandler("y2020", send_file("y2020")))
    dp.add_handler(MessageHandler(Filters.status_update.pinned_message, okey))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    loop()
