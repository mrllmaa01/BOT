import asyncio
import aiohttp
import time

TELEGRAM_IPS = [
    "149.154.167.51",
    "149.154.167.91", 
    "149.154.171.5",
    "91.108.56.0",
    "91.108.56.1",
    "91.108.56.2",
    "91.108.56.3",
    "91.108.56.4",
    "api.telegram.org"  # контрольный
]

async def test_ip(ip):
    start = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{ip}", timeout=5) as resp:
                elapsed = time.time() - start
                print(f"✅ {ip}: {elapsed:.2f}с (статус: {resp.status})")
                return elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ {ip}: {elapsed:.2f}с - {str(e)[:30]}")
        return None

async def main():
    print("🔍 Тестируем IP-адреса Telegram...")
    print("="*50)
    
    fastest = None
    fastest_time = float('inf')
    
    for ip in TELEGRAM_IPS:
        t = await test_ip(ip)
        if t and t < fastest_time:
            fastest_time = t
            fastest = ip
    
    print("="*50)
    if fastest:
        print(f"\n⚡ Самый быстрый IP: {fastest} ({fastest_time:.2f}с)")
        print("\n👉 Добавь в hosts файл:")
        print(f"   {fastest} api.telegram.org")
    else:
        print("❌ Не удалось найти рабочий IP")

if __name__ == "__main__":
    asyncio.run(main())