import logging
from settings import *
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

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


def queue_reminders(job_queue) -> None:
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
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = (
        "Timer successfully cancelled!" if job_removed else "You have no active timer."
    )
    update.message.reply_text(text)


def engage(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Mai kanchiong! Not ready yet!")


def disengage(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="Mai kanchiong! Not ready yet!")


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
    dispatcher.add_handler(CommandHandler("engage", engage))
    dispatcher.add_handler(CommandHandler("disengage", disengage))
    dispatcher.add_handler(CommandHandler("all_quacks", quacks))
    dispatcher.add_handler(CommandHandler("quack", quack))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))

    # Start the Bot
    updater.start_polling()
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN,
        webhook_url="https://{}.herokuapp.com/{}".format(NAME, TOKEN),
    )

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
