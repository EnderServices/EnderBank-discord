import disnake
from disnake.ext import commands

import mysql.connector as mc
from typing import Optional
# import schedule
import datetime
import random


# from background import keep_alive

bot = commands.Bot(command_prefix='!',
                   help_command=None,
                   intents=disnake.Intents.all(),
                   activity=disnake.Game(name="ЭмблаX"))
client = disnake.Client()

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
      now.strftime("%Y-%m-%d %H:%M") + ': ' +
      f"Bot {bot.user} is ready to work")


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

  cur.execute(f"""SELECT use_all FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
  use_all = cur.fetchone()[0]

  if use_all == 'True':
    cur.execute(
        f"""SELECT amount(*) FROM users WHERE username = '{user}' AND discord_id = '{inter.author.id}'"""
    )
    default = int(cur.fetchone()[0])

    if default >= 1:
        cur.execute(f"""INSERT INTO users
                            (discord_id, discord_name, username, cardname, balance, carddefault)
                            VALUES
                            ('{inter.author.id}', '{inter.author.name}', '{user}', '{cardname}', '0', 'False')"""
                    )
    else:
        cur.execute(f"""INSERT INTO users
                            (discord_id, discord_name, username, cardname, balance, carddefault)
                            VALUES
                            ('{inter.author.id}', '{inter.author.name}', '{user}', '{cardname}', '0', 'True')"""
                    )

    conn.commit()
    channel = bot.get_channel(1147602744560066670)  # канал логов

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

  cur.execute(f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND carddefault = 'True'""")
  balance_carddefault = int(cur.fetchone()[0])

  if balance_carddefault >= 0:
    cur.execute(f"""UPDATE users SET use_all = 'True' WHERE discord_id = '{inter.author.id}'""")
    conn.commit()

  cur.execute(
      f"""SELECT cardname FROM users WHERE discord_id = '{inter.author.id}'""")
  result = cur.fetchall()
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
    cur.execute(
        f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{fmt.format(*row)}'"""
    )
    balance = cur.fetchone()
    cur.execute(
        f"""SELECT carddefault FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{fmt.format(*row)}'"""
    )
    carddefault = cur.fetchone()
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
    amount: int = commands.Param(description='Сумма перевода', min_value=1),
    descrition=commands.Param(description='Сообщение')):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()

  cur.execute(f"""SELECT use_all FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")
  use_all = cur.fetchone()[0]

  if use_all == 'True':
    cur.execute(
        f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1"""
    )
    user_send = cur.fetchone()[0]

    cur.execute(
        f"""SELECT discord_id FROM users WHERE username = '{user}' LIMIT 0, 1""")
    user_recipient_id = cur.fetchone()[0]

    cur.execute(
        f"""SELECT balance FROM users WHERE username = '{user_send}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}'"""
    )
    balance_sender = int(cur.fetchone()[0])
    old_balance_sender = balance_sender

    cur.execute(
        f"""SELECT balance FROM users WHERE username = '{user}' AND carddefault = 'True'"""
    )
    balance_recipient = int(cur.fetchone()[0])
    old_balance_recipient = balance_recipient
    if user_send == user:
        await inter.send('Перевод на свой счет запрещен')
    else:
        if balance_sender - amount >= 0:
            balance_sender = balance_sender - amount
            balance_recipient = balance_recipient + amount
            cur.execute(f"""UPDATE users 
                            SET balance = {balance_sender}
                            WHERE username = '{user_send}' AND cardname = '{cardname}' AND discord_id = '{inter.author.id}'"""
                        )
            conn.commit()
            cur.execute(f"""UPDATE users 
                            SET balance = {balance_recipient}
                            WHERE username = '{user}' AND carddefault = 'True'""")
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
                            value=f'{amount} АР',
                            inline=False)
            embed.add_field(name='Сообщение: ', value=descrition, inline=False)

            await inter.send(embed=embed)

            channel = bot.get_channel(1147602744560066670)  # канал логов

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
                                    value=f'{amount} АР',
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
                                        value=f'{amount} АР',
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
    await inter.send('Ваш баланс отрицательный!\nНекоторые функции заблокированы')


