# Imports
import bs4
from bs4 import BeautifulSoup
import requests

import telebot

# Importing Conditions
try:
    import config
except ImportError:
    print("Can not import config file")
    print("Make sure that you copy config.py.template to config.py")
    exit()


def debug_message(message):
    if config.Debug:
        print(message)


# debug feature
debug_message("PROJECT START")

# Bot class creating
with open("TOKEN.txt", 'r') as token_file:
    TOKEN = token_file.read()
    
    # Debug message
    a = requests.get(url=f'https://api.telegram.org/bot{TOKEN}/getUpdates', )
    debug_message("Can not connect to bot" if "false" in str(a.content) else "Connected to bot")
    BOT = telebot.TeleBot(TOKEN)


# Start message
@BOT.message_handler(commands=['start'])
def start_message(message):
    BOT.send_message(message.chat.id, 'Bot started')


# Results  variables
RESULT = []
NON_STRICT_MATCH = []
SCANED_URLS = 0

# Counter variables
TOTAL_PAGES = 0
TOTAL_PRODUCTS = 0

# Pseudo threads
SEARCH_THREAD_INDEX = 0
SEARCH_THREADS = []

# URLs array
URLS = [
    "https://biggeek.ru/catalog/apple",
    "https://biggeek.ru/catalog/tesla",
    "https://biggeek.ru/catalog/xiaomi",
    "https://biggeek.ru/sale",
    "https://biggeek.ru/catalog/samsung",
    "https://biggeek.ru/catalog/dyson",
    "https://biggeek.ru/catalog/gadgeti",
    "https://biggeek.ru/catalog/smartfony",
    "https://biggeek.ru/catalog/odezhda",
    "https://biggeek.ru/catalog/aksessuary",
    "https://biggeek.ru/catalog/akusitcheskie-sistemi",
    "https://biggeek.ru/catalog/dlya-avto",
    "https://biggeek.ru/catalog/dlya-doma",
    "https://biggeek.ru/catalog/merch",
    "https://biggeek.ru/catalog/uslugi",
]


# get html function for parse
def get_html(url: str):
    r = requests.get(url)
    return r.text


# Adding 2 level urls to array
soup1 = bs4.BeautifulSoup(get_html("https://biggeek.ru"), "lxml")
links = soup1.find_all(class_="category-dropdown-header__sub-link")
for link in links:
    URLS.insert(0, f"https://biggeek.ru{link.get('href')}")


# Add prefix to url {example: https://biggeek.ru/catalog/merch?page=12}
def add_page_prefix(url, number):
    return f"{url}?page={number}"


# Console debug msg
def print_find_console(product):
    debug_message(f"FIND {product[0].text}")
    RESULT.append(
        [f"https://biggeek.ru/{product[0].get('href')}",
         product[0].text.strip(),
         product[1].text.strip()])


# converting parsed price to int
def convert_price_to_int(price):
    return int(price.replace("₽", "").replace(" ", ""))


