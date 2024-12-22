import heapq
import logging
import threading
import time

from app.llm import llm_answer_delay_msg
from app.messaging import send_message

logger = logging.getLogger(__name__)


class DelayQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def add_delay_task(self, qq, delay_msg, delay_time):
        execute_time = time.time() + delay_time
        task = {
            'qq': qq,
            'delay_msg': delay_msg
        }
        with self.condition:
            heapq.heappush(self.queue, (execute_time, task))
            self.condition.notify()
        logger.info(f'添加延迟队列任务: {delay_msg}, 将于 {delay_time} 秒后执行.')

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
                    qq = task['qq']
                    delay_msg = task['delay_msg']
                    logger.info(
                        f'Executing task: {task} at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                    answer = llm_answer_delay_msg(qq, delay_msg)
                    send_message(qq, answer)
                except Exception as e:
                    logger.error(f"Worker encountered an error: {e}", exc_info=True)

        threading.Thread(target=worker, daemon=True, name="DelayQueueWorker").start()


delay_queue = DelayQueue()
# 启动队列工作线程
delay_queue.start_worker()
