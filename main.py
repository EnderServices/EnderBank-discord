import disnake
from disnake.ext import commands

import mysql.connector as mc
from typing import Optional
import datetime
import random
from colorama import Fore, Style

from bot.models import *
from bot.messages import *


# ----ИВЕНТЫ---- #
# Запуск бота
@bot.event
async def on_ready():
  now = datetime.datetime.now()
  print(
      Fore.RED + now.strftime("%Y-%m-%d %H:%M:%S") + ': ' + Fore.GREEN +
      f"Bot {bot.user} is ready to work" + Style.RESET_ALL)
  channel = bot.get_channel(start_channel)  # канал логов
  await channel.send(now.strftime("%Y-%m-%d %H:%M:%S") + ': ' + 'Бот успешно запущен')



# ----КОМАНДЫ---- #
# Создание карты
@bot.slash_command(name='create_card', description='Создание новой карты')
async def create_card(inter,
                      user=commands.Param(description='Ник в Minecraft'),
                      cardname=commands.Param(description='Название карты')):

  await inter.response.defer()
  conn, cur = db_conn()
  
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


# Список карт
@bot.slash_command(name='cards', description='Список карт и их баланс')
async def cards(inter):

  await inter.response.defer()
  conn, cur = db_conn()

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


# Перевод
@bot.slash_command(name='transfer',
                   description='Денежный перевод другому игроку')
