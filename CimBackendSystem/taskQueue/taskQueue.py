import queue

from logManager.log import taskQueueLogger
class TaskQueue:
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)


    def enqueue(self, task):
        try:
            self.queue.put(task, block=True, timeout=5)
            print(f"Task {task} enqueued.")
            taskQueueLogger.info(f"Task {task} enqueued.")
        except queue.Full:
            print("Queue is full. Failed to enqueue task.")
            taskQueueLogger.info("Queue is full. Failed to enqueue task.")

    def dequeue(self):
        try:
            task = self.queue.get(block=True, timeout=5)
            print(f"Task {task} dequeued.")
            taskQueueLogger.info(f"Task {task} dequeued.")
            return task
        except queue.Empty:
            print("Queue is empty. Failed to dequeue task.")
            taskQueueLogger.info("Queue is empty. Failed to dequeue task.")
            return None

    def size(self):
        return self.queue.qsize()

    def is_empty(self):
        return self.queue.empty()
