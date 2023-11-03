import disnake
from disnake.ext import commands

import mysql.connector as mc
from typing import Optional
# import schedule
import datetime
import random
from colorama import Fore, Style
import os
import sys
from io import StringIO




bot = commands.Bot(command_prefix='!',
                   help_command=None,
                   intents=disnake.Intents.all(),
                   activity=disnake.Game(name="ЭмблаX"))
client = disnake.Client()

create_card_channel = 1150526596604760184
transfer_channel = 1150526686216077475
set_default_channel = 1150526651583709304
balance_channel = 1150526751353622578
fine_channel = 1150526712946372630
start_channel = 1150841304582987869
clan_user_channel = 1165740139771858944

admin_id = 508350823592362014



# conn = mc.connect(host='db.worldhosts.fun',
#                   user='u4980_7K91YKi39n',
#                   password='=dgsI.+5R1!Aal=pozVfwcSD',
#                   db='s4980_BankDB',
#                   port=3306)
# cur = conn.cursor()
# cur.execute("""CREATE TABLE IF NOT EXISTS users(
#     discord_id INTEGER,
#     discord_name INTEGER,
#     username INTEGER,
#     cardname INTEGER,
#     balance INT,
#     carddefault INT);
# """)
# conn.commit()

# def conn_check():
#   if conn.is_connected() == False:
#     conn.close()
#     conn = mc.connect(host='db.worldhosts.fun',
#                   user='u4980_7K91YKi39n',
#                   password='=dgsI.+5R1!Aal=pozVfwcSD',
#                   db='s4980_BankDB',
#                   port=3306)
#     cur = conn.cursor()
#   now = datetime.datetime.now()
#   print(now.strftime("%Y-%m-%d %H:%M") +': ' + 'Connection restarted')

# schedule.every(5).minutes.do(conn_check)


@bot.event
async def on_ready():
  now = datetime.datetime.now()
  print(
      Fore.RED + now.strftime("%Y-%m-%d %H:%M:%S") + ': ' + Fore.GREEN +
      f"Bot {bot.user} is ready to work" + Style.RESET_ALL)
  channel = bot.get_channel(start_channel)  # канал логов
  await channel.send(now.strftime("%Y-%m-%d %H:%M:%S") + ': ' + 'Бот успешно запущен')


@bot.slash_command(name='create_card', description='Создание новой карты')
async def create_card(inter,
                      user=commands.Param(description='Ник в Minecraft'),
                      cardname=commands.Param(description='Название карты')):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"""SELECT use_all FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
    use_all = cur.fetchone()

  except mc.Error as e:
     await inter.send(f'** Error: ** {e}')

  if use_all == None:
    use_all = 'True'
     
  if 'True' in use_all:
    try:
        cur.execute(
                f"""SELECT count(*) FROM users WHERE username = '{user}' AND discord_id = '{inter.author.id}'"""
        )
        default = int(cur.fetchone()[0])
    except mc.Error as e:
           await inter.send(f'** Error: ** {e}')

    if default >= 1:
        try:
            cur.execute(f"""INSERT INTO users
                                (discord_id, discord_name, username, cardname, balance, carddefault, use_all, clancard)
                                VALUES
                                ('{inter.author.id}', '{inter.author.name}', '{user}', '{cardname}', '0', 'False', 'True', 'null')"""
                        )
        except mc.Error as e:
            await inter.send(f'** Error: ** {e}')
    else:
        try:
            cur.execute(f"""INSERT INTO users
                                (discord_id, discord_name, username, cardname, balance, carddefault, use_all, clancard)
                                VALUES
                                ('{inter.author.id}', '{inter.author.name}', '{user}', '{cardname}', '0', 'True', 'True', 'null')"""
                        )
        except mc.Error as e:
            await inter.send(f'** Error: ** {e}')

    conn.commit()
    channel = bot.get_channel(create_card_channel)  # канал логов

    embed_admin = disnake.Embed(
        title="Информация для администрации",
        colour=0xf20000,
    )
    embed_admin.add_field(name='Действие: ',
                            value='Создание карты',
                            inline=False)
    embed_admin.add_field(name='', value='', inline=False)
    embed_admin.add_field(name='Disocrd ID: ',
                            value=f'{inter.author.id}',
                            inline=False)
    embed_admin.add_field(name='Discord UserName: ',
                            value=f'{inter.author.name}',
                            inline=False)
    embed_admin.add_field(name='Ник в Minecraft: ',
                            value=f'{user}',
                            inline=False)
    embed_admin.add_field(name='Название карты: ',
                            value=f'{cardname}',
                            inline=False)
    await channel.send(embed=embed_admin)

    await inter.send(
        f'Карта для игрока {user} с именем {cardname} была успешно создана')
    cur.close()
    conn.close()

  else: 
    await inter.send('Ваш баланс отрицательный!\nНекоторые функции заблокированы')

# class Confirm(disnake.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)
#         self.value = Optional[bool]

#     @disnake.ui.Button(label='Принять', style=disnake.ButtonStyle.gray, emoji='✅')
#     async def confirm(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
#         await inter.send('Перевод принят')
#         self.value = True
#         self.stop()
#     @disnake.ui.Button(label='Отклонить', style=disnake.ButtonStyle.gray, emoji='❌')
#     async def cancel(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
#         await inter.send('Перевод отклонен')
#         self.value = False
#         self.stop()

#     @bot.command(
#         name='transfer_accept',
#     )
#     async def transfer_accept(inter):
#         view = Confirm()
#         await inter.


#----CARDS----#
@bot.slash_command(name='cards', description='Список карт и их баланс')
async def cards(inter):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND carddefault = 'True'""")
    balance_carddefault = int(cur.fetchone()[0])
  except mc.Error as e:
     await inter.send(f'** Error: ** {e}')

  if balance_carddefault >= 0:
    try:
        cur.execute(f"""UPDATE users SET use_all = 'True' WHERE discord_id = '{inter.author.id}'""")
        conn.commit()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')
    try:
        cur.execute(
            f"""SELECT cardname FROM users WHERE discord_id = '{inter.author.id}'""")
        result = cur.fetchall()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')
  embed = disnake.Embed(
      title="Информация",
      colour=0xe60082,
  )
  embed.add_field(name='Карта', value='', inline=True)
  embed.add_field(name='Баланс', value='')
  embed.add_field(name='Карта по умолчанию', value='')
  embed.add_field(name='', value='', inline=False)
  for row in result:
    fmt = "{0}"
    try:
        cur.execute(
            f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{fmt.format(*row)}'"""
        )
        balance = cur.fetchone()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')
    try:
        cur.execute(
            f"""SELECT carddefault FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{fmt.format(*row)}'"""
        )
        carddefault = cur.fetchone()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')
    embed.add_field(name=fmt.format(*row), value='', inline=True)
    embed.add_field(name=f'{fmt.format(*balance)} АР', value='')
    embed.add_field(name=fmt.format(*carddefault), value='')
    embed.add_field(name='', value='', inline=False)

  await inter.send(embed=embed)
  cur.close()
  conn.close()


