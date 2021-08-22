# Rubaduck Bot
Bot for scheduled reminders. 
(Coming Soon: also for when you need a rubber duck to talk to)

Runs on Heroku. 
Currently using polling instead of webhooks.

## How to use 
0. Optional: set up your environment. I use in my project root folder:
```
python -m venv env
source env/bin/activate
```
1. Install requirements with `pip install -r requirements`
2. Create a bot using telegram's Botfather. Note down the TOKEN.
3. Create a `.env` file with the following env variables:
    - TOKEN : token of your bot. 
    - NAME : name of your bot 
    - CHAT_ID : for the chat you want to use the bot in.
4. Create a `msg` folder to contain any text you want to send. You can also remove references to this folder and just enter the text in the code directly. Mine has:
    - `start.md`
    - `quacks.txt`
5. Create a Heroku account if you haven't. 
6. Use `heroku git:remote -a YourAppName` to set up and `git push heroku master` to run


# References
1. [How to Deploy a Telegram Bot using Heroku for FREE](https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2)
2. [Dailybot](https://github.com/sapumar/dailybot)
3. [Python Telegram Bot with Scheduled Tasks](https://medium.com/analytics-vidhya/python-telegram-bot-with-scheduled-tasks-932edd61c534)