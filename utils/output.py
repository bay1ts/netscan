import sys
from datetime import datetime
from multiprocessing import Queue
from threading import Thread
from tqdm import tqdm

time_format = "%Y/%m/%d %H:%M:%S"
simple_output_format = "[{time}]     {message}"
target_output_format = "[{time}]     {target:50} {message}"
http_output_format =   "[{time}]     {target:50} {code}   {server:40} {title}"
dns_output_format =   "[{time}]     {target:30} {query_type:5}   {resolved}"
port_service_output_format =   "[{time}]     {target:30} {service:30} {version}"

class Output:

    @classmethod
    def setup(self):
        self.output_queue = Queue()

        self.output_thread = Thread(target=self.output_worker, args=(self.output_queue,))
        self.output_thread.daemon = True
        self.output_thread.start()

    @classmethod
    def stop(self):
        self.output_queue.put(None)
        self.output_thread.join()
        self.output_queue.close()
        self.output_queue.cancel_join_thread()

    @classmethod
    def write(self, message):
        self.output_queue.put(message)

    @classmethod
    def output_worker(self, output_queue):
        while True:
            message = output_queue.get()
            if message == None:
                break

            if type(message) == str:
                message = {'message': message}

            if not 'time' in message:
                now = datetime.now()
                message['time'] = now.strftime(time_format) 

            if 'message_type' in message and message['message_type'] == 'http':
                output_format = http_output_format
            elif 'message_type' in message and message['message_type'] == 'dns':
                output_format = dns_output_format
            elif 'message_type' in message and message['message_type'] == 'port_service':
                output_format = port_service_output_format
            elif 'target' in message:
                output_format = target_output_format
            else:
                output_format = simple_output_format

            tqdm.write(output_format.format(**message))
            sys.stdout.flush()