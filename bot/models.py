import disnake
from disnake.ext import commands

import mysql.connector as mc
import yaml
import os
import logging


# Загрузка файл конфига
config_path = os.path.join(os.getcwd(), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    data = yaml.safe_load(f)
    
# Параметры логирования   
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s\n\n",
    filename="log_file.txt",
    filemode="w",
)
    
# Инициализация бота
bot = commands.Bot(command_prefix='!',
                   help_command=None,
                   intents=disnake.Intents.all(),
                   activity=disnake.Game(name=data['main']['game_activity']))


# Инициализация базы данных
async def db_conn():
    try:
        conn = mc.connect(
            host=data['db']['host'],
            user=data['db']['user'],
            password=data['db']['password'],
            db=data['db']['db'],
            port=data['db']['port'],
            auth_plugin='mysql_native_password')
        cur = conn.cursor()
    except mc.Error as e:
        logging.error(f'Ошибка подключения к базе данных\nError: {e}')
        
        user = bot.get_user(data['main']['owner'])
        await user.send(f'Ошибка подключения к базе данных\nError: {e}')
        
        raise ConnectionError('Произошла ошибка при подключении к базе данных. Повторите попытку позже') from e
    return conn, cur


async def db_tables_check():
    try:
        conn, cur = await db_conn()
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        new_tables = []

        for table in tables:
            # if type(table) != list:
                # table = table[0].decode("utf-8")
            table = table[0]
            new_tables.append(table)
        tables = new_tables
        if not ('users' in tables):
            cur.execute("""CREATE TABLE `users` (
                        `discord_id` text CHARACTER SET utf8mb4 NOT NULL,
                        `discord_name` text CHARACTER SET utf8mb4 NOT NULL,
                        `username` text CHARACTER SET utf8mb4 NOT NULL,
                        `cardname` text CHARACTER SET utf8mb4 NOT NULL,
                        `balance` int(11) NOT NULL,
                        `carddefault` text CHARACTER SET utf8mb4 NOT NULL,
                        `use_all` text CHARACTER SET utf8mb4 NOT NULL,
                        `clancard` text CHARACTER SET utf8mb4 NOT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """)
        if not ('clans') in tables:
            cur.execute("""CREATE TABLE `clans` (
                        `discord_id_author` text CHARACTER SET utf8mb4 NOT NULL,
                        `username_author` text CHARACTER SET utf8mb4 NOT NULL,
                        `clan_cardname` text CHARACTER SET utf8mb4 NOT NULL,
                        `balance` int(11) NOT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """)
        
        if not ('fines') in tables:
            cur.execute("""CREATE TABLE `fines` (
                        `id` int(11) NOT NULL,
                        `discord_id_moder` text CHARACTER SET utf8 NOT NULL,
                        `username_moder` text CHARACTER SET utf8mb4 NOT NULL,
                        `discord_id` text CHARACTER SET utf8mb4 NOT NULL,
                        `username` text CHARACTER SET utf8mb4 NOT NULL,
                        `count` int(11) NOT NULL,
                        `description` text CHARACTER SET utf8mb4 NOT NULL,
                        `autopay` text CHARACTER SET utf8mb4 NOT NULL,
                        `date` datetime NOT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """)
            
        if not ('government') in tables:
            cur.execute("""CREATE TABLE `government` (
                        `discord_id` text CHARACTER SET utf8 NOT NULL,
                        `discord_name` text CHARACTER SET utf8mb4 NOT NULL,
                        `username` text CHARACTER SET utf8mb4 NOT NULL,
                        `balance` int(11) NOT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
            """)
            
        if data['main']['use_market'] == True:
            if not ('market') in tables:
                cur.execute("""CREATE TABLE `market` (
                            `discord_id` text CHARACTER SET utf8mb4 NOT NULL,
                            `username` text CHARACTER SET utf8mb4 NOT NULL,
                            `id` int(11) NOT NULL,
                            `name` text CHARACTER SET utf8mb4 NOT NULL,
                            `description` text CHARACTER SET utf8mb4 NOT NULL,
                            `price` int(11) NOT NULL,
                            `amount` int(11) NOT NULL DEFAULT 1,
                            `number` int(11) NOT NULL,
                            `msg_id` text NOT NULL
                            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
                """)
            
        conn.commit()
        cur.close()
        conn.close()
        return 
        
    except ConnectionError as e:
        logging.critical(f'Ошибка первоначального подключения к базе данных\n{e}')
        raise ConnectionError('Произошла ошибка при подключении к базе данных. Проверьте настройки базы данных') from e