import asyncio


async def my_promise():
    await asyncio.sleep(2)
    return "Shantanu Shubham"


def add_two_numbers(a, b):
    return a + b


async def main():
    task = asyncio.create_task(my_promise())

    task.add_done_callback(lambda t: print(f"The name is: {t.result()}"))

    total = add_two_numbers(5, 6)
    print(f"The sum is: {total}")

    await task


asyncio.run(main())