#----TRANSFER----#
@bot.slash_command(name='transfer',
                   description='Денежный перевод другому игроку')
async def transfer(
    inter,
    user=commands.Param(description='Ник кому хотите перевести деньги'),
    cardname=commands.Param(description='Карта с которой списать деньги'),
    count: int = commands.Param(description='Сумма перевода', min_value=1),
    descrition=commands.Param(description='Сообщение')):

  await inter.response.defer()

  
  try:
    cur.execute(f"""SELECT use_all FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
    use_all = cur.fetchone()[0]
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')

  if use_all == 'True':
    try:
        cur.execute(
            f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1"""
        )
        user_send = cur.fetchone()[0]

        cur.execute(
                f"""SELECT clan_cardname FROM clans WHERE clan_cardname = '{cardname}'"""
            )
        sender = cur.fetchone()
        if sender == None:
            cur.execute(
                f"""SELECT cardname FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1"""
            )
            sender = cur.fetchone()
            if sender != None:
                user_sender_type = 'user'
            else:
                await inter.send('Карта не найдена')
        else:
            user_sender_type = 'clan'

        cur.execute(
            f"""SELECT username FROM users WHERE username = '{user}' LIMIT 0, 1"""
        )
        recipient = cur.fetchone()
        if recipient == None:
            cur.execute(
                f"""SELECT clan_cardname FROM clans WHERE clan_cardname = '{user}'"""
            )
            recipient = cur.fetchone()
            if recipient != None:
                user_type = 'clan'
            else:
                await inter.send('Игрок не найден')
        else:
            user_type = 'user'

        if user_type == 'user':
            cur.execute(
                f"""SELECT discord_id FROM users WHERE username = '{user}' LIMIT 0, 1""")
        elif user_type == 'clan':
            cur.execute(
                f"""SELECT discord_id_author FROM clans WHERE clan_cardname = '{user}' LIMIT 0, 1""")
        user_recipient_id = cur.fetchone()[0]

        if user_sender_type == 'user':
            cur.execute(
                f"""SELECT balance FROM users WHERE username = '{user_send}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}' LIMIT 0, 1"""
            )
        elif user_sender_type == 'clan':
            cur.execute(
                f"""SELECT balance FROM clans WHERE clan_cardname = '{cardname}' LIMIT 0, 1"""
            )
        balance_sender = int(cur.fetchone()[0])
        old_balance_sender = balance_sender
        if user_type == 'user':
            cur.execute(
                f"""SELECT balance FROM users WHERE username = '{user}' AND carddefault = 'True' LIMIT 0, 1"""
            )
        elif user_type == 'clan':
            cur.execute(
                f"""SELECT balance FROM clans WHERE clan_cardname = '{user}' LIMIT 0, 1"""
            )
        balance_recipient = int(cur.fetchone()[0])
        old_balance_recipient = balance_recipient
        if user_sender_type == 'user':
            if user_send == user:
                await inter.send('Перевод на свой счет запрещен')
            
            else:
                if balance_sender - count >= 0:
                    balance_sender = balance_sender - count
                    balance_recipient = balance_recipient + count
                    if user_sender_type == 'user':
                        cur.execute(f"""UPDATE users 
                                        SET balance = {balance_sender}
                                        WHERE username = '{user_send}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}'"""
                                    )
                    elif user_sender_type == 'clan':
                                            cur.execute(f"""UPDATE clans 
                                        SET balance = {balance_sender}
                                        WHERE clan_cardname = '{user}'""")
                    conn.commit()
                    if user_type == 'user':
                        cur.execute(f"""UPDATE users 
                                        SET balance = {balance_recipient}
                                        WHERE username = '{user}' AND carddefault = 'True'""")
                    elif user_type == 'clan':
                        cur.execute(f"""UPDATE clans 
                                        SET balance = {balance_recipient}
                                        WHERE clan_cardname = '{user}'""")
                    conn.commit()
                    embed = disnake.Embed(
                        title="Информация о переводе",
                        colour=0xe60082,
                    )
                    embed.add_field(name='От кого: ', value=f'{user_send}', inline=False)
                    embed.add_field(name='Кому: ', value=f'{user}', inline=False)
                    embed.add_field(name='Карта: ', value=f'{cardname}', inline=False)
                    embed.add_field(name='Старый баланс: ',
                                    value=f'{old_balance_sender} АР',
                                    inline=False)
                    embed.add_field(name='Новый баланс: ',
                                    value=f'{balance_sender} АР',
                                    inline=False)
                    embed.add_field(name='Сумма перевода: ',
                                    value=f'{count} АР',
                                    inline=False)
                    embed.add_field(name='Сообщение: ', value=descrition, inline=False)

                    await inter.send(embed=embed)

                    channel = bot.get_channel(transfer_channel)  # канал логов

                    embed_admin = disnake.Embed(
                        title="Информация для администрации",
                        colour=0xf20000,
                    )
                    embed_admin.add_field(name='Действие: ', value='Перевод', inline=False)
                    embed_admin.add_field(name='От кого: ',
                                            value=f'{user_send}',
                                            inline=False)
                    embed_admin.add_field(name='Кому: ', value=f'{user}', inline=False)
                    embed_admin.add_field(name='Карта: ', value=f'{cardname}', inline=False)
                    embed_admin.add_field(name='Старый баланс отправителя: ',
                                            value=f'{old_balance_sender} АР',
                                            inline=False)
                    embed_admin.add_field(name='Новый баланс отправителя: ',
                                            value=f'{balance_sender} АР',
                                            inline=False)
                    embed_admin.add_field(name='Сумма перевода: ',
                                            value=f'{count} АР',
                                            inline=False)
                    embed_admin.add_field(name='Старый баланс получателя: ',
                                            value=f'{old_balance_recipient} АР',
                                            inline=False)
                    embed_admin.add_field(name='Новый баланс получателя: ',
                                            value=f'{balance_recipient} АР',
                                            inline=False)
                    embed_admin.add_field(name='Сообщение: ', value=descrition, inline=False)
                    await channel.send(embed=embed_admin)

                    embed_recipient = disnake.Embed(
                        title="Пополнение счета",
                        colour=0xe60082,
                    )

                    embed_recipient.add_field(name='Действие: ',
                                                value='Перевод',
                                                inline=False)
                    embed_recipient.add_field(name='От кого: ',
                                                value=f'{user_send}',
                                                inline=False)
                    embed_admin.add_field(name='Кому: ', value=f'{user}', inline=False)
                    embed_recipient.add_field(name='Карта: ',
                                                value='Зачислено на карту по умолчанию',
                                                inline=False)
                    embed_recipient.add_field(name='Старый баланс: ',
                                                value=f'{old_balance_recipient} АР',
                                                inline=False)
                    embed_recipient.add_field(name='Новый баланс: ',
                                                value=f'{balance_recipient} АР',
                                                inline=False)
                    embed_recipient.add_field(name='Сумма перевода: ',
                                                value=f'{count} АР',
                                                inline=False)
                    embed_recipient.add_field(name='Сообщение: ',
                                                value=descrition,
                                                inline=False)

                    user_recipient = await bot.fetch_user(user_recipient_id)

                    if balance_recipient >= 0:
                            cur.execute(f"""UPDATE users SET use_all = 'True' WHERE discord_id = '{user_recipient_id}'""")
                            conn.commit()
                    await user_recipient.send(embed=embed_recipient)

                else:
                    await inter.send('Недостаточно средств')
                    cur.close()
                    conn.close()

        else:
            if balance_sender - count >= 0:
                balance_sender = balance_sender - count
                balance_recipient = balance_recipient + count
                if user_sender_type == 'user':
                    cur.execute(f"""UPDATE users 
                                    SET balance = {balance_sender}
                                    WHERE username = '{user_send}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}'"""
                                )
                elif user_sender_type == 'clan':
                    cur.execute(f"""UPDATE clans 
                                    SET balance = {balance_sender}
                                    WHERE clan_cardname = '{cardname}'""")
                conn.commit()
                if user_type == 'user':
                    cur.execute(f"""UPDATE users 
                                    SET balance = {balance_recipient}
                                    WHERE username = '{user}' AND carddefault = 'True'""")
                elif user_type == 'clan':
                    cur.execute(f"""UPDATE clans 
                                    SET balance = {balance_recipient}
                                    WHERE clan_cardname = '{user}'""")
                conn.commit()
                embed = disnake.Embed(
                    title="Информация о переводе",
                    colour=0xe60082,
                )
                embed.add_field(name='От кого: ', value=f'{user_send}', inline=False)
                embed.add_field(name='Кому: ', value=f'{user}', inline=False)
                embed.add_field(name='Карта: ', value=f'{cardname}', inline=False)
                embed.add_field(name='Старый баланс: ',
                                value=f'{old_balance_sender} АР',
                                inline=False)
                embed.add_field(name='Новый баланс: ',
                                value=f'{balance_sender} АР',
                                inline=False)
                embed.add_field(name='Сумма перевода: ',
                                value=f'{count} АР',
                                inline=False)
                embed.add_field(name='Сообщение: ', value=descrition, inline=False)

                await inter.send(embed=embed)

                channel = bot.get_channel(transfer_channel)  # канал логов

                embed_admin = disnake.Embed(
                    title="Информация для администрации",
                    colour=0xf20000,
                )
                embed_admin.add_field(name='Действие: ', value='Перевод', inline=False)
                embed_admin.add_field(name='От кого: ',
                                        value=f'{user_send}',
                                        inline=False)
                embed_admin.add_field(name='Кому: ', value=f'{user}', inline=False)
                embed_admin.add_field(name='Карта: ', value=f'{cardname}', inline=False)
                embed_admin.add_field(name='Старый баланс отправителя: ',
                                        value=f'{old_balance_sender} АР',
                                        inline=False)
                embed_admin.add_field(name='Новый баланс отправителя: ',
                                        value=f'{balance_sender} АР',
                                        inline=False)
                embed_admin.add_field(name='Сумма перевода: ',
                                        value=f'{count} АР',
                                        inline=False)
                embed_admin.add_field(name='Старый баланс получателя: ',
                                        value=f'{old_balance_recipient} АР',
                                        inline=False)
                embed_admin.add_field(name='Новый баланс получателя: ',
                                        value=f'{balance_recipient} АР',
                                        inline=False)
                embed_admin.add_field(name='Сообщение: ', value=descrition, inline=False)
                await channel.send(embed=embed_admin)
                if user_type == 'user':
                    embed_recipient = disnake.Embed(
                        title="Пополнение счета",
                        colour=0xe60082,
                    )
                else:
                    embed_recipient = disnake.Embed(
                        title="Пополнение карты клана",
                        colour=0xe60082,
                    )

                embed_recipient.add_field(name='Действие: ',
                                            value='Перевод',
                                            inline=False)
                embed_recipient.add_field(name='От кого: ',
                                            value=f'{user_send}',
                                            inline=False)
                embed_admin.add_field(name='Кому: ', value=f'{user}', inline=False)
                if user_type == 'user':
                    embed_recipient.add_field(name='Карта: ',
                                                value='Зачислено на карту по умолчанию',
                                                inline=False)
                embed_recipient.add_field(name='Старый баланс: ',
                                            value=f'{old_balance_recipient} АР',
                                            inline=False)
                embed_recipient.add_field(name='Новый баланс: ',
                                            value=f'{balance_recipient} АР',
                                            inline=False)
                embed_recipient.add_field(name='Сумма перевода: ',
                                            value=f'{count} АР',
                                            inline=False)
                embed_recipient.add_field(name='Сообщение: ',
                                            value=descrition,
                                            inline=False)

                user_recipient = await bot.fetch_user(user_recipient_id)

                if balance_recipient >= 0:
                        cur.execute(f"""UPDATE users SET use_all = 'True' WHERE discord_id = '{user_recipient_id}'""")
                        conn.commit()
                await user_recipient.send(embed=embed_recipient)

            else:
                await inter.send('Недостаточно средств')
                cur.close()
                conn.close()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')
  else:
    await inter.send('Ваш баланс отрицательный!\nНекоторые функции заблокированы')


