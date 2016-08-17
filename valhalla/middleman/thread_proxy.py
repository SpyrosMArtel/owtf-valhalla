import threading
from .task_thread import TaskThread

class ThreadProxy():
    def __init__(self):
        self.threads = []

    def create_service(self, thread_id, output_list):
        """ creates a new :class:`.TaskThread`.
            :param thread_id The thread identifier
            :returns TaskThread
        """
        # TODO: check if thread exists and restart it.
        thread = self.get_thread_data(thread_id)
        if thread == None:
            thread = TaskThread(thread_id, output_list)
            self.threads.append(thread)

        return thread

    def get(self, thread_id):
        """ Retrieves the thread identified by the thread_id.
            :param thread_id The thread identifier
            :returns TaskThread
        """
        # for thread in threading.enumerate():
        #     if thread.getName() == thread_id:
        #         return thread
        for thread in self.threads:
            if thread.getName() == thread_id:
                return thread

        return None

    def get_thread_data(self, thread_id):
        """ Retrieves the thread local variables identified by the thread_id.
            :param thread_id The thread identifier
        """
        thread = self.get(thread_id)
        return thread.get_data()

    def execute(self, thread_id):
        thread = self.get(thread_id)
        thread.execute()

    def add_task(self, thread_id, task):
        """ Adds tasks to a specified thread, if it is alive.
            :param thread_id The thread identifier
            :param task The task to carry out
            :returns None
        """
        thread = self.get(thread_id)
        thread.add_task(task)