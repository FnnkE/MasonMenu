#Code By FnkE
import discord
from discord import Member
from discord import message
from discord import channel
import requests
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pytz import timezone
import os
import sqlite3
import asyncio
import random


#Menu URLs
ikesURL = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16653&locationId=27747017&whereami=http://masondining.sodexomyway.com/dining-near-me/ikes"
southsideURL = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16652&locationId=27747003&whereami=http://masondining.sodexomyway.com/dining-near-me/southsideURL"
otherURL = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16478&locationId=27747024&whereami=http://masondining.sodexomyway.com/dining-near-me/front-royal"

#Get Pages
ikesP = requests.get(ikesURL)
ssP = requests.get(southsideURL)
otherP = requests.get(otherURL)

#Convert Pages
soupI = BeautifulSoup(ikesP.content, "lxml")
soupS = BeautifulSoup(ssP.content, "lxml")
soupO = BeautifulSoup(otherP.content, "lxml")

#Calculate Current Day
currentDay = soupI.find(class_="bite-date current-menu")
idCurrent = currentDay.get('id') + "-day"

#Limit Page to Current Day
menuI = soupI.find("div", id=idCurrent)
menuS = soupS.find("div", id=idCurrent)
menuO = soupO.find("div", id=idCurrent)

#Discord Inits
TOKEN = os.getenv("TOKEN")
bot = commands.Bot(command_prefix="$", help_command=None, case_insensitive=True)

#Various Inits
ikesC = 0 #Default Channel ID
southsideC = 0 #Default Channel ID
otherC = 0 #Default Channel ID
menus = [menuI, menuS, menuO]
tz = timezone('US/Eastern')
now = datetime.now(tz) #Get current time on East Coast
hour = now.hour
time = 25-hour

async def changePresence():
    await bot.wait_until_ready()
    guilds = bot.guilds
    members = 0
    for guild in guilds:
        members += len(guild.members)
    statuses = [f"with {members} users | $help", f"on {len(bot.guilds)} servers | $help", "discord.py", 'with Ike', 'around with the menus']

    while not bot.is_closed():
        status = random.choice(statuses)
        await bot.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(10)


async def timeCalc():
    global time
    #Calculate time
    tz = timezone('US/Eastern')
    now = datetime.now(tz) #Get current time on East Coast
    hour = now.hour
    time = 25-hour #Calculate time till 1AM
    db = sqlite3.connect('main.sqlite') 
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (0, time, 'system')
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (time, 0, 'system')
    cursor.execute(sql,val)
    db.commit()
    cursor.close()
    db.close()

async def setMenu(ctx, name):
    if name == 'ikes':
        title = 'Ike\'s'
    elif name == 'southside':
        title = 'Southside'
    else:
        title = 'Front Royale Commons'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = name")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (ctx.guild.id, ctx.channel.id, name)
        await ctx.send(f"{title} channel has been set to {ctx.channel.mention}")
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, name)
        await ctx.send(f"{title} channel has been updated to {ctx.channel.mention}")
    cursor.execute(sql,val)
    print(f'A channel for {title} has been set')
    db.commit()
    cursor.close()
    db.close()

async def viewMenu(ctx, name):
    if name == 'ikes':
        title = 'Ike\'s'
    elif name == 'southside':
        title = 'Southside'
    else:
        title = 'Front Royale Commons'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = name")
    result = cursor.fetchone()
    if result is None:
        await ctx.send(f'{title} channel has not be set')
    elif result is not None:
        channelID = int(result[0])
        await ctx.channel.send(f"{title} channel set to <#{channelID}>")
    cursor.close()
    db.close()

