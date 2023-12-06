# About
Еhis script "browses" for all the names and prices of all the products on [this](https://biggeek.ru/) site. 
And then filters them and finds the products specified in `CONDTION`. 
The script also sends a notification in a telegram if it has found the right product, you can view the statistics of scanned products, pages and links in the bot

## Dependencies
You need these three modules, which you most likely don't have installed

```bash
sudo pip install bs4
```

```bash
sudo pip install requests
```

```bash
sudo pip install telebot
```

## Usage
Create your config file first:
```bash
cp config.py.template config.py
```

Run script file: 
```bash
python main.py
```