async def transfer(
    inter,
    user=commands.Param(description='Ник кому хотите перевести деньги'),
    cardname=commands.Param(description='Карта с которой списать деньги'),
    count: int = commands.Param(description='Сумма перевода', min_value=1),
    description=commands.Param(description='Сообщение')):

  await inter.response.defer()
  conn, cur = db_conn()
  
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
        username_sender = cur.fetchone()[0]

        cur.execute(
                f"""SELECT clan_cardname FROM clans WHERE clan_cardname = '{cardname}'"""
            ) # Ищем в БД карта клана равную cardname
        sender = cur.fetchone()[0]
        
        if sender == None: # Если ответ из БД равен None, получаем карту 
            cur.execute(
                f"""SELECT cardname FROM users WHERE discord_id = '{inter.author.id}' LIMIT 1"""
            )
            sender = cur.fetchone()
            if sender != None:
                sender_type = 'user'
            else:
                await inter.send('Карта не найдена')
        else:
            sender_type = 'clan'

        cur.execute(
            f"""SELECT username FROM users WHERE username = '{user}' LIMIT 1"""
        )
        recipient = cur.fetchone()
        if recipient == None:
            cur.execute(
                f"""SELECT clan_cardname FROM clans WHERE clan_cardname = '{user}'"""
            )
            recipient = cur.fetchone()
            if recipient != None:
                recipient_type = 'clan'
            else:
                await inter.send('Игрок не найден')
        else:
            recipient_type = 'user'


        if recipient_type == 'user':
            cur.execute(
                f"""SELECT discord_id FROM users WHERE username = '{user}' LIMIT 1""")
        elif recipient_type == 'clan':
            cur.execute(
                f"""SELECT discord_id_author FROM clans WHERE clan_cardname = '{user}' LIMIT 1""")
        user_recipient_id = cur.fetchone()[0]

        
        if sender_type == 'user':
            cur.execute(
                f"""SELECT balance FROM users WHERE username = '{username_sender}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}' LIMIT 1"""
            )
        elif sender_type == 'clan':
            cur.execute(
                f"""SELECT balance FROM clans WHERE clan_cardname = '{cardname}' LIMIT 1"""
            )
        balance_sender = int(cur.fetchone()[0])
        old_balance_sender = balance_sender
        
        if recipient_type == 'user':
            cur.execute(
                f"""SELECT balance FROM users WHERE username = '{user}' AND carddefault = 'True' LIMIT 1"""
            )
        elif recipient_type == 'clan':
            cur.execute(
                f"""SELECT balance FROM clans WHERE clan_cardname = '{user}' LIMIT 1"""
            )
        balance_recipient = int(cur.fetchone()[0])
        old_balance_recipient = balance_recipient
        if sender_type == 'user':
            if username_sender == user:
                await inter.send('Перевод на свой счет запрещен')
            
            else:
                if balance_sender - count >= 0:
                    balance_sender = balance_sender - count
                    balance_recipient = balance_recipient + count
                    if sender_type == 'user':
                        cur.execute(f"""UPDATE users 
                                        SET balance = {balance_sender}
                                        WHERE username = '{username_sender}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}'"""
                                    )
                    elif sender_type == 'clan':
                                            cur.execute(f"""UPDATE clans 
                                        SET balance = {balance_sender}
                                        WHERE clan_cardname = '{user}'""")
                    conn.commit()
                    if recipient_type == 'user':
                        cur.execute(f"""UPDATE users 
                                        SET balance = {balance_recipient}
                                        WHERE username = '{user}' AND carddefault = 'True'""")
                    elif recipient_type == 'clan':
                        cur.execute(f"""UPDATE clans 
                                        SET balance = {balance_recipient}
                                        WHERE clan_cardname = '{user}'""")
                    conn.commit()
                    embed = disnake.Embed(
                        title="Информация о переводе",
                        colour=0xe60082,
                    )
                    embed.add_field(name='От кого: ', value=f'{username_sender}', inline=False)
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
                    embed.add_field(name='Сообщение: ', value=description, inline=False)

                    await inter.send(embed=embed)

                    channel = bot.get_channel(transfer_channel)  # канал логов

                    embed_admin = disnake.Embed(
                        title="Информация для администрации",
                        colour=0xf20000,
                    )
                    embed_admin.add_field(name='Действие: ', value='Перевод', inline=False)
                    embed_admin.add_field(name='От кого: ',
                                            value=f'{username_sender}',
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
                    embed_admin.add_field(name='Сообщение: ', value=description, inline=False)
                    await channel.send(embed=embed_admin)

                    embed_recipient = disnake.Embed(
                        title="Пополнение счета",
                        colour=0xe60082,
                    )

                    embed_recipient.add_field(name='Действие: ',
                                                value='Перевод',
                                                inline=False)
                    embed_recipient.add_field(name='От кого: ',
                                                value=f'{username_sender}',
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
                                                value=description,
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
                if sender_type == 'user':
                    cur.execute(f"""UPDATE users 
                                    SET balance = {balance_sender}
                                    WHERE username = '{username_sender}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}'"""
                                )
                elif sender_type == 'clan':
                    cur.execute(f"""UPDATE clans 
                                    SET balance = {balance_sender}
                                    WHERE clan_cardname = '{cardname}'""")
                conn.commit()
                if recipient_type == 'user':
                    cur.execute(f"""UPDATE users 
                                    SET balance = {balance_recipient}
                                    WHERE username = '{user}' AND carddefault = 'True'""")
                elif recipient_type == 'clan':
                    cur.execute(f"""UPDATE clans 
                                    SET balance = {balance_recipient}
                                    WHERE clan_cardname = '{user}'""")
                conn.commit()
                embed = disnake.Embed(
                    title="Информация о переводе",
                    colour=0xe60082,
                )
                embed.add_field(name='От кого: ', value=f'{username_sender}', inline=False)
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
                embed.add_field(name='Сообщение: ', value=description, inline=False)

                await inter.send(embed=embed)

                channel = bot.get_channel(transfer_channel)  # канал логов

                embed_admin = disnake.Embed(
                    title="Информация для администрации",
                    colour=0xf20000,
                )
                embed_admin.add_field(name='Действие: ', value='Перевод', inline=False)
                embed_admin.add_field(name='От кого: ',
                                        value=f'{username_sender}',
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
                embed_admin.add_field(name='Сообщение: ', value=description, inline=False)
                await channel.send(embed=embed_admin)
                if recipient_type == 'user':
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
                                            value=f'{username_sender}',
                                            inline=False)
                embed_admin.add_field(name='Кому: ', value=f'{user}', inline=False)
                if recipient_type == 'user':
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
                                            value=description,
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
  

# Перевод между своими картами
@bot.slash_command(name='swap', description='Перевод между счетами')
async def swap(inter,
               card_1=commands.Param(description='Первый счет'),
               card_2=commands.Param(description='Второй счет'),
               count: int = commands.Param(description='Сумма перевода',
                                           min_value=1)):

  await inter.response.defer()
  conn, cur = db_conn()
  
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
        
        
# Изменение карты по умолчанию
@bot.slash_command(name='set_default',
                   description='Изменить карту по умолчанию')
async def set_default(
    inter,
    card=commands.Param(
        description='Название карты, которую хотите сделать картой по умолчанию'
    )):

  await inter.response.defer()
  conn, cur = db_conn()
  
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
        

# Список штрафов
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
        
        
# Оплата штрафа
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
        
        
# Статистика


  
  
  
  
  
  
  
# Запуск бота
bot.run(data['main']['token'])