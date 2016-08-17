import threading
import queue
import time

class TaskThread(threading.Thread):
    locals = None

    def __init__(self, thread_id, output_list):
        threading.Thread.__init__(self, name=thread_id)
        self.tasks = queue.Queue(maxsize=0)
        self.daemon = True
        # self.start()
        self.progress = 0
        self.output_list = output_list

    def get_data(self):
        if self.progress == 0:
            return self.output_list
        else:
            return ('in progress...',)

    def execute(self):
        self.start()
        self.output_list = self.tasks.join()

    def add_task(self, task):
        self.tasks.put(task)
        self.progress = self.progress + 1

    def run(self):
        while True:
            func, task, image = self.tasks.get()
            """ just for debugging
                to see what the thread is sending
            """
            print('%s %s %s %s' % (threading.current_thread().getName(), ':', func, task))
            self.output_list.append(func(image, task))
            self.tasks.task_done()
            self.progress = self.progress - 1
