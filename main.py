import requests
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData

from config import *
from constants import *


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
# Callback data for currency selection buttons
currency_cb = CallbackData("currency", "code")

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
    await message.reply(WelcomeMessage, reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN)

# Handler for "Курс 🚀" button
@dp.message_handler(text='Курс 🚀')
async def prices_command(message: types.Message):
    prices = await get_crypto_prices(default_currency)

    if 'error' in prices:
        error_message = prices['error']
        await message.reply(f'Ошибка: {error_message}')
    else:
        response_text = ''
        for symbol in prices.keys():
            coin_link = coin_links.get(symbol, '')
            if symbol == 'USDT':
                response_text += f'[{symbol}]({coin_link}) = {prices[symbol]:.2f} ***{default_currency}*** \n'
            else:
                usdt_price = await get_crypto_prices('USDT')  # Get USDT price for comparison
                response_text += f'[{symbol}]({coin_link}) = {usdt_price[symbol]:.2f} ***USDT*** / {prices[symbol]:.2f} ***{default_currency}*** \n'

        response_text += f'\n[{ReferalMessagexRocket}]({ReferalxRocket})\n[{ReferalMessageCrypto}]({ReferalCrypto})\n'

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

@dp.message_handler(regexp=r"^[A-Z]+$")  # Match uppercase coin symbols
async def inline_rate_handler(message: types.Message):
    coin_symbol = message.text.upper()
    prices = await get_crypto_prices(default_currency)

    if 'error' in prices:
        error_message = prices['error']
        await message.reply(f'Ошибка: {error_message}')
    elif coin_symbol not in prices:
        await message.reply(f"Неизвестная монета: {coin_symbol}")
    else:
        usdt_price = await get_crypto_prices('USDT')
        response_text = f"[{coin_symbol}]({coin_links.get(coin_symbol, '')}) = {usdt_price[coin_symbol]:.2f} USDT / {prices[coin_symbol]:.2f} {default_currency}"
        await message.reply(response_text, parse_mode=types.ParseMode.MARKDOWN, disable_web_page_preview=True)

@dp.inline_handler()
async def inline_query_handler(query: types.InlineQuery):
    query_text = query.query.upper()  # Convert query to uppercase
    results = []

    if query_text:  # If there's a query, filter coins
        filtered_coins = [coin for coin in supported_coins if query_text in coin]
    else:
        filtered_coins = supported_coins  # Show all coins if no query

    for coin in filtered_coins:
        coin_link = coin_links.get(coin, '')
        result = types.InlineQueryResultArticle(
            id=coin,
            title=coin,
            url=coin_link,
            input_message_content=types.InputTextMessageContent(
                message_text=f"{coin} = ..."  # Placeholder for rate
            )
        )
        results.append(result)

    await query.answer(results, cache_time=1)  # Cache results for 1 second

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)