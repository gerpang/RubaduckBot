import logging
from settings import *
from os.path import join, dirname
from dotenv import load_dotenv
import requests

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)

LISTENING, REPLYING, SEARCHING = range(3)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    with open(START_FILE) as start_file:
        try:
            start_text = start_file.read()
            update.message.reply_text(
                text=start_text,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as error:
            logger.error(error)
    # update.message.reply_text("Hi! Use /set <seconds> to set a timer")


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text="Beep!")


def send_meal_reminder(context: CallbackContext) -> None:
    """Send a meal reminder at the set time"""
    job = context.job
    context.bot.send_message(job.context, text="[🐤🤖] THIS IS A REMINDER: PLEASE EAT!")


def health_check(context: CallbackContext) -> None:
    try:
        response = requests.get(
            f"https://api.telegram.org/bot${TOKEN}/getWebhookInfo", timeout=30
        )
        logger.debug(response.status_code)
    except Exception as error:
        logger.error(error)


def queue_reminders(job_queue) -> None:
    job_queue.run_repeating(
        health_check,
        interval=300,
    )
    job_queue.run_daily(
        send_meal_reminder,
        time=datetime.time(hour=4, minute=30),
        days=(0, 1, 2, 3, 4),
        context=CHAT_ID,
        name=str(CHAT_ID),
    )
    job_queue.run_daily(
        send_meal_reminder,
        time=datetime.time(hour=11, minute=0),
        days=(0, 1, 2, 3, 4),
        context=CHAT_ID,
        name=str(CHAT_ID),
    )


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text("Sorry we can not go back to future!")
            return

        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = "Timer successfully set!"
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /set <seconds>")


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    text = "Timer successfully cancelled!"
    update.message.reply_text(text)


def listen(update: Update, context: CallbackContext) -> None:
    context.user_data["count"] += 1
    count = context.user_data["count"]
    interval = context.user_data["interval"]
    if count < interval:
        return LISTENING
    else:
        context.user_data["count"] = 0
        return quack(update, context)


def search(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Give me a second, I'll look that up.")
    try:
        from googlesearch import search
    except ImportError:
        logger.debug("No module named 'google' found")
    # to search
    query = " ".join(context.args)
    results = "This is what I found:\n\n"
    for j in search(query, tld="co.in", num=3, stop=5, pause=2):
        results += f"{j}\n"
    update.message.reply_text(results)
    logger.debug("Completed the search")
    return LISTENING


def engage(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="I'm listening. Talk to me.")
    context.user_data["count"] = 0
    try:
        context.user_data["interval"] = int(context.args[0])
    except:
        context.user_data["interval"] = 5
    print(f'Listening; Will reply every {context.user_data["interval"]} messages')
    return LISTENING


def disengage(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Roger that, bye.")
    return ConversationHandler.END


def quacks(update: Update, context: CallbackContext) -> None:
    with open(QUACKS) as quacks:
        try:
            quacks = quacks.read()  # .split('\n')
            text = """
            Right now, these are the ways I can quack! \n---\n{}
            """.format(
                quacks
            )
            update.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as error:
            logger.error(error)


def quack(update: Update, context: CallbackContext) -> None:
    with open(QUACKS) as quacks:
        try:
            import random

            quacks = quacks.read().split("\n")
            update.message.reply_text(text=random.choice(quacks))
        except Exception as error:
            logger.error(error)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # auto reminders on
    j = updater.job_queue
    queue_reminders(j)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("all_quacks", quacks))
    dispatcher.add_handler(CommandHandler("quack", quack))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("engage", engage)],
            states={
                LISTENING: [
                    MessageHandler(Filters.text & ~Filters.command, listen),
                    CommandHandler("search", search),
                ],
                REPLYING: [MessageHandler(Filters.text & ~Filters.command, quack)],
            },
            fallbacks=[CommandHandler("disengage", disengage)],
        )
    )
    # Start the Bot
    # updater.start_polling()
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN,
        webhook_url=URL,
    )

    updater.idle()


if __name__ == "__main__":
    main()
