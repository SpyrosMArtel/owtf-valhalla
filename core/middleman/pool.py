import threading
from Queue import Queue

class TaskPool:
    def __init__(self, number_of_threads):
        self.output = Queue(maxsize=0)
        self.workers = []
        self.task_queue = Queue(maxsize=0)
        self.counter_tasks = 0
        self.number_of_threads = number_of_threads
        for i in range(number_of_threads):
            worker = threading.Thread(target=self.__worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def wait(self):
        # for tasks in self.workers:
        #     self.output.put((None,))

        self.output.join()

        return [self.output.get() for _ in range(self.counter_tasks)]

    def add_task(self, func, *args):
        """Add a task to the queue"""
        self.task_queue.put((func, args))
        self.counter_tasks += 1

    def __worker(self):
        while True:
            func, args= self.task_queue.get()
            try:
                # we put the results in the Queue
                # that way the parent will get informed
                output = func(*args)
                self.output.put(output)
                self.task_queue.task_done()
            except Exception as exception: print(exception)