#----SWAP----#
@bot.slash_command(name='swap', description='Перевод между счетами')
async def swap(inter,
               card_1=commands.Param(description='Первый счет'),
               card_2=commands.Param(description='Второй счет'),
               amount: int = commands.Param(description='Сумма перевода',
                                           min_value=1)):

  await inter.response.defer()

  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()
  cur.execute(
      f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{card_1}'"""
  )
  first_balance = int(cur.fetchone()[0])
  old_first_balance = first_balance

  cur.execute(
      f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{card_2}'"""
  )
  second_balance = int(cur.fetchone()[0])
  old_second_balance = second_balance

  cur.execute(
      f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{card_1}' LIMIT 0, 1"""
  )
  username = cur.fetchone()[0]

  if first_balance - amount >= 0:
    first_balance = first_balance - amount
    second_balance = second_balance + amount
    cur.execute(f"""UPDATE users 
                    SET balance = {first_balance}
                    WHERE discord_id = '{inter.author.id}' AND cardname = '{card_1}'"""
                )
    conn.commit()
    cur.execute(f"""UPDATE users 
                    SET balance = {second_balance}
                    WHERE discord_id = '{inter.author.id}' AND cardname = '{card_2}'"""
                )
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
    embed.add_field(name='Сумма перевода: ', value=f'{amount} АР', inline=False)
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
                          value=f'{amount} АР',
                          inline=False)
    embed_admin.add_field(name='Вторая карта: ', value=card_2, inline=False)
    embed_admin.add_field(name='Старый баланс: ',
                          value=f'{old_second_balance} АР',
                          inline=False)
    embed_admin.add_field(name='Новый баланс: ',
                          value=f'{second_balance} АР',
                          inline=False)

    channel = bot.get_channel(1147602744560066670)  # канал логов

    await channel.send(embed=embed_admin)
  else:
    await inter.send('Недостаточно средств')
  cur.close()
  conn.close()


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

    channel = bot.get_channel(1147602744560066670)  # канал логов

    await channel.send(embed=embed_admin)
    cur.close()
    conn.close()
  else:
    await inter.send('Ваш баланс отрицательный!\nНекоторые функции заблокированы')


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
        f"""SELECT amount FROM fines WHERE discord_id = '{inter.author.id}' AND description = '{fmt.format(*row)}'"""
    )
    amount = cur.fetchone()
    cur.execute(
        f"""SELECT id FROM fines WHERE discord_id = '{inter.author.id}' AND description = '{fmt.format(*row)}'"""
    )
    id = cur.fetchone()[0]
    embed.add_field(name=fmt.format(*row), value='', inline=True)
    embed.add_field(name=f'{fmt.format(*amount)} АР', value='')
    embed.add_field(name=id, value='')
    embed.add_field(name='', value='', inline=False)

  await inter.send(embed=embed)
  cur.close()
  conn.close()


#----PAY----#
@bot.slash_command(
    name='pay',
    description='Оплатить штраф'
)
async def pay(inter, id: int = commands.Param(description='ID штрафа', min_value = 10, max_value = 99), amount: int = commands.Param(description='Сколько хотиите оплатить', min_value = 1), cardname = commands.Param(description='Карта с которой хотите произвести оплату')):
  conn = mc.connect(
      host='db.worldhosts.fun',  # создание курсора
      user='u4980_7K91YKi39n',
      password='=dgsI.+5R1!Aal=pozVfwcSD',
      db='s4980_BankDB',
      port=3306)
  cur = conn.cursor()

  cur.execute(f"""SELECT balance FROM users WHERE discord_id = '{inter.author.id}' AND cardname = '{cardname}'""")
  balance = int(cur.fetchone()[0])
  cur.execute(f"""SELECT amount FROM fines WHERE discord_id = '{inter.author.id}' AND id = '{id}'""")
  amount_fine = int(cur.fetchone()[0])

  if amount_fine < amount:
    amount = amount_fine
    
  old_balance = balance

  if amount_fine - amount <= 0:
    if balance - amount > 0:
      balance = balance - amount
    cur.execute(f"""DELETE FROM fines WHERE discord_id = '{inter.author.id}' AND id = {id}""")
    cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{inter.author.id}' AND cardname = '{cardname}'""")
    
    conn.commit()

    embed = disnake.Embed(
      title="Информация",
      colour=0xe60082,
    )
    embed.add_field(name='Действие: ', value='Оплата штрафа', inline=False)
    embed.add_field(name='Сумма штрафа', value=f'{amount_fine}', inline=False)
    embed.add_field(name='Оплачено: ', value=f'{amount}', inline=False)
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
    embed_admin.add_field(name='Сумма штрафа', value=f'{amount_fine}', inline=False)
    embed_admin.add_field(name='Оплачено: ', value=f'{amount}', inline=False)
    embed_admin.add_field(name='Карта: ', value=cardname, inline=False)
    embed_admin.add_field(name='Старый баланс: ',
                          value=f'{old_balance} АР',
                          inline=False)
    embed_admin.add_field(name='Новый баланс: ',
                          value=f'{balance} АР',
                          inline=False)
    embed_admin.add_field(name='ID', value=id, inline=False)

    channel = bot.get_channel(1147602744560066670)  # канал логов

    await channel.send(embed=embed_admin)


  else:
    balance = balance - amount

    cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{inter.author.id}' AND cardname = '{cardname}'""")
    cur.execute(f"""UPDATE fines SET amount = {amount_fine-amount} WHERE discord_id = '{inter.author.id}' AND id = '{id}'""")
    conn.commit()


    embed = disnake.Embed(
      title="Информация",
      colour=0xe60082,
    )
    embed.add_field(name='Действие: ', value='Оплата штрафа', inline=False)
    embed.add_field(name='Сумма штрафа', value=f'{amount_fine}', inline=False)
    embed.add_field(name='Оплачено: ', value=f'{amount}', inline=False)
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
    embed_admin.add_field(name='Сумма штрафа', value=f'{amount_fine}', inline=False)
    embed_admin.add_field(name='Оплачено: ', value=f'{amount}', inline=False)
    embed_admin.add_field(name='Карта: ', value=cardname, inline=False)
    embed_admin.add_field(name='Старый баланс: ',
                          value=f'{old_balance} АР',
                          inline=False)
    embed_admin.add_field(name='Новый баланс: ',
                          value=f'{balance} АР',
                          inline=False)
    embed_admin.add_field(name='ID', value=id, inline=False)

    channel = bot.get_channel(1147602744560066670)  # канал логов

    await channel.send(embed=embed_admin)













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

  channel = bot.get_channel(1147602744560066670)  # канал логов

  await channel.send(embed=embed_admin)
  await inter.send('Баланс обновлен')
  cur.close()
  conn.close()


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

  cur.execute(f"{sqlcommand}")
  conn.commit()
  cur.close()
  conn.close()
  await inter.send(f'Выполнена команда: {sqlcommand}')