#----SWAP----#
@bot.slash_command(name='swap', description='Перевод между счетами')
async def swap(inter,
               card_1=commands.Param(description='Первый счет'),
               card_2=commands.Param(description='Второй счет'),
               count: int = commands.Param(description='Сумма перевода',
                                           min_value=1)):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()

  try:
    if card_1 == 'government' or card_2 == 'government':
        cur.execute("""SELECT discord_id FROM government""")
        users = cur.fetchall()
        users = [int(row[0]) for row in users] 
        if inter.author.id in users:
            cur.execute("SELECT balance FROM government LIMIT 0, 1")
            government_balance = int(cur.fetchone()[0])
        else:
            await inter.send('У вас нет доступа к государственной карте')
            return

    cur.execute(
        f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{card_1}'"""
    )
    first_balance = cur.fetchone()
    if first_balance != None:
        first_balance = int(first_balance[0])
        old_first_balance = first_balance

    cur.execute(
        f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{card_2}'"""
    )
    second_balance = cur.fetchone()
    if second_balance != None:
        second_balance = int(second_balance[0])
        old_second_balance = second_balance

    if card_1 == 'government':
        first_balance = government_balance
        old_first_balance = first_balance
    elif card_2 == 'government':
        second_balance = government_balance
        old_second_balance = second_balance
    

    cur.execute(
        f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1"""
    )
    username = cur.fetchone()
    if username != None:
        username = username[0]

    if first_balance - count >= 0:
        first_balance = first_balance - count
        second_balance = second_balance + count
        if card_1 != 'government':
            cur.execute(f"""UPDATE users 
                            SET balance = {first_balance}
                            WHERE discord_id = '{inter.author.id}' AND cardname = '{card_1}'"""
                        )
        elif card_1 == 'government':
            cur.execute(f"""UPDATE government 
                            SET balance = {first_balance}
                        """)
        
        if card_2 != 'government':
            cur.execute(f"""UPDATE users 
                            SET balance = {second_balance}
                            WHERE discord_id = '{inter.author.id}' AND cardname = '{card_2}'"""
                        )
        elif card_2 == 'government':
            cur.execute(f"""UPDATE government 
                            SET balance = {second_balance}
                        """)
        conn.commit()
        embed = disnake.Embed(
            title="Информация",
            colour=0xe60082,
        )
        embed.add_field(name='Действие: ',
                        value='Перевод между счетами',
                        inline=False)
        embed.add_field(name='Первая карта: ', value=card_1, inline=False)
        embed.add_field(name='Старый баланс: ',
                        value=f'{old_first_balance} АР',
                        inline=False)
        embed.add_field(name='Новый баланс: ',
                        value=f'{first_balance} АР',
                        inline=False)
        embed.add_field(name='Сумма перевода: ', value=f'{count} АР', inline=False)
        embed.add_field(name='Вторая карта: ', value=card_2, inline=False)
        embed.add_field(name='Старый баланс: ',
                        value=f'{old_second_balance} АР',
                        inline=False)
        embed.add_field(name='Новый баланс: ',
                        value=f'{second_balance} АР',
                        inline=False)
        await inter.send(embed=embed)

        embed_admin = disnake.Embed(
            title="Информация для администрации",
            colour=0xf20000,
        )
        embed_admin.add_field(name='Игрок: ', value=username)
        embed_admin.add_field(name='Действие: ',
                            value='Перевод между счетами',
                            inline=False)
        embed_admin.add_field(name='Первая карта: ', value=card_1, inline=False)
        embed_admin.add_field(name='Старый баланс: ',
                            value=f'{old_first_balance} АР',
                            inline=False)
        embed_admin.add_field(name='Новый баланс: ',
                            value=f'{first_balance} АР',
                            inline=False)
        embed_admin.add_field(name='Сумма перевода: ',
                            value=f'{count} АР',
                            inline=False)
        embed_admin.add_field(name='Вторая карта: ', value=card_2, inline=False)
        embed_admin.add_field(name='Старый баланс: ',
                            value=f'{old_second_balance} АР',
                            inline=False)
        embed_admin.add_field(name='Новый баланс: ',
                            value=f'{second_balance} АР',
                            inline=False)

        channel = bot.get_channel(transfer_channel)  # канал логов

        await channel.send(embed=embed_admin)
    else:
        await inter.send('Недостаточно средств')
    cur.close()
    conn.close()
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----SET_DEFAULT----#
@bot.slash_command(name='set_default',
                   description='Изменить карту по умолчанию')
async def set_default(
    inter,
    card=commands.Param(
        description='Название карты, которую хотите сделать картой по умолчанию'
    )):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"""SELECT use_all FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
    use_all = cur.fetchone()[0]

    if use_all == 'True':
        cur.execute(
            f"""SELECT cardname FROM users WHERE discord_id = '{inter.author.id}' AND carddefault = 'True'"""
        )
        old_default = cur.fetchone()[0]

        cur.execute(f"""UPDATE users 
                        SET carddefault = 'False'
                        WHERE cardname = '{old_default}' AND discord_id = '{inter.author.id}'
                        """)
        cur.execute(f"""UPDATE users 
                        SET carddefault = 'True'
                        WHERE cardname = '{card}' AND discord_id = '{inter.author.id}'
                        """)

        cur.execute(
            f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1"""
        )
        username = cur.fetchone()[0]

        conn.commit()

        embed = disnake.Embed(
            title="Информация",
            colour=0xe60082,
        )
        embed.add_field(name='Действие: ',
                        value='Изменение карты по умолчанию',
                        inline=False)
        embed.add_field(name='Старая карта: ', value=old_default, inline=False)
        embed.add_field(name='Новый карта: ', value=card, inline=False)

        await inter.send(embed=embed)

        embed_admin = disnake.Embed(
            title="Информация для администрации",
            colour=0xf20000,
        )
        embed_admin.add_field(name='Игрок: ', value=username)
        embed_admin.add_field(name='Действие: ',
                                value='Изменение карты по умолчанию',
                                inline=False)
        embed_admin.add_field(name='Старая карта: ', value=old_default, inline=False)
        embed_admin.add_field(name='Новый карта: ', value=card, inline=False)

        channel = bot.get_channel(set_default_channel)  # канал логов

        await channel.send(embed=embed_admin)
        cur.close()
        conn.close()
    else:
        await inter.send('Ваш баланс отрицательный!\nНекоторые функции заблокированы')
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')



#----FINES----#
@bot.slash_command(
    name='fines',
    description='Посмотреть список штрафов'
)
async def fines(inter):
  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(
        f"""SELECT description FROM fines WHERE discord_id = '{inter.author.id}'""")
    result = cur.fetchall()
    embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
    )
    embed.add_field(name='Описание', value='', inline=True)
    embed.add_field(name='Сумма штрафа', value='')
    embed.add_field(name='ID', value='')
    embed.add_field(name='', value='', inline=False)
    for row in result:
        fmt = "{0}"
        cur.execute(
            f"""SELECT count FROM fines WHERE discord_id = '{inter.author.id}' AND description = '{fmt.format(*row)}'"""
        )
        count = cur.fetchone()
        cur.execute(
            f"""SELECT id FROM fines WHERE discord_id = '{inter.author.id}' AND description = '{fmt.format(*row)}'"""
        )
        id = cur.fetchone()[0]
        embed.add_field(name=fmt.format(*row), value='', inline=True)
        embed.add_field(name=f'{fmt.format(*count)} АР', value='')
        embed.add_field(name=id, value='')
        embed.add_field(name='', value='', inline=False)

    await inter.send(embed=embed)
    cur.close()
    conn.close()
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----PAY----#
@bot.slash_command(
    name='pay',
    description='Оплатить штраф'
)
async def pay(inter, id: int = commands.Param(description='ID штрафа', min_value = 10, max_value = 99), count: int = commands.Param(description='Сколько хотиите оплатить', min_value = 1), cardname = commands.Param(description='Карта с которой хотите произвести оплату')):
  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{cardname}'""")
    balance = int(cur.fetchone()[0])
    cur.execute(f"""SELECT count FROM fines WHERE discord_id = '{inter.author.id}' AND id = '{id}'""")
    count_fine = int(cur.fetchone()[0])

    if count_fine < count:
        count = count_fine
        
    old_balance = balance

    if count_fine - count <= 0:
        if balance - count > 0:
            balance = balance - count
            cur.execute("""SELECT balance FROM government LIMIT 1""")
            gov_balance = int(cur.fetchone()[0])
            gov_balance = gov_balance + count
        cur.execute(f"""DELETE FROM fines WHERE discord_id = '{inter.author.id}' AND id = {id}""")
        cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{inter.author.id}' AND cardname = '{cardname}'""")
        cur.execute(f"""UPDATE government SET balance = {gov_balance}""")
        conn.commit()

        embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
        )
        embed.add_field(name='Действие: ', value='Оплата штрафа', inline=False)
        embed.add_field(name='Сумма штрафа', value=f'{count_fine}', inline=False)
        embed.add_field(name='Оплачено: ', value=f'{count}', inline=False)
        embed.add_field(name='Карта: ', value=cardname, inline=False)
        embed.add_field(name='Старый баланс: ',
                            value=f'{old_balance} АР',
                            inline=False)
        embed.add_field(name='Новый баланс: ',
                            value=f'{balance} АР',
                            inline=False)
        embed.add_field(name='ID', value=id, inline=False)
        await inter.send(embed=embed)

        cur.execute(f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
        username = cur.fetchone()[0]

        embed_admin = disnake.Embed(
        title="Информация для администрации",
        colour=0xf20000,
        )
        embed_admin.add_field(name='Игрок: ', value=username, inline=False)
        embed_admin.add_field(name='Действие: ', value='Оплата штрафа', inline=False)
        embed_admin.add_field(name='Сумма штрафа', value=f'{count_fine}', inline=False)
        embed_admin.add_field(name='Оплачено: ', value=f'{count}', inline=False)
        embed_admin.add_field(name='Карта: ', value=cardname, inline=False)
        embed_admin.add_field(name='Старый баланс: ',
                            value=f'{old_balance} АР',
                            inline=False)
        embed_admin.add_field(name='Новый баланс: ',
                            value=f'{balance} АР',
                            inline=False)
        embed_admin.add_field(name='ID', value=id, inline=False)

        channel = bot.get_channel(fine_channel)  # канал логов

        await channel.send(embed=embed_admin)


    else:
        balance = balance - count
        cur.execute("""SELECT balance FROM government LIMIT 1""")
        gov_balance = int(cur.fetchone()[0])
        gov_balance = gov_balance + count

        cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{inter.author.id}' AND cardname = '{cardname}'""")
        cur.execute(f"""UPDATE fines SET count = {count_fine-count} WHERE discord_id = '{inter.author.id}' AND id = '{id}'""")
        cur.execute(f"""UPDATE government SET balance = {gov_balance}""")
        conn.commit()


        embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
        )
        embed.add_field(name='Действие: ', value='Оплата штрафа', inline=False)
        embed.add_field(name='Сумма штрафа', value=f'{count_fine}', inline=False)
        embed.add_field(name='Оплачено: ', value=f'{count}', inline=False)
        embed.add_field(name='Карта: ', value=cardname, inline=False)
        embed.add_field(name='Старый баланс: ',
                            value=f'{old_balance} АР',
                            inline=False)
        embed.add_field(name='Новый баланс: ',
                            value=f'{balance} АР',
                            inline=False)
        embed.add_field(name='ID', value=id, inline=False)
        await inter.send(embed=embed)

        cur.execute(f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
        username = cur.fetchone()[0]

        embed_admin = disnake.Embed(
        title="Информация для администрации",
        colour=0xf20000,
        )
        embed_admin.add_field(name='Игрок: ', value=username, inline=False)
        embed_admin.add_field(name='Действие: ', value='Оплата штрафа', inline=False)
        embed_admin.add_field(name='Сумма штрафа', value=f'{count_fine}', inline=False)
        embed_admin.add_field(name='Оплачено: ', value=f'{count}', inline=False)
        embed_admin.add_field(name='Карта: ', value=cardname, inline=False)
        embed_admin.add_field(name='Старый баланс: ',
                            value=f'{old_balance} АР',
                            inline=False)
        embed_admin.add_field(name='Новый баланс: ',
                            value=f'{balance} АР',
                            inline=False)
        embed_admin.add_field(name='ID', value=id, inline=False)

        channel = bot.get_channel(fine_channel)  # канал логов

        await channel.send(embed=embed_admin)
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')



#-----STATS-----#
@bot.slash_command(
        name='stats',
        description='Выводит топ игроков по балансу'
        )
async def stats(inter):
    conn = mc.connect(
        host='db.worldhosts.fun',  # создание курсора
        user='u4980_7K91YKi39n',
        password='=dgsI.+5R1!Aal=pozVfwcSD',
        db='s4980_BankDB',
        port=3306)
    cur = conn.cursor()
    try:
        cur.execute("""SELECT username, balance FROM users ORDER BY users.balance DESC LIMIT 3""")
        result = cur.fetchall()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')

    embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
    )
    embed.add_field(name='Игрок', value='', inline=True)
    embed.add_field(name='Баланс', value='')
    embed.add_field(name='', value='', inline=False)
    for rows in result:
        username = rows[0]
        if '_' in username:
            username = '\\'+username
        embed.add_field(name=username, value='', inline=True)
        embed.add_field(name=rows[1], value='', inline=False)
    await inter.send(embed=embed)
    cur.close()
    conn.close()

