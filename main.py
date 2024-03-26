import requests
import json
from aiogram import Bot, Dispatcher, executor, types

from config import BOT_TOKEN, API_KEY, ReferalXrocket, ReferalCrypto


# Создание объектов Bot и Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Функция для получения курсов криптовалют в USDT
async def get_crypto_prices_usdt():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }
    params = {
        'symbol': 'TON,BTC,ETH,USDT,TRX',
        'convert': 'USDT'
    }
    response = requests.get(url, headers=headers, params=params).json()

    if 'data' not in response:
        error_message = response.get('status', {}).get('error_message', 'Unknown error')
        return {'error': error_message}

    data = response['data']
    prices_usdt = {}
    for symbol, coin_data in data.items():
        prices_usdt[symbol] = coin_data['quote']['USDT']['price']
    return prices_usdt

# Функция для получения курсов криптовалют в UAH
async def get_crypto_prices_uah():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }
    params = {
        'symbol': 'TON,BTC,ETH,USDT,TRX',
        'convert': 'UAH'
    }
    response = requests.get(url, headers=headers, params=params).json()

    if 'data' not in response:
        error_message = response.get('status', {}).get('error_message', 'Unknown error')
        return {'error': error_message}

    data = response['data']
    prices_uah = {}
    for symbol, coin_data in data.items():
        prices_uah[symbol] = coin_data['quote']['UAH']['price']
    return prices_uah

# Обработчик команды /prices
@dp.message_handler(commands=['prices'])
async def prices_command(message: types.Message):
    prices_usdt = await get_crypto_prices_usdt()
    prices_uah = await get_crypto_prices_uah()

    if 'error' in prices_usdt or 'error' in prices_uah:
        error_message = prices_usdt.get('error', '') or prices_uah.get('error', '')
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
        for symbol in prices_usdt.keys():
            coin_link = coin_links.get(symbol, '')
            response_text += f'[{symbol}]({coin_link}) = '
            if symbol == 'USDT':
                response_text += f'{prices_uah[symbol]:.2f} ***UAH*** \n'
            else:
                response_text += f'{prices_usdt[symbol]:.2f} ***USDT*** / {prices_uah[symbol]:.2f} ***UAH*** \n'

        response_text += f'[Торговать криптовалютой в XRocketBot]({ReferalXrocket})\n[Торговать криптовалютой в Cryptobot]({ReferalCrypto})\n'
            

        await message.reply(response_text, parse_mode=types.ParseMode.MARKDOWN, disable_web_page_preview=True)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)