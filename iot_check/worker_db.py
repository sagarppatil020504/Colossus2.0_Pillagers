import threading
import queue

# Task queue for database operations
task_queue = queue.Queue()

# 🔹 Background Worker to Process Firebase Tasks
def db_worker():
    while True:
        task = task_queue.get()
        if task is None:
            break  # Graceful shutdown
        try:
            task()  # Execute the queued task
        except Exception as e:
            print(f"⚠️ Database Error: {e}")
        finally:
            task_queue.task_done()

# 🔹 Start Worker Thread
worker_thread = threading.Thread(target=db_worker, daemon=True)
worker_thread.start()

def add_task(task):
    """ Adds a task to the queue """
    task_queue.put(task)

def stop_worker():
    """ Gracefully stops the worker thread """
    task_queue.put(None)
    worker_thread.join()
    print("🔌 Database Worker Stopped!")