async def rmMenu(ctx, name):
    if name == 'ikes':
        title = 'Ike\'s'
    elif name == 'southside':
        title = 'Southside'
    else:
        title = 'Front Royale Commons'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = name")
    result = cursor.fetchone()
    if result is None:
        await ctx.send(f"{title} channel has not been set")
    elif result is not None:
        sql = ("DELETE FROM main WHERE channel_id = ? AND guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, name)
        await ctx.send(f"{title} channel has been removed")
    cursor.execute(sql,val)
    print(f'A channel for {title} has been removed')
    db.commit()
    cursor.close()
    db.close()

async def printMenu(cursor, guild_id=0):
    global menuI
    global menuS
    global menuO
    global menus
    global currentDay
    global idCurrent
    global soupI
    currentDay = soupI.find(class_="bite-date current-menu")
    idCurrent = currentDay.get('id') + "-day"
    #Check if requests are updating
    if menuI in menus:
        menus.remove(menuI)
        ikesP = requests.get(ikesURL)
        soupI = BeautifulSoup(ikesP.content, "lxml")
        menuI = soupI.find("div", id=idCurrent)
        menus.append(menuI)
        print('Ike\'s updated')
    if menuS in menus:
        menus.remove(menuS)
        ssP = requests.get(southsideURL)
        soupS = BeautifulSoup(ssP.content, "lxml")
        menuS = soupS.find("div", id=idCurrent)
        menus.append(menuS)
        print('Southside updated')
    if menuO in menus:
        menus.remove(menuO)
        otherP = requests.get(otherURL)
        soupO = BeautifulSoup(otherP.content, "lxml")
        menuO = soupO.find("div", id=idCurrent)
        menus.append(menuO)
        print('Other updated')
    if guild_id > 0:
        result = cursor.execute(f"SELECT * FROM main WHERE guild_id={guild_id}")
    else:
        result = cursor.execute("SELECT * FROM main")
    data = result.fetchall()
    for d in data:
        #Inits
        char = 0
        counter = 0
        temp = ''
        flag = 0
        print(d)
        #Print Titles of Menus
        if d[2] == 'ikes':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            temp= "⋯⋯⋯⋯⋯| **Ike's** |⋯⋯⋯⋯⋯ \n"
            m = menuI
        elif d[2] == 'southside':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            temp= "⋯⋯⋯⋯⋯| **Southside** |⋯⋯⋯⋯⋯ \n"
            m = menuS
        elif d[2] == 'other': 
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            temp= "⋯⋯⋯⋯⋯| **SMSC Front Royal Commons** |⋯⋯⋯⋯⋯ \n"
            m = menuO
        l = m.text.split("\n")
        #print(l)
        for i in l:
            #Calc Characters and Send if Needed
            for s in temp.split():
                char += len(s)
            if char >= 1000:
                msg = await message_channel.send(temp)
                #print (temp)
                if flag == 1:
                    temp = '⠀'
                else:
                    temp = ''
            char = 0
            #Adding Text to List Below
            if i.strip() != '':
                #print(repr(i)) 
                if i.isupper() == True or i == '-': #Add Text Decor
                    if i == 'BREAKFAST' or i == 'LUNCH' or i == 'DINNER' or i == 'BRUNCH' or i == 'LATE NIGHT':
                        temp += '\n ━━━***__' + i + '__***━━━ \n'    
                    else:
                        temp += '\n **' + i + '** \n'      
                elif counter == 0: #I'm going to be honest, i forgot what happens after
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
            msg = await message_channel.send(temp)
        await msg.add_reaction("⬆️")
        await msg.add_reaction("🔻")

#Run on Bot Start
@bot.event
async def on_ready():
    print('Bot Online')
    return await bot.change_presence(activity=discord.Game(name='Bot Things'))

#Run on $ikes
@bot.command(name='ikes')
@has_permissions(manage_channels = True)
async def ikes(ctx):
    await setMenu(ctx, 'ikes')
    await timeCalc()

#Print channel set to Ike's
@bot.command(name='viewikes')
@has_permissions(manage_channels = True)
async def viewIkes(ctx):
    await viewMenu(ctx, 'ikes')

@bot.command(name='rmikes')
@has_permissions(manage_channels = True)
async def rmIkes(ctx):
    await rmMenu(ctx, 'ikes')

#Run on $southside
@bot.command(name='southside')
@has_permissions(manage_channels = True)
async def southside(ctx):
    await setMenu(ctx, 'southside')
    await timeCalc()

    
@bot.command(name='viewsouthside')
@has_permissions(manage_channels = True)
async def viewSS(ctx):
    await viewMenu(ctx, 'southside')

@bot.command(name='rmsouthside')
@has_permissions(manage_channels = True)
async def rmSS(ctx):
    await rmMenu(ctx, 'southside')

#Run on $frontroyale
@bot.command(name='frontroyale')
@has_permissions(manage_channels = True)
async def frontroyale(ctx):
    await setMenu(ctx, 'other')
    await timeCalc()

@bot.command(name='viewfrontroyale')
@has_permissions(manage_channels = True)
async def viewOther(ctx):
    await viewMenu(ctx, 'other')

@bot.command(name='rmfrontroyale')
@has_permissions(manage_channels = True)
async def rmOther(ctx):
    await rmMenu(ctx, 'other')

@bot.command(name='time')
@has_permissions(manage_channels = True)
async def timeCheck(ctx):
    print('checking time')
    message=''
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        message = 'Error: Time not set'
    elif result is not None:
        for c in result:
            if c.isnumeric() == True:
                message += c
        message += ' hours until next print'
    cursor.close()
    db.close()
    await ctx.channel.send(message)

@bot.command(name='help') #Print list of commands
@has_permissions(manage_channels = True)
async def help(ctx):
    message = """   Commands - \n
                    **$ikes** - Set channel to print Ike\'s menu \n
                    **$southside** - Set channel to print Southside\'s menu \n
                    **$frontroyale** - Set channel to print Front Royale Common\'s menu \n
                    **$time** - Check how long until next print (Rough hour estimate) \n
                    **$viewikes** - View the channel where Ike\'s has been set to \n
                    **$viewsouthside** - View the channel where Southside\'s has been set to \n
                    **$viewikes** - View the channel where Front Royales\'s has been set to \n
                    **$rmIkes** - Remove the channel where Ike\'s has been set to \n
                    **$rmSouthside** - Remove the channel where Southside has been set to \n
                    **$rmFrontRoyale** - Remove the channel where Front Royale has been set to \n"""
    await ctx.channel.send(message)

@bot.command(name='print') #Print list of commands
@has_permissions(manage_channels = True)
async def forcePrint(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    await printMenu(cursor,guild_id=ctx.guild.id)

#Run Daily at 1AM
@tasks.loop(hours=1)
async def calledPerDay():
    global time
    #Put time var on SQL database
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        message = 'Error: Time not set'
        print(message)
    elif result is not None:
        for c in result:
            if c.isnumeric() == True:
                time = int(c)
    time -= 1
    sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
    val = (time, 0, 'system')
    cursor.execute(sql,val)
    if time == 0:
        time = 24 #Reset Loop - SQL update
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (time, 0, 'system')
        cursor.execute(sql,val)
        await printMenu(cursor)
    db.commit()
    cursor.close()
    db.close()

@calledPerDay.before_loop
async def before():
    await bot.wait_until_ready()

calledPerDay.start()
bot.loop.create_task(changePresence())
bot.run(TOKEN)
