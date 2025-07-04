import aiohttp


async def get_ltc_usd_price() -> float:
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["litecoin"]["usd"]
