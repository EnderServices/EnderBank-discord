from flask import Flask
from flask import request
from threading import Thread
import time
import requests
import mysql.connector as mc

app = Flask('')


@app.route('/')
def home():
  return "I'm alive"


def run():
  app.run(host='0.0.0.0', port=84)


def keep_alive():
  t = Thread(target=run)
  t.start()

@app.route('/add', methods=['GET', 'POST'])
def addar():
    if flask.request.method == 'POST':
        return ""
    else:
        username = flask.request.args.get('nick')
        amount = flask.request.args.get('amunt')
        try:
            conn = mc.connect(
                host='db.worldhosts.fun',  # создание курсора
                user='u4980_7K91YKi39n',
                password='=dgsI.+5R1!Aal=pozVfwcSD',
                db='s4980_BankDB',
                port=3306)
            cur = conn.cursor()
            cur.execute(
                f"""SELECT balance FROM users WHERE username = '{username}' AND carddefault = 'True'"""
            )
            balance = int(cur.fetchone()[0])

            balance = balance + amount

            cur.execute(f"""UPDATE users 
                            SET balance = {balance}
                            WHERE username = '{username}' AND carddefault = 'True'""")
            conn.commit()

            cur.close()
            conn.close()
        except mc.connector.Error as err:
           print("Error while connecting to MySQL",err)

		  #код добавления аров в бд
        return 'true'
		  

@app.route('/get', methods=['GET', 'POST'])
def getar():
    if flask.request.method == 'POST':
        return ""
    else:
        username = flask.request.args.get('nick')
        amount = flask.request.args.get('amunt')

        try:
            conn = mc.connect(
                host='db.worldhosts.fun',  # создание курсора
                user='u4980_7K91YKi39n',
                password='=dgsI.+5R1!Aal=pozVfwcSD',
                db='s4980_BankDB',
                port=3306)
            cur = conn.cursor()
            cur.execute(
                f"""SELECT balance FROM users WHERE username = '{username}' AND carddefault = 'True'"""
            )
            balance = int(cur.fetchone()[0])

            if balance - amount >= 0:

                balance = balance - amount

                cur.execute(f"""UPDATE users 
                                SET balance = {balance}
                                WHERE username = '{username}' AND carddefault = 'True'""")
                conn.commit()

                cur.close()
                conn.close()

            return 'true'

        except mc.connector.Error as err:
            print("Error while connecting to MySQL",err)

            #код удаления аров с бд + проверка на то есть ли такие деньги вернуть значение 'true' если успешно
            