from time import sleep
import asyncio

mylist=range(10)

async def vessel():
	for i in range(10):
		print(mylist.pop(0))
		sleep(1)
