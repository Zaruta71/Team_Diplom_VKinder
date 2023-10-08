# About

A simple chat bot for finding candidates for romantic dates.
![bot's dialog shema](https://github.com/Zaruta71/Team_Diplom_VKinder/raw/main/dialog_shema.jpg)
![database shema](https://github.com/Zaruta71/Team_Diplom_VKinder/raw/main/db_shema.jpg)

# Installation

## clone repo go to the directory:

```
git clone <repo_name>
cd <repo_name>
```

## setup virtualenvironment:

```
python -m venv .venv
```

## activate virtualenvironment:

- linux:

```
source .venv/bin/activate
```

- windows

```
.venv\Scripts\activate
```

## install dependencies from requirements.txt

```
pip install -r requirements.txt
```

## Create database in postgres

## change the file settings.py

```
GROUP_TOKEN - VK group token
USER_TOKEN - VK user token
DB_LOGIN = {"login": "{YOUR_LOGIN}", "password": {YOUR_PASSWORD}, "host": "localhost", "port": 5432, "database": {YOUR_DATABASE_NAME}}
```

# Usage

## run main.py

```
python main.py
```

## write to the bot "/start"

# Technology stack

- python
- vkbottle
- postgresql
- sqlalchemy
