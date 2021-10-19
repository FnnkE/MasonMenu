import discord
from discord import message
import requests
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

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

menus = [menuI, menuS, menuO]

TOKEN = 'ODkyMTA4ODQ2Mzg0OTUxMzA2.YVIHGw.fbB_55cRs0a4hn0v065apR1b3NE'

client = discord.Client()
ikes=891893981393354783
southside=891894003547660321
other=899727333970292797

@client.event
async def on_ready():
    print('Bot Online')

@tasks.loop(hours=24.0)
async def called_once_a_day():
    for m in menus:
        if m == menuI:
            message_channel = client.get_channel(ikes)
        elif m == menuS:
            message_channel = client.get_channel(southside)
        else: 
            message_channel = client.get_channel(other)
        l = m.text.split("\n")
        print(l)
        char = 0
        counter = 0
        temp = ''
        flag = 0
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
    await client.wait_until_ready()
    print ("Finished waiting")
            
called_once_a_day.start()
client.run(TOKEN)