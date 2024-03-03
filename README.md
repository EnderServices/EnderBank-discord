# EnderBank
## Банковский Discord бот для Майнкрафт сервера

Этот бот предназначен для управления виртуальными банковскими картами и переводами денежных средств между игроками на Майнкрафт сервере. Бот интегрируется с Discord сервером и использует слэш-команды для взаимодействия.

## Файлы
- `config.yaml` - файл конфигурации бота
- `main.py` - основной файл с кодом бота
- `bot/messages.py` - файл с константами для ID каналов Discord
- `bot/models.py` - файл с моделями данных
- `requirements.txt` - файл зависимостей

## Настройка
1. Склонируйте этот репозиторий 
```
git clone https://github.com/Mag329/EnderBank.git
```
2. Установите все необходимые зависимости, указанные в `requirements.txt`
```
pip install -r requirements.txt
```
3. Заполните файл `config.yaml`
4. Запустите бота с помощью команды 
```
python3 main.py
```

## Функции бота

- Создание виртуальных карт для игроков
- Просмотр списка имеющихся карт и их баланса
- Перевод денежных средств между картами игроков и кланов
- Изменение карты по умолчанию
- Выписка и оплата штрафов
- Статистика игроков по балансу
- Команды администрации (изменение баланса, SQL-запросы, выдача доступа к гос. карте и др.)
- Логирование всех админ-операций в специальных каналах Discord

## Использование

Бот реагирует на следующие слэш-команды в Discord:

### Команды для игроков

- `/create_card user: <Ник в Minecraft> cardname: <Название карты>` - создание новой банковской карты
  ```
  /create_card user:Mag329 cardname:Карта Мага
  ```

- `/cards` - вывод списка всех имеющихся карт и их баланса

- `/translate user: <Ник/название клана кому хотите перевести> cardname: <Карта с которой списать деньги> count: <Сумма перевода> descrition: <Сообщение>` - перевод денег другому игроку или клану
  ```
  /translate user: Withor_ cardname: Карта Мага count: 10 descrition: Спасибо за плагин
  ```

- `/swap card_1: <Название карты с которой вы хотите перевести Ары> card_2: <Название карты на которую хотите перевести Ары> count: <Сумма перевода>` - перевод денег между своими картами
  ```
  /swap card_1: Карта Мага card_2: Вторая карта count:15
  ``` 

- `/set_default card: <Название карты>` - изменение карты по умолчанию
  ```
  /set_default card: Вторая карта
  ```

- `/fines` - список выписанных штрафов

- `/pay id: <ID штрафа, выводится при получение или при использование /fines> count: <Сумма оплаты> cardname: <Карта с которой хотите оплатить>` - оплата штрафа
  ```
  /pay id: 24 count: 10 cardname: Карта мага
  ```

- `/stats` - статистика топ игроков по балансу

### Команды администрации  

- `/set_balance user_mc: <Ник игрока> cardname: <Название карты на которой изменить баланс> balance: <Новый баланс>` - изменить баланс карты игрока
```
/set_balance user_mc: Mag329 cardname: Карта мага balance: 10
```
- `/cards_admin username: <Ник игрока>` - показать карты и баланс указанного игрока
```
/cards_admin username: Mag329
```
- `/sql_console sqlcommand: <SQL запрос>` - выполнить SQL запрос в базе данных
```
/sql_console sqlcommand: DELETE FROM users WHERE username = "Mag329"
```
- `/fine username: <Ник игрока> count: <Сумма штрафа> description: <Описание> autopay: <Авто оплата(True/False)>` - выписать штраф игроку
- `/fines_admin <ник_игрока>` - список штрафов указанного игрока
- `/unfine <ник_игрока> <id_штрафа>` - удалить штраф игрока
- `/restart` - перезапустить бота.
- `/government_add <ник_игрока>` - выдать доступ к государственной карте
- `/debug` - получить файл с логами бота

Подробное описание команд и их аргументов можно найти в исходном коде `main.py`.

## Логирование

Все операции бота логируются в файл `log_file.txt`. Критические ошибки также отправляются владельцу бота в Discord.
