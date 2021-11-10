#Code By FnkE
import discord
from discord import Member
from discord import message
from discord import channel
import requests
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pytz import timezone
import os
import sqlite3


#Menu URLs
ikes = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16653&locationId=27747017&whereami=http://masondining.sodexomyway.com/dining-near-me/ikes"
southside = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16652&locationId=27747003&whereami=http://masondining.sodexomyway.com/dining-near-me/southside"
other = "https://menus.sodexomyway.com/BiteMenu/Menu?menuId=16478&locationId=27747024&whereami=http://masondining.sodexomyway.com/dining-near-me/front-royal"

#Get Pages
ikesP = requests.get(ikes)
ssP = requests.get(southside)
otherP = requests.get(other)

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
TOKEN = 'ODkyMTA4ODQ2Mzg0OTUxMzA2.YVIHGw.tt9EnW3Fb040RUvSV2nqSckZGAg'#os.getenv("TOKEN")
bot = commands.Bot(command_prefix="$")

#Various Inits
ikes = 0 #Default Channel ID
southside = 0 #Default Channel ID
other = 0 #Default Channel ID
menus = []
time = 24

#Run on Bot Start
@bot.event
async def on_ready():
    """
    Initializing main db
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        guild_id TEXT,
        channel_id TEXT,
        name TEXT
        )
    ''')
    """
    print('Bot Online')
    
    return await bot.change_presence(activity=discord.Streaming(name="Bot Things", url='https://www.twitch.tv/fnke'))

#Run on $ikes
@bot.command(name='ikes')
@has_permissions(manage_channels = True)
async def ikes(ctx):
    global ikes  
    global time
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id} AND name = 'ikes'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO main(guild_id, channel_id, name) VALUES(?,?,?)")
        val = (ctx.guild.id, ctx.channel.id, 'ikes')
        await ctx.send(f"Channel has been set to {ctx.channel.mention}")
    elif result is not None:
        sql = ("UPDATE main SET channel_id = ? WHERE guild_id = ? AND name = ?")
        val = (ctx.channel.id, ctx.guild.id, 'ikes')
        await ctx.send(f"Update... Channel has been set to {ctx.channel.mention}")
    cursor.execute(sql,val)
    db.commit()
    cursor.close()
    db.close()
    print('A channel for Ike\'s set')
    if menuI not in menus:
        menus.append(menuI) #Add Ikes' Menu to List for Printing
    #Calculate Current Time Till 1AM
    tz = timezone('US/Eastern')
    now = datetime.now(tz)
    hour = now.hour
    time = 25-hour

@bot.command(name='viewikes')
@has_permissions(manage_channels = True)
async def viewIkes(ctx):
    if ikes == 0:
        await ctx.channel.send('Ikes channel not set') #Confirm Channel Set
    else:
        await ctx.channel.send(ikes)

#Run on $southside
@bot.command(name='southside')
@has_permissions(manage_channels = True)
async def southside(ctx):
    global southside
    global time
    southside = ctx.channel.id #Get Channel ID
    if menuS not in menus:
        menus.append(menuS) #Add Southside's Menu to List for Printing
    await ctx.channel.send("Southside's channel has been set") #Confirm Channel Set
    #Calculate Current Time Till 1AM
    tz = timezone('US/Eastern')
    now = datetime.now(tz)
    hour = now.hour
    time = 25-hour

#Run on $frontroyale
@bot.command(name='frontroyale')
@has_permissions(manage_channels = True)
async def frontroyale(ctx):
    global other
    global time
    other = ctx.channel.id #Get Channel ID
    if menuO not in menus:
        menus.append(menuO) #Add Front Royale's Menu to List for Printing
    await ctx.channel.send("Front Royale Common's channel has been set") #Confirm Channel Set
    #Calculate Current Time Till 1AM
    tz = timezone("US/Eastern")
    now = datetime.now(tz)
    hour = now.hour
    time = 25-hour
    
#Run on $time
@bot.command(name='time')
@has_permissions(manage_channels = True)
async def timeCheck(ctx):
    message = str(time) + ' Hours Until Print'
    await ctx.channel.send(message)

@bot.command(name='forceprint')
@has_permissions(manage_channels = True)
async def forcePrint(ctx):
    global loop
    global time
    time = 0
    print('Forcing print')


#Run Daily at 1AM
@tasks.loop(hours=1)
async def called_once_a_day():
    global loop
    global time
    global menuI
    global menuS
    global menuO
    global menus

    time -= 1
    if time == 0:
        if menuI in menus:
            menus.remove(menuI)
            soupI = BeautifulSoup(ikesP.content, "lxml")
            menuI = soupI.find("div", id=idCurrent)
            menus.append(menuI)
        if menuS in menus:
            menus.remove(menuS)
            soupS = BeautifulSoup(ssP.content, "lxml")
            menuS = soupS.find("div", id=idCurrent)
            menus.append(menuS)
        if menuO in menus:
            menus.remove(menuO)
            soupO = BeautifulSoup(otherP.content, "lxml")
            menuO = soupS.find("div", id=idCurrent)
            menus.append(menuO)
        time = 24 #Reset Loop
        for m in menus:
            #Inits
            char = 0
            counter = 0
            temp = ''
            flag = 0
            #Print Titles of Menus
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
            #print(l)

            for i in l:
                #Calc Characters and Send if Needed
                for s in temp.split():
                    char += len(s)
                if char >= 1000:
                    await message_channel.send(temp)
                    #print (temp)
                    if flag == 1:
                        temp = '⠀'
                    else:
                        temp = ''
                char = 0
                #Adding Text to List Below
                if i.strip() != '':
                    #print(repr(i)) 
                    if i.isupper() == True: #Add Text Decor
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
                await message_channel.send(temp)

@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()
    print ("Finished waiting")
            
called_once_a_day.start()
bot.run(TOKEN)