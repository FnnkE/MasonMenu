#Code By FnkE
import discord
from discord import Member
from discord import message
import requests
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pytz import timezone
import os


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
"""
TOKEN = os.read("TOKEN")
"""
TOKEN = 'ODY4OTQ2Mzk2NDIwNjQwODI4.YP3DZQ.zttad6Mq71vww1iVxqWXtElol6E'
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
    print('Bot Online')

#Run on $ikes
@bot.command(name='ikes')
@has_permissions(manage_channels = True)
async def ikes(ctx):
    global ikes  
    global time
    ikes = ctx.channel.id #Get Channel ID
    if menuI not in menus:
        menus.append(menuI) #Add Ikes' Menu to List for Printing
    await ctx.channel.send("Ike's channel has been set") #Confirm Channel Set
    #Calculate Current Time Till 1AM
    tz = timezone('US/Eastern')
    now = datetime.now(tz)
    hour = now.hour
    time = 25-hour

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
    print(menuO in menus)
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
    if time == 0:
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
    time -= 1

@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()
    print ("Finished waiting")
            
called_once_a_day.start()
bot.run(TOKEN)