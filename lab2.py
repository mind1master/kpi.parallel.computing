# The program simulates management of tasks process by CPU process with two 
# queues. Every task is putted in the first queue of a limited size. The 
# task is putted in the buffer queue if the first queue is full. Tasks are
# executed from the first queue. CPU takes tasks from the second queue only
# if the size of this queue exceeds the particular value.

from multiprocessing import Process, Lock, Queue, Event
import random
import sys
import time

from colorama import init as make_life_colorful
from colorama import Fore, Back, Style


class Task(object):
    """Task with a random execution time"""
    def __init__(self):
        self.execution_time = random.randrange(10)

    def run(self):
        """Execute task"""
        time.sleep(self.execution_time)


def generate_tasks(number, limited_queue, buffer_queue, tasks_finished):
    """Generate new task and put it the needed queue. Move tasks from buffer 
    to limited queue if possible."""
    for task in xrange(number):
        time.sleep(random.randrange(5))
        # Move tasks from buffer to limited queue if possible
        while True:
            print Fore.RESET + '\nLimited queue size - %s Buffer size - %s' % (
                limited_queue.qsize(), buffer_queue.qsize())
            if not buffer_queue.empty() and not limited_queue.full():
                task = buffer_queue.get()
                limited_queue.put(task)
            else:
                break
        # Generate new task
        if not limited_queue.full():
            print Fore.RESET + 'Adding task to limited queue...'
            limited_queue.put(Task())
        else:
            print Fore.RESET + 'Adding task to buffer...'
            buffer_queue.put(Task())
            if buffer_queue.qsize() > 3:
                print Fore.RED + 'Buffer is overloaded...'
    tasks_finished.set()
    print Fore.RED + 'Generator finished'

def run_tasks(number, limited_queue, buffer_queue, tasks_finished):
    """Execute tasks in a particular order"""
    def run_task(limited_queue, buffer_queue, execute_all=False):
        if buffer_queue.qsize() > 3:
            print Fore.GREEN + 'Task from buffer is executing'
            task = buffer_queue.get()
            task.run()
        elif execute_all and not buffer_queue.empty():
            task = buffer_queue.get()
            task.run()
        elif not limited_queue.empty():
            task = limited_queue.get()
            print Fore.GREEN + 'Task from limited queue is executing'
            task.run()
        else:
            return True

    while True:
        if not tasks_finished.is_set():
            run_task(limited_queue, buffer_queue)
        else:
            # Generator finished yielding new tasks
            finished = run_task(limited_queue, buffer_queue, True)
            if finished:
                print Fore.RED + 'CPU finished'
                break

def main(tasks):
    """Simulate CPU management of tasks process"""
    make_life_colorful(wrap=False)
    limited_queue = Queue(5)
    buffer_queue = Queue()
    tasks_finished = Event()
    generator = Process(target=generate_tasks, 
        args=(tasks, limited_queue, buffer_queue, tasks_finished))
    cpu = Process(target=run_tasks, args=(tasks, limited_queue, 
        buffer_queue, tasks_finished))
    generator.start()
    cpu.start()
    generator.join()
    cpu.join()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(tasks=int(sys.argv[1]))
    else:
        raise Exception(
            'Please specify number of tasks need to be generated.')
