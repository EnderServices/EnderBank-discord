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