#----CLANCARD_CREATE----#
@bot.slash_command(name='clancard_create', description='Создание карты для клана')
async def clancard_create(inter, cardname = commands.Param(description='Название карты')):
    conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
    cur = conn.cursor()

    await inter.response.defer()

    try:
        cur.execute(f"""SELECT clancard FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
        clancard = cur.fetchone()[0]
        if clancard == 'null':
            cur.execute(f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
            username = cur.fetchone()[0]

            cur.execute(f"""UPDATE users SET clancard = '{cardname}' WHERE discord_id = '{inter.author.id}'""")
            cur.execute(f"""INSERT INTO clans
                                    (discord_id_author, username_author, clan_cardname, balance)
                                    VALUES
                                    ('{inter.author.id}', '{username}', '{cardname}', 0)""")
            conn.commit()
            channel = bot.get_channel(create_card_channel)  # канал логов
            embed_admin = disnake.Embed(
                title="Информация для администрации",
                colour=0xf20000,
            )
            embed_admin.add_field(name='Действие: ',
                                    value='Создание карты клана',
                                    inline=False)
            embed_admin.add_field(name='', value='', inline=False)
            embed_admin.add_field(name='Disocrd ID: ',
                                    value=f'{inter.author.id}',
                                    inline=False)
            embed_admin.add_field(name='Discord UserName: ',
                                    value=f'{inter.author.name}',
                                    inline=False)
            embed_admin.add_field(name='Ник в Minecraft: ',
                                    value=f'{username}',
                                    inline=False)
            embed_admin.add_field(name='Название карты: ',
                                    value=f'{cardname}',
                                    inline=False)
            await channel.send(embed=embed_admin)

            await inter.send(
                f'Карта клана с названием {cardname} была успешно создана')
        else:
            await inter.send('Карта клана уже есть')
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')

    
    cur.close()
    conn.close()


#----CLAN_ADD----#
@bot.slash_command(name='clan_add', description='Дать доступ другому игроку к карте')
async def clan_add(inter, username = commands.Param(description='Ник игрока которого хотите добавить')):
    conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
    cur = conn.cursor()

    await inter.response.defer()

    try:
        cur.execute(f"""SELECT clancard FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
        clancard = cur.fetchone()[0]
        if clancard == 'null':
            await inter.send('У вас нет карты клана')
        else:
            cur.execute(f"""SELECT clancard FROM users WHERE username = '{username}' LIMIT 0, 1""")
            clancard_user = cur.fetchone()[0]
            if clancard_user != 'null':
                await inter.send('У игрока уже есть карта клана')
            else:
                cardname = clancard
                cur.execute(f"""UPDATE users SET clancard = '{cardname}' WHERE username = '{username}'""")
                conn.commit()
                channel = bot.get_channel(clan_user_channel)  # канал логов
                embed_admin = disnake.Embed(
                    title="Информация для администрации",
                    colour=0xf20000,
                )
                embed_admin.add_field(name='Действие: ',
                                        value='Добавление игрока в карту клана',
                                        inline=False)
                embed_admin.add_field(name='', value='', inline=False)
                embed_admin.add_field(name='Добавил: ',
                                        value=inter.author.display_name,
                                        inline=False)
                embed_admin.add_field(name='Кому: ',
                                        value=f'{username}',
                                        inline=False)
                embed_admin.add_field(name='Название карты: ',
                                        value=f'{cardname}',
                                        inline=False)
                await channel.send(embed=embed_admin)

                await inter.send(f'Игроку {username} дан доступ к карте {cardname}')
                
                cur.execute(f"""SELECT discord_id FROM users WHERE username = '{username}' LIMIT 0, 1""")
                user_discord_id = cur.fetchone()[0]
                user = await bot.fetch_user(user_discord_id)
                await user.send(f'Вам был выдан доступ к карте клана {cardname}')
            conn.commit()
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')
    cur.close()
    conn.close()



    #----CLAN_CARD----#
@bot.slash_command(name='clan_card', description='Информация о карте клана')
async def clan_card(inter):
    await inter.response.defer()

    conn = mc.connect(
        host='db.worldhosts.fun',  # создание курсора
        user='u4980_7K91YKi39n',
        password='=dgsI.+5R1!Aal=pozVfwcSD',
        db='s4980_BankDB',
        port=3306)
    cur = conn.cursor()

    try:
        cur.execute(f"""SELECT clancard FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
        clancard = cur.fetchone()[0]
        if clancard == 'null':
            await inter.send('У вас нет карты клана')
        else:
            cur.execute(
                f"""SELECT clancard FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
            clancard = cur.fetchone()[0]

            cur.execute(
                f"""SELECT COUNT(*) FROM users WHERE clancard = '{clancard}'""")
            count = int(cur.fetchone()[0])
            cur.execute(f"""SELECT balance FROM clans WHERE clan_cardname = '{clancard}'""")
            balance = int(cur.fetchone()[0])
    except mc.Error as e:
        await inter.send(f' Error:  {e}')
    embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
    )
    embed.add_field(name='Карта:', value=clancard, inline=True)
    embed.add_field(name='Баланс', value=balance, inline=True)
    embed.add_field(name='', value='', inline=False)
    embed.add_field(name='Игроки', value='', inline=False)


    try:
        cur.execute(
            f"""SELECT username FROM users WHERE clancard = '{clancard}'"""
        )
        users = cur.fetchall()

        embed 
        users_unique = []
        for row in users:
            username = row[0]
            if username not in users_unique:
                users_unique.append(username)

        for username in users_unique:
            embed.add_field(name='', value=username, inline=False)
                

    except mc.Error as e:
        await inter.send(f' Error:  {e}')

    # i = 0
    # print(users[i])
    # while i <= count:
    #     embed.add_field(name=(users[i]), value='', inline=False)
    #     embed.add_field(name='', value='', inline=False)
    #     i = i +1
    await inter.send(embed=embed)
    cur.close()
    conn.close()





















#------------------ADMIN------------------#


#-------BALANCE_SET------#
@bot.slash_command(name='balance_set')
@commands.has_any_role(1147225574499168367)
async def balance_set(inter, user_mc, cardname, balance):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(
        f"""SELECT balance FROM users WHERE username = '{user_mc}' AND cardname = '{cardname}'"""
    )
    old_balance = int(cur.fetchone()[0])

    cur.execute(f"""UPDATE users 
                    SET balance = {balance}
                    WHERE username = '{user_mc}' AND cardname = '{cardname}'""")
    conn.commit()

    embed_admin = disnake.Embed(
        title="Информация для администрации",
        colour=0xf20000,
    )
    embed_admin.add_field(name='Игрок: ', value=user_mc)
    embed_admin.add_field(name='Действие: ',
                            value='Изменение баланса',
                            inline=False)
    embed_admin.add_field(name='Карта: ', value=cardname, inline=False)
    embed_admin.add_field(name='Старый баланс: ',
                            value=f'{old_balance} АР',
                            inline=False)
    embed_admin.add_field(name='Новый баланс: ',
                            value=f'{balance} АР',
                            inline=False)

    channel = bot.get_channel(balance_channel)  # канал логов

    await channel.send(embed=embed_admin)
    await inter.send('Баланс обновлен')
    cur.close()
    conn.close()
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----CARDS-ADMIN----#
@bot.slash_command(name='cards_admin', description='Список карт и их баланс')
@commands.has_any_role(1147225574499168367)
async def cards_admin(inter, username):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"""SELECT cardname FROM users WHERE username = '{username}'""")
    result = cur.fetchall()
    embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
    )
    embed.add_field(name='Карта', value='', inline=True)
    embed.add_field(name='Баланс', value='')
    embed.add_field(name='', value='', inline=False)
    for row in result:
        fmt = "{0}"
        cur.execute(
            f"""SELECT balance FROM users WHERE username = '{username}' AND cardname = '{fmt.format(*row)}'"""
        )
        balance = cur.fetchone()

        cur.execute(
            f"""SELECT carddefault FROM users WHERE username = '{username}' AND cardname = '{fmt.format(*row)}'"""
        )
        carddefault = cur.fetchone()
        embed.add_field(name=fmt.format(*row), value='', inline=True)
        embed.add_field(name=f'{fmt.format(*balance)} АР', value='')
        embed.add_field(name=fmt.format(*carddefault), value='')
        embed.add_field(name='', value='', inline=False)

    await inter.send(embed=embed)
    cur.close()
    conn.close()
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----SQL----#
@bot.slash_command(name='sql_console')
@commands.has_any_role(1147225574499168367)
async def sqlconsole(inter, sqlcommand: str):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"{sqlcommand}")
    conn.commit()
    cur.close()
    conn.close()
    await inter.send(f'Выполнена команда: {sqlcommand}')
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----FINE----#
@bot.slash_command(
  name='fine',
  description='Выписать штраф'
)
@commands.has_any_role(1147225574499168367, 1144692417283506339)
async def fine(inter, 
               username: str = commands.Param(description='Ник на кого будет выписан штраф'), 
               count: int = commands.Param(description='Сумма штрафа', min_value = 1), 
               description: str = commands.Param(description='Описание штрафа'), 
               autopay = commands.Param(description='Настройка авто-оплаты', choices={'True', 'False'})):
  
    await inter.response.defer()

    conn = mc.connect(
        host='db.worldhosts.fun',  # создание курсора
        user='u4980_7K91YKi39n',
        password='=dgsI.+5R1!Aal=pozVfwcSD',
        db='s4980_BankDB',
        port=3306)
    cur = conn.cursor()
    try:
        now = datetime.datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        
        cur.execute(f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")

        username_moder = cur.fetchone()[0]

        cur.execute(f"""SELECT discord_id FROM users WHERE username = '{username}' LIMIT 0, 1""")

        discord_id = cur.fetchone()[0]

        id = random.randint(10,99)

        cur.execute(f"""INSERT INTO fines
                        (discord_id_moder, username_moder, discord_id, username, count, description, autopay, date, id)
                        VALUES
                        ('{inter.author.id}', '{username_moder}', '{discord_id}', '{username}', '{count}', '{description}', '{autopay}', '{formatted_date}', {id})"""
        )
        conn.commit()

        cur.execute(f"""SELECT balance FROM users WHERE discord_id = '{discord_id}' AND carddefault = 'True'""")

        balance = int(cur.fetchone()[0])
        old_balance = balance


        if autopay == 'True':
            balance = balance - count
            cur.execute("""SELECT balance FROM government LIMIT 1""")
            gov_balance = int(cur.fetchone()[0])
            gov_balance = gov_balance + count
            cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{inter.author.id}' AND carddefault = 'True'""")
            cur.execute(f"""UPDATE government SET balance = {gov_balance}""")
            conn.commit()
            if balance < 0:
                cur.execute(f"""UPDATE users SET use_all = 'False' WHERE discord_id = '{inter.author.id}'""")


        if autopay == 'True':
            autopay_embed = 'Включена'
        else:
            autopay_embed = 'Выключена'

        embed = disnake.Embed(
            title="Информация",
            colour=0xe60082,
        )
        embed.add_field(name='Вам выписан штраф: ',
                        value='',
                        inline=False)
        embed.add_field(name='От кого: ', value=username_moder, inline=False)
        embed.add_field(name='Кому: ',
                        value=username,
                        inline=False)
        embed.add_field(name='Причина: ',
                        value=description,
                        inline=False)
        embed.add_field(name='ID: ', value=id, inline=False)
        embed.add_field(name='Сумма штрафа: ', value=f'{count} АР', inline=False)
        embed.add_field(name='Авто-Оплата: ', value=f'{autopay_embed}', inline=False)
        embed.add_field(name='Старый баланс: ',
                        value=f'{old_balance} АР',
                        inline=False)
        embed.add_field(name='Новый баланс: ',
                        value=f'{balance} АР',
                        inline=False)

        user = await bot.fetch_user(discord_id)

        await user.send(embed=embed)
        
        if autopay == 'True':
            await user.send('Штраф оплачен автоматически')

        embed_admin = disnake.Embed(
        title="Информация для администрации",
        colour=0xf20000,
        )
        embed_admin.add_field(name='Действие: ',
                        value='Создание штрафа',
                        inline=False)
        embed_admin.add_field(name='От кого: ', value=username_moder, inline=False)
        embed_admin.add_field(name='Кому: ',
                        value=username,
                        inline=False)
        embed_admin.add_field(name='Причина: ',
                        value=description,
                        inline=False)
        embed_admin.add_field(name='ID: ', value=id, inline=False)
        embed_admin.add_field(name='Сумма штрафа: ', value=f'{count} АР', inline=False)
        embed_admin.add_field(name='Старый баланс: ',
                        value=f'{old_balance} АР',
                        inline=False)
        embed_admin.add_field(name='Новый баланс: ',
                        value=f'{balance} АР',
                        inline=False)

        channel = bot.get_channel(fine_channel)  # канал логов

        await channel.send(embed=embed_admin)


        if autopay == 'True':
            cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{discord_id}' AND carddefault = 'True'""")
            cur.execute(f"""DELETE FROM fines WHERE discord_id = '{discord_id}' AND id = {id}""")
            conn.commit()
            await channel.send(f'{username} оплатил штраф с причиной {description}')
        else:
            await user.send('Скорее оплатите штраф!')
            cur.close()
            conn.close()

        await inter.send(f'Штраф выписан\nID: {id}')
    except mc.Error as e:
        await inter.send(f'** Error: ** {e}')



#----FINES_ADMIN----#
@bot.slash_command(
    name='fines_admin',
    description='Посмотреть список штрафов игрока'
)
async def fines_admin(inter, username = commands.Param(description='Ник игрока')):
  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  try:
    cur.execute(
        f"""SELECT description FROM fines WHERE username = '{username}'""")
    result = cur.fetchall()
    embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
    )
    embed.add_field(name='Описание', value='', inline=True)
    embed.add_field(name='Сумма штрафа', value='')
    embed.add_field(name='ID', value='')
    embed.add_field(name='', value='', inline=False)
    for row in result:
        fmt = "{0}"
        cur.execute(
            f"""SELECT count FROM fines WHERE username = '{username}' AND description = '{fmt.format(*row)}'"""
        )
        count = cur.fetchone()
        cur.execute(
            f"""SELECT id FROM fines WHERE username = '{username}' AND description = '{fmt.format(*row)}'"""
        )
        id = cur.fetchone()[0]
        embed.add_field(name=fmt.format(*row), value='', inline=True)
        embed.add_field(name=f'{fmt.format(*count)} АР', value='')
        embed.add_field(name=id, value='')
        embed.add_field(name='', value='', inline=False)

    await inter.send(embed=embed)
    cur.close()
    conn.close()
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----UNFINE----#
@bot.slash_command(
  name='unfine',
  description='Удалить штраф'
)
@commands.has_any_role(1147225574499168367, 1144692417283506339) 
async def unfine(inter, username = commands.Param(description='Ник игрока'), id: int = commands.Param(description='ID штрафа', min_value = 10, max_value = 99)):
  conn = mc.connect(
        host='db.worldhosts.fun',  # создание курсора
        user='u4980_7K91YKi39n',
        password='=dgsI.+5R1!Aal=pozVfwcSD',
        db='s4980_BankDB',
        port=3306)
  cur = conn.cursor()
  try:
    cur.execute(f"""DELETE FROM fines WHERE username = '{username}' AND id = {id}""")
    cur.execute(f"""UPDATE users SET use_all = 'True' WHERE discord_id = '{inter.author.id}'""")
    
    conn.commit()

    await inter.send(f'Удален штраф для игрока {username}\nID: {id}')
    
    cur.execute(f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
    username_moder = cur.fetchone()[0]
    cur.execute(f"""SELECT discord_id FROM users WHERE username = '{username}' LIMIT 0, 1""")
    discord_id = cur.fetchone()[0]

    embed = disnake.Embed(
        title="Информация",
        colour=0xe60082,
    )
    embed.add_field(name='Действие: ',
                    value='Удаление штрафа',
                    inline=False)
    embed.add_field(name='Кто: ', value=username_moder, inline=False)
    embed.add_field(name='Кому: ',
                    value=username,
                    inline=False)
    embed.add_field(name='ID: ', value=id, inline=False)

    user = await bot.fetch_user(discord_id)

    await user.send(embed=embed)

    embed_admin = disnake.Embed(
        title="Информация для администрации",
        colour=0xf20000,
    )
    embed_admin.add_field(name='Действие: ',
                    value='Удаление штрафа',
                    inline=False)
    embed_admin.add_field(name='Кто: ', value=username_moder, inline=False)
    embed_admin.add_field(name='Кому: ',
                    value=username,
                    inline=False)
    embed_admin.add_field(name='ID: ', value=id, inline=False)

    channel = bot.get_channel(fine_channel)  # канал логов

    await channel.send(embed=embed_admin)
    
    cur.close()
    conn.close()
  except mc.Error as e:
        await inter.send(f'** Error: ** {e}')


#----RESTART----#
@bot.slash_command(
    name='restart',
    description='Ужасная команда'
)
@commands.has_any_role(1147225574499168367)
async def restart(inter):
    await inter.send('Перезагрузка...')

    python = sys.executable
    os.execl(python, python, *sys.argv)


#----government_ADD----#
@bot.slash_command(
    name='government_add',
    description='Добавить в правительство'
)
@commands.has_any_role(1147225574499168367)
async def government_add(inter, username):
    conn = mc.connect(
        host='db.worldhosts.fun',  # создание курсора
        user='u4980_7K91YKi39n',
        password='=dgsI.+5R1!Aal=pozVfwcSD',
        db='s4980_BankDB',
        port=3306)
    cur = conn.cursor()
    
    try:
        cur.execute(f"""SELECT discord_id FROM users WHERE username='{username}' LIMIT 0, 1""")
        discord_id = cur.fetchone()[0]
        if discord_id == None:
            await inter.send(f'Игрок с ником `{username}` не найден')
        else:
            cur.execute(f"""SELECT discord_name FROM users WHERE discord_id='{discord_id}' LIMIT 0, 1""")
            discord_name = cur.fetchone()[0]
            cur.execute(f"""SELECT username FROM users WHERE username = '{username}' LIMIT 0, 1""")
            username = cur.fetchone()[0]
            cur.execute(f"""SELECT balance FROM government LIMIT 0, 1""")
            balance = cur.fetchone()

            if balance is None:
                balance = 0
            else:
                balance = balance[0]
            cur.execute(f"""INSERT INTO government
                            (discord_id, discord_name, username, balance)
                            VALUES
                            ('{discord_id}', '{discord_name}', '{username}', '{balance}')"""
            )
            conn.commit()

            await inter.send(f'Игроку с ником `{username}` выдан доступ к государственной карте')
    except mc.Error as e:
            await inter.send(f'** Error: ** {e}')


#----CONSOLE LOG----#
# async def console_log():
#     a = 0
#     while a==1:
#         result = StringIO()
#         sys.stdout = result
#         result_string = result.getvalue()
#         if result_string != None:
#             user = await bot.fetch_user(admin_id)
#             await user.send(result_string)

# console_log()
bot.run('MTE0NTA3NDE4NTg5MTIzNzk1OA.GYH7Pm.8pcxfYonRx7DnI65LpFb6q9UBMT2tDVT83JQXs')

# bot.run('MTE0ODAwNzQ1Nzk0NDI0MDE1OA.GoevFD.IW6ODYpMb87aIR0rzW3rdLDZ7n9NkIZuSB5Etc') # TEST BOT