# Main function
@BOT.message_handler(commands=['track'])
def init_bot(message):
    # Import variables from global
    global SEARCH_THREAD_INDEX
    global SEARCH_THREADS

    # Threads manipulating
    SEARCH_THREAD_INDEX += 1
    SEARCH_THREADS.append([f"Поток-{SEARCH_THREAD_INDEX}", 0, 0])

    # Start thread msg to telegram
    BOT.send_message(message.chat.id, f"НАЧАТ ПОТОК - {SEARCH_THREAD_INDEX}")

    # Console debug msg
    debug_message(f"START THREAD - {SEARCH_THREAD_INDEX}")
    while True:
        # Parse all urls from arr
        for url in URLS:
            # Import var from global
            global SCANED_URLS

            # Console debug msg
            debug_message(f"NEW URL: {url}")
            debug_message(f"SCANNED URLS: {SCANED_URLS}")

            # Parsing url pages {range(100000) is example value, it can be anything}
            for urlPageIndex in range(100000):

                # Variable for counting searched pages
                global TOTAL_PAGES
                TOTAL_PAGES += 1

                # Threads manipulating
                SEARCH_THREADS[SEARCH_THREAD_INDEX - 1][1] += 1

                # index for counting
                urlPageIndex += 1

                # products array
                products = []

                # break from cycle if find all products
                if len(RESULT) == 3:
                    break

                # BeautifulSoup class creating
                soup = BeautifulSoup(
                    # get html from page
                    get_html(
                        # adding prefix to url
                        add_page_prefix(
                            url,
                            urlPageIndex)
                    ),
                    # parser format
                    "lxml")
                # finding all products names and prices
                names = soup.find_all("a", class_="catalog-card__title")
                prices = soup.find_all(class_="cart-modal-count")

                # if page is empty break from cycle
                if names == [] and prices == []:
                    break

                # Exception for break {only https://biggeek.ru special}
                if add_page_prefix(url, urlPageIndex) == "https://biggeek.ru/catalog/uslugi?page=2":
                    break

                # append products to array for easier manipulations
                for i in range(len(names)):
                    # {example: [PlayStation 5, 100 ₽]}
                    products.append([names[i], prices[i]])

                # checking all products on page
                for product in products:
                    # variable for counting scanned products
                    global TOTAL_PRODUCTS
                    TOTAL_PRODUCTS += 1

                    # Threads manipulating
                    SEARCH_THREADS[SEARCH_THREAD_INDEX - 1][2] += 1

                    # Check if name in product name
                    if (config.CONDITION_1[0] in product[0].text.strip()) or (config.CONDITION_2[0] in product[0].text.strip()) or (
                            config.CONDITION_3[0] in product[0].text.strip()):

                        # check if price equal CONDITION_1 price
                        # ONLY FOR CONDITION WITH SAME PRICE
                        # if conditions price is not equal just copy code near
                        if product[1].text.strip() == config.CONDITION_1[1]:
                            # debug msg
                            print_find_console(product)

                            # telegram find message
                            BOT.send_message(message.chat.id,
                                             # {example: НАЙДЕНО HomePod mini ЗА 100 ₽}
                                             f"❗❗❗НАЙДЕНО {product[0].text} ЗА {product[1].text} "
                                             # link
                                             f"\n https://biggeek.ru/{product[0].get('href')}")

                            # break from cycle if find product
                            break

                        # unstrict find
                        # product[0].text[0:4].lower() != 'игра' is clearing unstrict, but only for default condition
                        elif convert_price_to_int(config.CONDITION_1[1]) \
                                <= \
                                convert_price_to_int(product[1].text) \
                                and \
                                product[0].text[0:4].lower() != 'игра':

                            # Debug msg
                            debug_message(f"UN-STRICT-FIND {product[0].text}")

                            # Appending product to NON_STRICT_MATCH
                            NON_STRICT_MATCH.append(
                                [f"https://biggeek.ru/{product[0].get('href')}",
                                 product[0].text.strip(),
                                 product[1].text.strip()])

            SCANED_URLS += 1

        # switch SCANED_URLS to 0 because scaned all urls
        SCANED_URLS = 0
        debug_message("❗❗❗URLS END❗❗❗")


# TELEGRAM COMMAND PROCESSING SECTION

@BOT.message_handler(commands=['notstrict'])
def print_not_strict_match(message):
    result = ""
    for match in NON_STRICT_MATCH:
        result += str(match) \
                      .replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n\n"
    if result != "":
        BOT.send_message(message.chat.id, result)
    else:
        BOT.send_message(message.chat.id, "Ничего не найдено")


# Show scaned urls
@BOT.message_handler(commands=['url'])
def print_current_url(message):
    BOT.send_message(message.chat.id, f"{URLS[SCANED_URLS]} - {SCANED_URLS} \n\n"
                                      f"Осталось: {len(URLS) - SCANED_URLS}")


# Show scaned products
@BOT.message_handler(commands=['products'])
def print_total_products(message):
    BOT.send_message(message.chat.id, f"Scanned: {TOTAL_PRODUCTS}")


# Show scaned pages
@BOT.message_handler(commands=['pages'])
def print_total_pages(message):
    BOT.send_message(message.chat.id, f"Scanned: {TOTAL_PAGES}")


"""
Threads work poorly and you can run a maximum of one,
if you try more, the bot will simply stop responding to commands.
Therefore, everything related to them can be simply deleted if desired).
"""


# Show threads
@BOT.message_handler(commands=['threads'])
def print_search_thread_index(message):
    BOT.send_message(message.chat.id,
                     f"""
        Текущие
        потоки:
        {str(SEARCH_THREADS)
                     .replace("[", "")
                     .replace("]", "")
                     .replace("'", "")
                     .replace(",", "")}\n\n""")


# for non-stoppable script work
try:
    BOT.polling(none_stop=True)
except telebot.apihelper.ApiTelegramException:
    print("Check the validity of the token in TOKEN.txt")
# Debug msg
debug_message("PROJECT END")
