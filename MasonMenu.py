#Code By FnkE
from email.policy import default
from optparse import Values
from unittest import case
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
import sqlite3
import asyncio
import random

#Menu URLs
ikesURL = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16653&locationId=27747017&whereami=http://masondining.sodexomyway.com/dining-near-me/ikes"
southsideURL = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16652&locationId=27747003&whereami=http://masondining.sodexomyway.com/dining-near-me/southsideURL"
otherURL = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16478&locationId=27747024&whereami=http://masondining.sodexomyway.com/dining-near-me/front-royal"

#Discord Inits
TOKEN = 'OTU2OTYzNjI1NjQwMjc2MDUw.Yj330w.oxr26bjg7BzBYOgz0rF0HPDHsDk'
bot = commands.Bot(command_prefix="|", help_command=None, case_insensitive=True)

#Run on Bot Start
@bot.event
async def on_ready():
    await timeCalc()
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        guild_id TEXT,
        channel_id TEXT,
        name TEXT
        )
    ''')
    cursor.execute("SELECT channel_id FROM main WHERE guild_id = 0 AND name = 'system'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (0, time, 'system')
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (time, 0, 'system')
    cursor.execute(sql,val)
    print(f'Time has been recorded')
    db.commit()
    cursor.close()
    db.close()
    await updateMenus()
    print('Bot Online')

async def changePresence(): #updates status stats | still make random?
    await bot.wait_until_ready()
    index = 0
    while not bot.is_closed(): #Added more into the loop for constant updates
        guilds = bot.guilds
        members = 0
        if (index == 0):
            for guild in guilds:
                members += guild.member_count
        statuses = [f"with {members} users | $help", f"on {len(bot.guilds)} servers | $help", "discord.py", 'with Ike', 'around with the menus']
        status = statuses[index]
        print(status)
        await bot.change_presence(activity=discord.Game(name=status))
        index += 1
        if (index == len(statuses)): index = 0
        await asyncio.sleep(10) #lowered time for testing

async def timeCalc():
    global time
    #Calculate time
    print("Calculating time...")
    tz = timezone('US/Eastern')
    now = datetime.now(tz) #Get current time on East Coast
    hour = now.hour
    minute = hour*60 + now.minute
    time = 1500-minute #Calculate time till 1AM
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
    print("Time until next print: " + str(time))

async def viewMenu(ctx, name):
    if name == 'ikes':
        title = 'Ike\'s'
    elif name == 'southside':
        title = 'Southside'
    else:
        title = 'Front Royale Commons'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = '{name}'")
    result = cursor.fetchone()
    if result is None:
        print(f'{title} channel has not be set in {ctx.guild.id}')
        await ctx.send(f'{title} channel has not be set')
    elif result is not None:
        channelID = int(result[0])
        print(f"{title} channel set to <#{channelID}> in {ctx.guild.id}")
        await ctx.channel.send(f"{title} channel set to <#{channelID}>")
    cursor.close()
    db.close()    

async def updateMenus():
    global ikesP
    global ssP
    global otherP
    global currentDay
    global idCurrent
    global menuI
    global menuS
    global menuO

    valid = False
    while (valid == False):
        ikesP = requests.get(ikesURL)
        print("Ikes Response Code: ", ikesP.status_code)
        if ikesP.status_code == 200: valid = True
    soupI = BeautifulSoup(ikesP.content, "lxml")

    valid = False
    while (valid == False):
        ssP = requests.get(southsideURL)
        print("Southside Response Code: ", ssP.status_code)
        if ssP.status_code == 200: valid = True
    soupS = BeautifulSoup(ssP.content, "lxml")

    valid = False
    while (valid == False):
        otherP = requests.get(otherURL)
        print("Other Response Code: ", otherP.status_code)
        if otherP.status_code == 200: valid = True
    soupO = BeautifulSoup(otherP.content, "lxml")

    currentDay = soupI.find(class_="bite-date current-menu")
    idCurrent = currentDay.get('id') + "-day"
    menuI = soupI.find("div", id=idCurrent)
    print(idCurrent)

    menuI = soupI.find("div", id=idCurrent)
    menuS = soupS.find("div", id=idCurrent)
    menuO = soupO.find("div", id=idCurrent)

async def setMenu(ctx, name):
    if name == 'ikes':
        title = 'Ike\'s'
    elif name == 'southside':
        title = 'Southside'
    else:
        title = 'Front Royale Commons'
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = '{name}'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (ctx.guild.id, ctx.channel.id, name)
        print(f"{title} channel has been set to {ctx.channel.mention} in {ctx.guild.id}")
        await ctx.send(f"{title} channel has been set to {ctx.channel.mention}")
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, name)
        print(f"{title} channel has been updated to {ctx.channel.mention} in {ctx.guild.id}")
        await ctx.send(f"{title} channel has been updated to {ctx.channel.mention}")
    cursor.execute(sql,val)
    db.commit()
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
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = '{name}'")
    result = cursor.fetchone()
    if result is None:
        print(f'{title} channel has not be set in {ctx.guild.id}')
        await ctx.send(f"{title} channel has not been set")
    elif result is not None:
        sql = ("DELETE FROM main WHERE channel_id = ? AND guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, name)
        print(f'{title} channel has been removed in {ctx.guild.id}')
        await ctx.send(f"{title} channel has been removed")
    cursor.execute(sql,val)
    db.commit()
    cursor.close()
    db.close()

async def printMenu(cursor, guild_id=0):
    global menuI
    global menuS
    global menuO
    global currentDay
    global idCurrent

    updateMenus()
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
        breakfastFlag = False
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
        else:
            continue
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
                    if i == 'LUNCH' or i == 'DINNER' or i == 'BRUNCH' or i == 'LATE NIGHT':
                        temp += '\n ━━━***__' + i + '__***━━━ \n'    
                    elif i == 'BREAKFAST' and breakfastFlag == False:
                        temp += '\n ━━━***__' + i + '__***━━━ \n'
                        breakfastFlag = True
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

async def printEmbed(cursor, guild_id=0):
    global menuI
    global menuS
    global menuO
    global currentDay
    global idCurrent

    if guild_id > 0:
        result = cursor.execute(f"SELECT * FROM main WHERE guild_id={guild_id}")
    else:
        result = cursor.execute("SELECT * FROM main")
    data = result.fetchall()
    for d in data:
        #Inits
        title = ""
        counter = 0
        counters = 0
        values = ""
        breakfastFlag = False
        print(d)
        #Print Titles of Menus
        if d[2] == 'ikes':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            author = "Ikes"
            m = menuI
        elif d[2] == 'southside':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            author = "Southside"
            m = menuS
        elif d[2] == 'other': 
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            author = "Front Royale"
            m = menuO
        else:
            continue
        l = m.text.split("\n")
        #print(l)
        for i in l:
            #Adding Text to List Below
            if i.strip() != '':
                if i.isupper() == True or i == '-':
                    if i == 'LUNCH' or i == 'DINNER' or i == 'BRUNCH' or i == 'LATE NIGHT':
                        embed.add_field(name=title, value=values,inline= True)
                        values = ""
                        title = ""
                        await sendMessage(message_channel, embed) #could cause problems - (Brunch)
                        embed = discord.Embed(title=i, description= "Current Date", color = 0x87CEEB)    
                    elif i == 'BREAKFAST' and breakfastFlag == False:
                        embed = discord.Embed(title=i, description= "Current Date", color = 0x87CEEB)
                        breakfastFlag = True
                    else:
                        if title != "": 
                            embed.add_field(name=title, value=values,inline= True)
                            values = ""
                            counters += 1
                        title = i      
                elif counter == 0: #Skips calories
                    values += i.strip() + '\n'
                    counter += 1
                elif counter == 1:
                    counter = 0 
        embed.add_field(name=title, value=values,inline= True)
        embed.set_author(name=author)
        embed.set_footer(text="Test :)", icon_url="https://cdn.discordapp.com/emojis/754736642761424986.png")
        await sendMessage(message_channel, embed)
        break

async def printEmbedButBetter(cursor, guild_id=0): #Make Visually Better
    global menuI
    global menuS
    global menuO
    global currentDay
    global idCurrent

    if guild_id > 0:
        result = cursor.execute(f"SELECT * FROM main WHERE guild_id={guild_id}")
    else:
        result = cursor.execute("SELECT * FROM main")
    data = result.fetchall()
    for d in data:
        #Inits
        values = ["","","","","","","","","","","",""]
        titles = ['METRO GRILL', 'CLARENDON', 'DUPONT - PASTA', 'DUPONT - PIZZA', 'HOT CEREAL/SOUP', 'VIENNA', 'CAPITAL SOUTH - DELI',
                'EASTERN MARKET', 'SALAD BAR', 'SIMPLE SERVINGS', 'EASTERN-OMELET','MISCELLANEOUS']
        index = 0
        counter = 0
        breakfastFlag = False
        print(d)
        #Print Titles of Menus
        if d[2] == 'ikes':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            author = "Ikes"
            m = menuI
        elif d[2] == 'southside':
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            author = "Southside"
            m = menuS
        elif d[2] == 'other': 
            channelID = int(d[1])
            message_channel = bot.get_channel(channelID)
            print(message_channel)
            author = "Front Royale"
            m = menuO
        else:
            continue
        l = m.text.split("\n")
        #print(l)
        for i in l:
            #Adding Text to List Below
            if i.strip() != '':
                if i.isupper() == True or i == '-':
                    if i == 'LUNCH' or i == 'DINNER' or i == 'LATE NIGHT':
                        c=0
                        for v in values:
                            if v != "":
                                embed.add_field(name=titles[c], value=v,inline= True)
                            c+=1
                        values = ["","","","","","","","","","","",""]
                        title = ""
                        await sendMessage(message_channel, embed)
                        embed = discord.Embed(title=i, description= "Current Date", color = 0x87CEEB)    
                    elif i == 'BREAKFAST' and breakfastFlag == False:
                        embed = discord.Embed(title=i, description= "Current Date", color = 0x87CEEB)
                        breakfastFlag = True
                    elif i == 'BRUNCH':
                        embed = discord.Embed(title=i, description= "Current Date", color = 0x87CEEB)
                    else:
                        print(repr(i))                          
                        if i == 'METRO GRILL':
                            index = 0
                        elif i == 'CLARENDON':
                            index = 1
                        elif i == 'DUPONT - PASTA':
                            index = 2
                        elif i == 'DUPONT - PIZZA':
                            index = 3
                        elif i == 'HOT CEREAL/SOUP':
                            index = 4
                        elif i == 'VIENNA':
                            index = 5
                        elif i == 'CAPITAL SOUTH - DELI':
                            index = 6
                        elif i == 'EASTERN MARKET':
                            index = 7
                        elif i == 'SALAD BAR':
                            index = 8
                        elif i == 'SIMPLE SERVINGS':
                            index = 9
                        elif i == 'EASTERN-OMELET':
                            index = 10
                        elif i == 'MISCELLANEOUS':
                            index = 11     
                elif counter == 0: #Skips calories
                    print('index:', index)
                    values[index] += i.strip() + '\n'
                    counter += 1
                elif counter == 1:
                    counter = 0 
        c=0
        for v in values:
            if v != "":
                embed.add_field(name=titles[c], value=v,inline= True)
            c+=1
        embed.set_author(name=author)
        embed.set_footer(text="Test :)", icon_url="https://cdn.discordapp.com/emojis/754736642761424986.png")
        await sendMessage(message_channel, embed)
        break

async def sendMessage(message_channel, embed):
    msg = await message_channel.send(embed=embed)
    await msg.add_reaction("⬆️")
    await msg.add_reaction("🔻")

@bot.command(name='display')
@has_permissions(manage_channels = True)
async def display(ctx):#Embed test
    embed = discord.Embed(title="Breakfast", description= "March 28th", color = 0x87CEEB)
    embed.set_author(name="Ike's")
    embed.add_field(name="Food1", value="Food2",inline=True)
    embed.add_field(name="Food3", value="Food4",inline=True)
    embed.add_field(name="Food5", value="---",inline=True)
    embed.add_field(name="Food6", value="---",inline=False)
    embed.add_field(name="Station", value="Food7,Food7,Food7,Food7,Food7\nFood8\nFood9\nFood10",inline=True)
    embed.add_field(name="Station2", value="Food7,Food7,Food7,Food7,Food7\nFood12\nFood13\nFood14",inline=True)
    embed.set_footer(text="Fun messages?", icon_url="https://cdn.discordapp.com/emojis/754736642761424986.png")
    await ctx.send(embed=embed)

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
                message += str(int(c)//60) + ':'
                if int(c)%60 < 10:
                    message += "0" + str(int(c)%60)
                else:
                    message += str(int(c)%60)
        message += ' until next print'
    cursor.close()
    db.close()
    print(message)
    await ctx.channel.send(message)

@bot.command(name='help') #Print list of commands
@has_permissions(manage_channels = True)
async def help(ctx):
    message = """   Commands - \n
                    **$ikes** - Set channel to print Ike\'s menu \n
                    **$southside** - Set channel to print Southside\'s menu \n
                    **$frontroyale** - Set channel to print Front Royale Common\'s menu \n
                    **$viewikes** - View the channel where Ike\'s has been set to \n
                    **$viewsouthside** - View the channel where Southside\'s has been set to \n
                    **$viewikes** - View the channel where Front Royales\'s has been set to \n
                    **$rmIkes** - Remove the channel where Ike\'s has been set to \n
                    **$rmSouthside** - Remove the channel where Southside has been set to \n
                    **$rmFrontRoyale** - Remove the channel where Front Royale has been set to \n
                    **$time** - Check how long until next print (hh:mm) \n
                    **$print** - Force print all menus for your server \n"""
    await ctx.channel.send(message)

@bot.command(name='print') #Print list of commands
@has_permissions(manage_channels = True)
async def forcePrint(ctx):
    await updateMenus()
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    await printEmbedButBetter(cursor,guild_id=ctx.guild.id)
    db.close()

@bot.command(name='sql') #Print list of commands
@has_permissions(manage_channels = True)
async def sqlPrint(ctx):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM main")
    result = cursor.fetchall()
    for r in result:
        await ctx.channel.send(r)
    db.close()

#Run Daily at 1AM
@tasks.loop(minutes=1)
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
        time = 1440 #Reset Loop - SQL update
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
