from queue import Queue
from enum import Enum
from uuid import UUID, uuid4
import threading
import os
from time import sleep
from prettytable import PrettyTable
from secrets import token_urlsafe


CHECK_REQUESTS_INTERVAL = 3
CREATE_REQUEST_INTERVAL = 3
CLEAR_PROCESSED_REQUEST_INTERVAL = 3


class RequestStatus(str, Enum):
    PROCESSED = "processed"
    UNPROCESSED = "unprocessed"


class AppMode(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"


class Request:
    def __init__(
        self,
        name: str,
        state: RequestStatus = RequestStatus.UNPROCESSED,
    ) -> None:
        self.id = uuid4()
        self.state = state
        self.name = name

    def process(self):
        self.state = RequestStatus.PROCESSED


class App:
    def __init__(
        self,
        initial_requests: list[Request] = list(),
        mode: AppMode = AppMode.AUTO,
        auto_remove: bool = True,
    ) -> None:
        self.__threads: list[threading.Thread] = []
        self.__requests: list[Request] = []
        self.__queue = Queue()
        self._mode = mode
        self._auto_remove = auto_remove
        self._run = True
        for request in initial_requests:
            self.__requests.append(request)
            self.__queue.put(request)

    def run(self):
        print("App is ready to run...")
        print(
            """
Help Section:
 - exit: Exit App
 - print_all_requests: Shows table of requests
 - print_complete_requests: Shows table of processed requests              
"""
        )
        self.__threads.append(threading.Thread(target=self.__process_requests))
        self.__threads.append(threading.Thread(target=self.__get_new_requests))
        if self._mode == AppMode.AUTO:
            self.__threads.append(threading.Thread(target=self.__auto_requests))
        if self._auto_remove:
            self.__threads.append(threading.Thread(target=self.__remove_processed))
        for thread in self.__threads:
            thread.start()
        for thread in self.__threads:
            thread.join()

    def stop(self):
        self._run = False
        os._exit(1)

    def __process_requests(self):
        while self._run:
            request = self.__queue.get()
            sleep(CHECK_REQUESTS_INTERVAL)
            request.process()

    def __get_new_requests(self):
        while self._run:
            request_name = input("Enter Request name: ")
            if request_name == "exit":
                self.stop()
            elif request_name == "print_all_requests":
                self.__print_complete_requests()
                continue
            elif request_name == "print_complete_requests":
                self.__print_complete_requests(completed=True)
                continue
            request = Request(name=request_name)
            self.__requests.append(request)
            self.__queue.put(request)
            print(f"Request '{request.name}' will be processed soon")

    def __print_complete_requests(self, completed: bool = False):
        table = PrettyTable()
        table.field_names = ("id", "name", "status")
        requests: list[Request]
        if completed:
            requests = [
                request
                for request in self.__requests
                if request.state == RequestStatus.PROCESSED
            ]
        else:
            requests = self.__requests.copy()
        for request in requests:
            table.add_row((str(request.id), request.name, request.state.value))
        print(table)

    def __auto_requests(self):
        while self._run:
            request = Request(name=token_urlsafe(8))
            self.__requests.append(request)
            self.__queue.put(request)
            sleep(CREATE_REQUEST_INTERVAL)

    def __remove_processed(self):
        while self._run:
            self.__requests = [
                request
                for request in self.__requests
                if request.state != RequestStatus.PROCESSED
            ]
            sleep(CLEAR_PROCESSED_REQUEST_INTERVAL)


app = App()

if __name__ == "__main__":
    app.run()
