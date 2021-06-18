# By Berjis Karbhari

import discord
import requests
import urllib.parse
from discord.ext import commands
import matplotlib.pyplot as plt
import os

STATTRACK = 'StatTrak%E2%84%A2%20'

GREEN = discord.colour.Colour(0).from_rgb(r=0, g=255, b=0)

TOKEN = 'YOUR TOKEN GOES HERE'
intents = discord.Intents(messages=True, guilds=True, reactions=True,
                          members=True, presences=True)
csgoBot = commands.Bot(command_prefix='!', intents=intents)

condition_dict = {"BS": "Battle-Scarred", "WW": "Well-Worn",
                  "FT": "Field-Tested", "MW": "Minimal Wear",
                  "FN": "Factory New"}


def makeGraph(link, timeframe):
    data = requests.get(link + "&full=1").json()[-timeframe:]
    y = []
    plt.style.use('dark_background')
    plt.title(f"Sales data for the last {timeframe} transactions")

    for entry in range(len(data)):
        y.append(data[entry][1])

    plt.plot(list(range(len(data))), y, marker='o')

    for entry in range(len(data)):
        plt.annotate(str(data[entry][1]) + "USD",
                     xy=(entry + 0.2, data[entry][1]))

    plt.savefig('graph.png')


def getWeaponInfo(weapon_name: str, skin: str, condition: str,
                  currency: str):
    CSGO_LINK = "http://csgobackpack.net/api/GetItemPrice/?"

    weapon_with_skin = weapon_name + " | " + skin + f" ({condition_dict[condition]})"

    embedVar = discord.Embed(title="Data for the " + weapon_with_skin,
                             description=f"Pricing and sales information for {weapon_name + ' ' + skin}",
                             color=0x00ff00)

    data_dict = {"currency": currency,
                 "id": weapon_with_skin,
                 "time": 10, "icon": 1}

    final = CSGO_LINK + urllib.parse.urlencode(data_dict)

    weapon_data = requests.get(final).json()

    if weapon_data['success'] and weapon_data['success'] != 'false':
        embedVar.set_thumbnail(url=weapon_data['icon'])

        embedVar.add_field(name="Condition: ", value=condition_dict[condition],
                           inline=False)
        embedVar.add_field(name="Lowest Price: ",
                           value=weapon_data['lowest_price'] + " " + currency,
                           inline=True)
        embedVar.add_field(name="Average Price: ",
                           value=weapon_data['average_price'] + " " + currency,
                           inline=True)
        embedVar.add_field(name="Highest Price: ",
                           value=weapon_data['highest_price'] + " " + currency,
                           inline=True)

        embedVar.add_field(name="Amount Sold: ",
                           value=weapon_data['amount_sold'], inline=False)

        makeGraph(final, data_dict['time'])

        return embedVar

    embedVar.add_field(name="ERROR", value="INVALID FIELD", inline=False)
    embedVar.color = 0xff0000
    return embedVar


@csgoBot.event
async def on_ready():  # Prints when csgoBot is up and running.
    print(csgoBot.guilds[0].name)
    print(f'{csgoBot.user} has connected to Discord!')


@csgoBot.event
async def on_member_join(member):  # Prints when user leaves server
    print(f'{member} has joined {csgoBot.guilds[0].name}')


@csgoBot.command()
async def ping(ctx):
    await ctx.send(
        f'{ctx.author.name} has a ping of: {round(csgoBot.latency * 1000)}ms')
    await ctx.send(ctx)


@csgoBot.command()
async def weapon(ctx, weapon_name, skin, condition, currency):
    data = getWeaponInfo(weapon_name, skin, condition, currency)

    if data.color == GREEN:
        print('yee')
        f = discord.File(
            os.getcwd() + "\\graph.png",
            filename="graph.png")

        data.set_image(url="attachment://graph.png")

        await ctx.send(file=f, embed=data)
        os.remove("graph.png")
    else:
        print('wrong branch')
        await ctx.send(embed=data)


csgoBot.run(TOKEN)
