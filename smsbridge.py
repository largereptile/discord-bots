#!/usr/bin/env python

"""sms bridge using twilio and discordpy version like 0.6"""


import asyncio
from twilio.rest import TwilioRestClient
import discord

class User:
    def __init__(self):
        self.own_number = "Your own phone number"               
        self.twilio_number = "The phone number twilio gave you" 
        self.discord_user_id = "Your discord user ID"           # Right click on your own name in discord and click "copy ID" with dev mode on
        self.discord_email = "Your discord email"               
        self.discord_password = "Your discord password"         
        self.twilio_sid = "Your twilio account SID"             # Your twilio account SID
        self.twilio_auth_token = "Your twilio auth token"       # Your twilio auth token


user = User()


tclient = TwilioRestClient(user.twilio_sid, user.twilio_auth_token)
dclient = discord.Client()


class Bot:
    def __init__(self):
        self.last_message = tclient.messages.list(from_=user.own_number)[0].sid
        self.channel = ""
        self.should_i = False


bot = Bot()


@dclient.event
async def on_ready():
    print('Logged in as')
    print(dclient.user.name)
    print(dclient.user.id)
    print('------')


@dclient.event
async def on_message(message):
    msg = message.content.split(" ")
    if message.channel == bot.channel and message.author.id != user.discord_user_id and bot.should_i:
        body = (message.author.name + ":\n" + message.content)
        tclient.sms.messages.create(to=user.own_number, from_=user.twilio_number, body=body)

    elif message.author.id == user.discord_user_id and msg[0] == "~toggle":
        bot.should_i, bot.channel = toggler(dclient, bot.should_i, message.channel.id)
        await dclient.delete_message(message)

    elif message.author.id == user.discord_user_id and msg[0] == "~textme":
        bot.channel = dclient.get_channel(message.channel.id)
        await dclient.delete_message(message)


async def message_receive():
    await dclient.wait_until_ready()
    while not dclient.is_closed:
        newmessage = tclient.messages.list(from_=user.own_number)[0]
        if newmessage.sid != bot.last_message and bot.should_i:
            await dclient.send_message(bot.channel, newmessage.body)
            bot.last_message = newmessage.sid
        await asyncio.sleep(1)


def toggler(client, toggle, channel):
    if not toggle:
        channel = client.get_channel(channel)
    else:
        channel = ""
    return not toggle, channel


dclient.loop.create_task(message_receive())
dclient.run(user.discord_email, user.discord_password)
