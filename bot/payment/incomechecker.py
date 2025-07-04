import aiohttp

### Проверка входящего платежа
async def check_ltc_transactions(ltc_address: str) -> list:
    url = f'https://api.blockcypher.com/v1/ltc/main/addrs/{ltc_address}?unspentOnly=true&includeScript=true'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return data.get("txrefs", [])
    except Exception as e:
        print(f"BlockCypher API error: {e}")
        return []