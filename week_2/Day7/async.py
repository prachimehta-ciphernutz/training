import asyncio
import time

async def api_call(i):
    print(f"Calling API {i}")
    await asyncio.sleep(2)
    return f"Response {i}"

async def main():
    start = time.time()
    tasks = [api_call(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    end = time.time()
    print(results)
    print("Total time:", round(end-start, 2), "seconds")

asyncio.run(main())