#----FINE----#
@bot.slash_command(
  name='fine',
  description='Выписать штраф'
)
@commands.has_any_role(1147225574499168367, 1144692417283506339)
async def fine(inter, 
               username: str = commands.Param(description='Ник на кого будет выписан штраф'), 
               amount: int = commands.Param(description='Сумма штрафа', min_value = 1), 
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

    now = datetime.datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    
    cur.execute(f"""SELECT username FROM users WHERE discord_id = '{inter.author.id}' LIMIT 0, 1""")

    username_moder = cur.fetchone()[0]

    cur.execute(f"""SELECT discord_id FROM users WHERE username = '{username}' LIMIT 0, 1""")

    discord_id = cur.fetchone()[0]

    id = random.randint(10,99)

    cur.execute(f"""INSERT INTO fines
                    (discord_id_moder, username_moder, discord_id, username, amount, description, autopay, date, id)
                    VALUES
                    ('{inter.author.id}', '{username_moder}', '{discord_id}', '{username}', '{amount}', '{description}', '{autopay}', '{formatted_date}', {id})"""
    )
    conn.commit()

    cur.execute(f"""SELECT balance FROM users WHERE discord_id = '{discord_id}' AND carddefault = 'True'""")

    balance = int(cur.fetchone()[0])
    old_balance = balance


    if autopay == 'True':
        balance = balance - amount
        cur.execute(f"""UPDATE users SET balance = {balance} WHERE discord_id = '{inter.author.id}' AND carddefault = 'True'""")
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
    embed.add_field(name='Сумма штрафа: ', value=f'{amount} АР', inline=False)
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
    embed_admin.add_field(name='Сумма штрафа: ', value=f'{amount} АР', inline=False)
    embed_admin.add_field(name='Старый баланс: ',
                    value=f'{old_balance} АР',
                    inline=False)
    embed_admin.add_field(name='Новый баланс: ',
                    value=f'{balance} АР',
                    inline=False)

    channel = bot.get_channel(1147602744560066670)  # канал логов

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

    await inter.send('Штраф выписан')



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
        f"""SELECT amount FROM fines WHERE username = '{username}' AND description = '{fmt.format(*row)}'"""
    )
    amount = cur.fetchone()
    cur.execute(
        f"""SELECT id FROM fines WHERE username = '{username}' AND description = '{fmt.format(*row)}'"""
    )
    id = cur.fetchone()[0]
    embed.add_field(name=fmt.format(*row), value='', inline=True)
    embed.add_field(name=f'{fmt.format(*amount)} АР', value='')
    embed.add_field(name=id, value='')
    embed.add_field(name='', value='', inline=False)

  await inter.send(embed=embed)
  cur.close()
  conn.close()


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
  cur.execute(f"""DELETE FROM fines WHERE username = '{username}' AND id = {id}""")
  cur.execute(f"""UPDATE users SET use_all = 'True' WHERE discord_id = '{inter.author.id}'""")
  
  conn.commit()

  await inter.send(f'Удален штраф для игрока {username}\nID: {id}')

  embed_admin = disnake.Embed(
      title="Информация для администрации",
      colour=0xf20000,
  )
  embed_admin.add_field(name='Действие: ',
                  value='Удаление штрафа',
                  inline=False)
  embed_admin.add_field(name='Кто: ', value=inter.author.name, inline=False)
  embed_admin.add_field(name='Кому: ',
                  value=username,
                  inline=False)
  embed_admin.add_field(name='ID: ', value=id, inline=False)

  channel = bot.get_channel(1147602744560066670)  # канал логов

  await channel.send(embed=embed_admin)
  
  cur.close()
  conn.close()



# keep_alive()
bot.run(
    'MTE0NTA3NDE4NTg5MTIzNzk1OA.G_H3dh.kBp7fpeXDEE3frooXM0EdtW7LFYCkJM8_DoHeM')

