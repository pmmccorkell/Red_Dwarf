import mocap
from threading import Thread
from time import sleep
import concurrent.futures
import asyncio
from multiprocessing import Process, Queue

# a=mocap.Motion_Capture()

# def start_mocap():
	#1
	# asyncio.ensure_future(a.connect())	
	# asyncio.get_event_loop().run_forever()

	#2
	# some_future = asyncio.get_event_loop().create_future()
	# asyncio.get_event_loop().run_until_complete(some_future)

	#3
	# global some_await
	# some_await = asyncio.create_task(a.connect())


# async def main():
def main():
	# global some_await
	# mocap_thread = Thread(target=mocap.stream_data)
	# mocap_thread.start()
	# mocap_thread.start()

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	# mocap_process = executor.submit(a.start)
	# start_mocap()

	mocap.stream_data()


	print('got past asyncio')


	while(1):
		sleep(1)
		print('data: '+str(mocap.data_in))
	# await some_await


main()
# asyncio.run(main())