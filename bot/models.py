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
def db_conn():
  conn = mc.connect(
      host=data['db']['host'],
      user=data['db']['user'],
      password=data['db']['password'],
      db=data['db']['db'],
      port=data['db']['port'])
  cur = conn.cursor()
  return conn, cur
