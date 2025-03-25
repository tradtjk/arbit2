import asyncio
import ccxt.async_support as ccxt

class ArbitrageScanner:
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'bybit': ccxt.bybit(),
            'gateio': ccxt.gateio(),
            'mexc': ccxt.mexc(),
            'huobi': ccxt.huobi(),
            'bitget': ccxt.bitget(),
            'lbank': ccxt.lbank(),
            'bingx': ccxt.bingx(),
            'kucoin': ccxt.kucoin(),
            'bitmart': ccxt.bitmart()
        }
        self.pairs = ["USDT"]
        self.monitoring = False
        self.monitor_task = None

    async def scan(self):
        results = []
        tickers = {}

        for name, ex in self.exchanges.items():
            try:
                markets = await ex.load_markets()
                for symbol in markets:
                    if "/USDT" in symbol and markets[symbol]['active']:
                        ticker = await ex.fetch_order_book(symbol, limit=15)
                        buy_price, buy_volume = self.analyze_orders(ticker['asks'])
                        sell_price, sell_volume = self.analyze_orders(ticker['bids'])
                        tickers.setdefault(symbol, []).append((name, buy_price, sell_price))
            except Exception:
                continue

        for symbol, data in tickers.items():
            for buy in data:
                for sell in data:
                    if buy[0] != sell[0]:
                        profit = (sell[2] - buy[1]) / buy[1] * 100
                        if profit > 1:
                            results.append(self.format_result(symbol, buy, sell, profit))
        return results

    def analyze_orders(self, orders):
        total = 0
        usdt = 0
        for price, amount in orders:
            trade_value = price * amount
            if usdt + trade_value > 100:
                amount = (100 - usdt) / price
                total += amount
                usdt = 100
                break
            usdt += trade_value
            total += amount
        avg_price = usdt / total if total else 0
        return avg_price, usdt

    def format_result(self, symbol, buy, sell, profit):
        volume = 100
        return f"""
<b>🔁 Арбитраж найден</b>

<b>Блок 1: Покупка</b>
Пара: {symbol}
Биржа: {buy[0]}
Средняя цена: {buy[1]:.4f}
Ссылка на спот: https://www.{buy[0]}.com/en/trade/{symbol.replace("/", "_")}
Ссылка на вывод: https://www.{buy[0]}.com/en/withdraw
Объем: {volume} USDT

<b>Блок 2: Продажа</b>
Биржа: {sell[0]}
Средняя цена: {sell[2]:.4f}
Ссылка на спот: https://www.{sell[0]}.com/en/trade/{symbol.replace("/", "_")}
Ссылка на ввод: https://www.{sell[0]}.com/en/deposit
Объем: {volume} USDT

<b>Блок 3: Прибыль</b>
Чистая прибыль: {profit:.2f}% (~{profit:.2f} USDT)
Сеть: USDT (доступно)
"""

    async def start_monitoring(self, bot, chat_id):
        self.monitoring = True

        async def monitor():
            while self.monitoring:
                results = await self.scan()
                if results:
                    for res in results:
                        await bot.send_message(chat_id, res, parse_mode="HTML")
                await asyncio.sleep(60)

        self.monitor_task = asyncio.create_task(monitor())

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()