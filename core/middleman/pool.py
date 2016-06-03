import threading
from Queue import Queue

class Worker(threading.Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                # we put the results in the Queue
                # that way the parent will get informed
                self.result_queue.put(func(*args, **kargs))
            except Exception, e: print e
            self.tasks.task_done()

    def set_result_queue(self, result_queue):
        self.result_queue = result_queue

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        # the most thread safe way to get the results from a thread
        # was to use another Queue
        self.result_queue = Queue(num_threads)
        self.counter_tasks = 0
        for _ in range(num_threads):
            worker = Worker(self.tasks)
            worker.set_result_queue(self.result_queue)


    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))
        self.counter_tasks += 1

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
        # after all the tasks are done, we return a list of all the results.
        # I believe it would be nice if we can make the Queue a part of views instead (just an idea)
        return [self.result_queue.get() for _ in xrange(self.counter_tasks)]
