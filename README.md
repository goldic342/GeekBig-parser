# About
Еhis script "browses" for all the names and prices of all the products on [this](https://biggeek.ru/) site. 
And then filters them and finds the products specified in `CONDTION`. 
The script also sends a notification in a telegram if it has found the right product, you can view the statistics of scanned products, pages and links in the bot

## Dependencies
You need these three modules, which you most likely don't have installed

```bash
sudo pip install bs4
sudo pip install requests
sudo pip install telebot
```

## Usage
Create your config file first:
```bash
cp config.py.template config.py
```

Create a `TOKEN.txt` where will your bot's token be stored
```bash
echo "<YOUR_BOT_TOKEN>" > TOKEN.txt
```

Run script file: 
```bash
python main.py
```
## Variables
**Change in `config.py`**
- `Debug` - Set to `True` for verbose realtime printing to console for debugging or development **not necessary**
- `CONDITION_1`, `CONDITION_2`, `CONDITION_3` - Write your condition here iin this format ```["Product name", "Product price"]```

## Bugs 
There is one invalid [link](https://biggeek.ru/catalog/uslugi) on the site that makes the script run indefinitely, because it finds products, but they are not visible to the user.
This is fixed with this simple check: 
```python
if add_page_prefix(url, urlPageIndex) == "https://biggeek.ru/catalog/uslugi?page=2":
  break
```
