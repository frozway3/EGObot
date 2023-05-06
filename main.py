import discord
from discord.ext import commands
import json
import requests
import random
import tasks
import asyncio
import os
import aiohttp
import sys
import time
import datetime
import aeval
import pyautogui
import math

bot = discord.Bot(help_command=None)
TOKEN = 'MTA5NjgwMDAyMDU5MTgxNjczNA.GVvXp1.ZJELr1QYcjK-1bYP3o36ItMbEIJdn4M_0sTqDU'
times_used = 0


class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Quality"))
        self.add_item(discord.ui.InputText(label="Level link or level id"))
        self.add_item(discord.ui.InputText(label="Texture pack link"))
        self.add_item(discord.ui.InputText(label="Texture pack image link"))
        self.add_item(discord.ui.InputText(label="Icon kit image link"))
        #self.add_item(discord.ui.InputText(label="Wishes"))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="NEW REQUEST")
        embed.add_field(name="Quality", value=self.children[0].value)
        embed.add_field(name="Level", value=self.children[1].value)
        embed.add_field(name="TP", value=self.children[2].value)
        embed.add_field(name="TP image link", value=self.children[3].value)
        embed.add_field(name="IK image link", value=self.children[4].value)
        #embed.add_field(name="Wishes", value=self.children[5].value)
        await interaction.response.send_message(embeds=[embed])


class MyView(discord.ui.View):
    @discord.ui.button(label="Send request")
    async def button_callback(self,  button, interaction):
        await interaction.response.send_modal(MyModal(title="SHOWCASING FORM"))


class MyView1(discord.ui.View):
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.success)
    async def button_callback(self, interaction, button):
        await interaction.response.send_message("You clicked the button!")


class MyView2(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder="Choose a showcaser!", # the placeholder text that will be displayed if nothing is selected
        min_values=1, # the minimum number of values that must be selected by the users
        max_values=1, # the maximum number of values that can be selected by the users
        options=[ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Akeno",
                description="Pick this if you want fuck xWounDx"
            ),
            discord.SelectOption(
                label="mn02",
                description="Pick this if you like big black cocks"
            ),
            discord.SelectOption(
                label="pealko",
                description="Pick this if you clever"
            )
        ]
    )
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")


@bot.event
async def on_ready():
    print(f'ready as {bot.user.name}')

@bot.slash_command()
async def ping(ctx):
    await ctx.respond(f'Ping time is {bot.latency}')


@bot.slash_command()
async def sendreq(ctx, user_id, *, msg):
    user = bot.fetch_user(user_id)
    try:
        await bot.create_dm(user).send(msg)
    except Exception as e:
        await ctx.send(f'Error: {e}')

@bot.slash_command()
async def choose_showcaser(ctx):
    await ctx.send("Choose a chowcaser", view=MyView2())

@bot.slash_command()
async def button(ctx):
    await ctx.send("This is a button!", view=MyView1())

@bot.slash_command(name='rec')
async def form(ctx):
    await ctx.send(view=MyView())

def minify_text(txt: str):
    if len(str(txt)) >= 1024:
        return f'''{str(txt)[:-900]}...
        ...и ещё {len(str(txt).replace(str(txt)[:-900], ""))} символов...'''
    else:
        return str(txt) # Захотелось использовать лямбду и всё в одну строку... но решил хоть как-то сделать читабельней

@bot.slash_command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}')

@bot.slash_command()
@commands.has_role('Admin')
async def ban(ctx, member: discord.Member, *, reason = None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} was banned')

@bot.slash_command()
async def help(ctx):
    global times_used
    times_used += 1
    await ctx.send(
        'prefix - /\n'
        'choose_showcaser - choose showcaser\n'
        'button - press button\n'
        'form - give form\n'
        'hello - send hello message\n'
        'ban - ban(onlyadmins)\n'
        'eval *args - execute code\n'
        'help1 - get help\n'
        f'"Help" command used {times_used} times'
    )

@bot.slash_command(name='eval')
@commands.has_role('Admin')
async def __eval(ctx, *, content):
    #if ctx.author.id not in bot.owner_ids: return await ctx.send("Кыш!") # Защита от os.system('format C') :)
    # Проверка на то, записан ли код в Markdown'овском блоке кода и его "очистка":
    code = "\n".join(content.split("\n")[1:])[:-3] if content.startswith("```") and content.endswith("```") else content
    standart_args = { # Стандартные библиотеки и переменные, которые будут определены в коде. Для удобства. Кстати, я уже добавил несколько встроенных либ и переменных из d.py
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "tasks": tasks,
        "ctx": ctx,
        "asyncio": asyncio,
        "aiohttp": aiohttp,
        #"os": os,
        'sys': sys,
        "time": time,
        "datetime": datetime,
        "random": random,
        "requests": requests,
        "pyautogui": pyautogui,
        "math": math
    }
    start = time.time() # запись стартового таймстампа для расчёта времени выполнения
    try:
        r = await aeval.aeval(f"""{code}""", standart_args, {}) # выполняем код
        ended = time.time() - start # рассчитываем конец выполнения
        print(r)
        if not code.startswith('#nooutput'): # Если код начинается с #nooutput, то вывода не будет
            embed = discord.Embed(title="Successfully!", description=f"Выполнено за: {math.floor(ended)}", color=0x72F009)
            """
             Есть нюанс: если входные/выходные данные будут длиннее 1024 символов, то эмбед не отправится, а функция выдаст ошибку.
             Именно поэтому сверху стоит print(r), а так же есть функция minify_text, которая
             минифицирует текст для эмбеда во избежание БэдРеквеста (который тут возникает когда слишком много символов). Поставил специально лимит на 900, чтобы точно хватило
            """
            embed.add_field(name=f'Входные данные:', value=f'`{minify_text(code) }`')
            embed.add_field(name=f'Выходные данные:', value=f'`{minify_text(r)}`', inline=False)
            await ctx.send(embed=embed) # Отправка, уиии
    except Exception as e: # Ловим ошибки из строки с выполнением нашего кода (и не только!)
        ended = time.time() - start # Сново считаем время, но на этот раз до ошибки
        if not code.startswith('#nooutput'): # Аналогично коду выше
            code = minify_text(code)
            embed = discord.Embed(title=f"При выполнении возникла ошибка.\nВремя: {math.floor(ended)}", description=f'Ошибка:\n```py\n{e}```', color=0xEC2211)
            embed.add_field(name=f'Входные данные:', value=f'`{minify_text(code)}`', inline=False)
            await ctx.send(embed=embed)
            raise e # Ну и поднимем исключение

bot.run(TOKEN)