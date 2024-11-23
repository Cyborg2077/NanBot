import heapq
import time
import threading
import logging
from logging_config import setup_logging

setup_logging()  # 设置日志

logger = logging.getLogger(__name__)


class DelayQueue:

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def add_task(self, task, delay):
        execute_time = time.time() + delay
        with self.condition:
            heapq.heappush(self.queue, (execute_time, task))
            self.condition.notify()
        logger.info(f'Task added: {task}, will run after {delay} seconds.')

    def get_task(self):
        with self.condition:
            while True:
                if self.queue:
                    execute_time, task = self.queue[0]
                    current_time = time.time()

                    if current_time >= execute_time:
                        heapq.heappop(self.queue)
                        return task
                    else:
                        self.condition.wait(timeout=execute_time - current_time)
                else:
                    self.condition.wait()

    def start_worker(self):
        def worker():
            while True:
                try:
                    task = self.get_task()
                    logger.info(f'Executing task: {task} at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                except Exception as e:
                    logger.error(f"Worker encountered an error: {e}", exc_info=True)

        threading.Thread(target=worker, daemon=True, name="DelayQueueWorker").start()


if __name__ == '__main__':
    queue = DelayQueue()
    queue.start_worker()
    queue.add_task('task1', 5)
    queue.add_task('task2', 3)
    queue.add_task('task3', 7)

    while True:
        time.sleep(1)
