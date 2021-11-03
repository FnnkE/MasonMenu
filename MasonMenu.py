import discord
from discord import message
import requests
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from datetime import datetime

ikes = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16653&locationId=27747017&whereami=http://masondining.sodexomyway.com/dining-near-me/ikes"
southside = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16652&locationId=27747003&whereami=http://masondining.sodexomyway.com/dining-near-me/southside"
other = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16478&locationId=27747024&whereami=http://masondining.sodexomyway.com/dining-near-me/front-royal"

ikesP = requests.get(ikes)
ssP = requests.get(southside)
otherP = requests.get(other)

soupI = BeautifulSoup(ikesP.content, "lxml")
soupS = BeautifulSoup(ssP.content, "lxml")
soupO = BeautifulSoup(otherP.content, "lxml")

currentDay = soupI.find(class_="bite-date current-menu")
idCurrent = currentDay.get('id') + "-day"

menuI = soupI.find("div", id=idCurrent)
menuS = soupS.find("div", id=idCurrent)
menuO = soupO.find("div", id=idCurrent)

menus = []

TOKEN = 'ODkyMTA4ODQ2Mzg0OTUxMzA2.YVIHGw.fbB_55cRs0a4hn0v065apR1b3NE'

bot = commands.Bot(command_prefix="$")

ikes = 0
southside = 0
other = 0

loop = 24

@bot.event
async def on_ready():
    print('Bot Online')

@bot.command(name='ikes')
async def ikes(ctx):
    global ikes  
    global loop
    ikes = ctx.channel.id
    menus.append(menuI)
    await ctx.channel.send("Ike's channel has been set")
    now = datetime.now()
    hour = now.second
    loop = 25-hour

@bot.command(name='southside')
async def southside(ctx):
    global southside
    global loop
    southside = ctx.channel.id
    menus.append(menuS)
    await ctx.channel.send("Southside's channel has been set")
    now = datetime.now()
    hour = now.second
    loop = 25-hour

@bot.command(name='frontroyale')
async def frontroyale(ctx):
    global other
    global loop
    other = ctx.channel.id   
    menus.append(menuO)
    await ctx.channel.send("Front Royale Common's channel has been set")
    now = datetime.now()
    hour = now.second
    loop = 25-hour

@tasks.loop(hours=loop)
async def called_once_a_day():
    global loop
    loop = 60
    for m in menus:
        char = 0
        counter = 0
        temp = ''
        flag = 0
        if m == menuI:
            message_channel = bot.get_channel(ikes)
            temp= "⋯⋯⋯⋯⋯| **Ike's** |⋯⋯⋯⋯⋯ \n"
        elif m == menuS:
            message_channel = bot.get_channel(southside)
            temp= "⋯⋯⋯⋯⋯| **Southside** |⋯⋯⋯⋯⋯ \n"
        elif m == menuO: 
            message_channel = bot.get_channel(other)
            temp= "⋯⋯⋯⋯⋯| **SMSC Front Royal Commons** |⋯⋯⋯⋯⋯ \n"
        l = m.text.split("\n")
        print(l)
        
        for i in l:
            for s in temp.split():
                char += len(s)
            if char >= 1000:
                await message_channel.send(temp)
                print (temp)
                if flag == 1:
                    temp = '⠀'
                else:
                    temp = ''
            char = 0
            if i.strip() != '':
                print(repr(i)) 
                if i.isupper() == True:
                    if i == 'BREAKFAST' or i == 'LUNCH' or i == 'DINNER' or i == 'BRUNCH' or i == 'LATE NIGHT':
                        temp += '\n ━━━***__' + i + '__***━━━ \n'    
                    else:
                        temp += '\n **' + i + '** \n'      
                elif counter == 0:
                    flag = 1
                    if temp == '⠀':
                        temp += i.strip() + '\n'
                    else:
                        temp += '\t' + i.strip() + '\n'
                    counter += 1
                elif counter == 1:
                    flag = 0
                    counter = 0 
        if len(temp) > 0 and temp != '⠀':
            await message_channel.send(temp)
    
@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()
    print ("Finished waiting")
            
called_once_a_day.start()
bot.run(TOKEN)