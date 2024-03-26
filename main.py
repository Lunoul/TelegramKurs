import requests
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData

from config import BOT_TOKEN, API_KEY, ReferalXrocket, ReferalCrypto


# Создание объектов Bot и Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Callback data for currency selection buttons
currency_cb = CallbackData("currency", "code")

# Default currency
default_currency = "EUR"

# Supported currencies
supported_currencies = {
    "UAH": "Ukrainian Hryvnia",
    "RUB": "Russian Ruble",
    "PLN": "Polish Złoty",
    "EUR": "Euro",
}


# Function to get cryptocurrency prices in a given currency
async def get_crypto_prices(currency):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }
    params = {
        'symbol': 'TON,BTC,ETH,USDT,TRX',
        'convert': currency
    }
    response = requests.get(url, headers=headers, params=params).json()

    if 'data' not in response:
        error_message = response.get('status', {}).get('error_message', 'Unknown error')
        return {'error': error_message}

    data = response['data']
    prices = {}
    for symbol, coin_data in data.items():
        prices[symbol] = coin_data['quote'][currency]['price']
    return prices


# Handler for /start command
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Курс 🚀'))
    keyboard.add(types.KeyboardButton('Смена основной валюты'))
    await message.reply('Привет! Я могу показать тебе курсы криптовалют.', reply_markup=keyboard)


# Handler for "Курс 🚀" button
@dp.message_handler(text='Курс 🚀')
async def prices_command(message: types.Message):
    prices = await get_crypto_prices(default_currency)

    if 'error' in prices:
        error_message = prices['error']
        await message.reply(f'Ошибка: {error_message}')
    else:
        coin_links = {
            'TON': 'https://coinmarketcap.com/currencies/toncoin/',
            'BTC': 'https://coinmarketcap.com/currencies/bitcoin/',
            'ETH': 'https://coinmarketcap.com/currencies/ethereum/',
            'TRX': 'https://coinmarketcap.com/currencies/tron/',
            'USDT': 'https://coinmarketcap.com/currencies/tether/',
        }

        response_text = ''
        for symbol in prices.keys():
            coin_link = coin_links.get(symbol, '')
            if symbol == 'USDT':
                response_text += f'[{symbol}]({coin_link}) = {prices[symbol]:.2f} ***{default_currency}*** \n'
            else:
                usdt_price = await get_crypto_prices('USDT')  # Get USDT price for comparison
                response_text += f'[{symbol}]({coin_link}) = {usdt_price[symbol]:.2f} ***USDT*** / {prices[symbol]:.2f} ***{default_currency}*** \n'

        response_text += f'\n[Торговать криптовалютой в XRocketBot]({ReferalXrocket})\n[Торговать криптовалютой в Cryptobot]({ReferalCrypto})\n'

        await message.reply(response_text, parse_mode=types.ParseMode.MARKDOWN, disable_web_page_preview=True)


# Handler for "Смена основной валюты" button
@dp.message_handler(text='Смена основной валюты')
async def change_currency_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for code, name in supported_currencies.items():
        keyboard.add(types.InlineKeyboardButton(name, callback_data=currency_cb.new(code=code)))
    await message.reply('Выберите валюту:', reply_markup=keyboard)


# Callback handler for currency selection buttons
@dp.callback_query_handler(currency_cb.filter())
async def currency_callback(query: types.CallbackQuery, callback_data: dict):
    global default_currency
    selected_currency = callback_data['code']
    default_currency = selected_currency
    await query.message.edit_text(f'Основная валюта изменена на {supported_currencies[selected_currency]}')


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)