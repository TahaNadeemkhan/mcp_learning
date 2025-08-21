import asyncio
from contextlib import asynccontextmanager
from contextlib import AsyncExitStack



# @asynccontextmanager
# async def make_connection(name):
#     print(f"Making connection... {name}")
#     yield name
#     print(f"Connected {name}!")


# async def main():
#     async with make_connection("My connection") as connection:
#         print("Using conencion", {connection})
#         await asyncio.sleep(1)



async def make_connection(name):
    class Ctx():
        async def __aenter__(self):
            print(f"Connecting...{name}")
            return name
        async def __aexit__(self, *args):
            print(f"Connected...{name}")
    return Ctx()

async def main():
    async with AsyncExitStack() as stack:   
            a = await stack.enter_async_context(await make_connection("A"))
            b = await stack.enter_async_context(await make_connection("B"))
            print(f"Making connection of {a} and {b}...")
        

asyncio.run(main())