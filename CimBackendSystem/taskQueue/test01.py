from taskQueue import TaskQueue
from task import Task
from PIL import Image
import io

# 创建 TaskQueue 实例
task_queue = TaskQueue(maxsize=10)

# 创建一些 Task 对象
image_data = io.BytesIO()  # 示例图片数据
image = Image.new('RGB', (100, 100), color = 'red')
image.save(image_data, format='JPEG')
image_data.seek(0)

task1 = Task(image=image_data, Cameraid=1, location="Location A")
task2 = Task(image=image_data, Cameraid=2, location="Location B")

# 入队操作
task_queue.enqueue(task1)
task_queue.enqueue(task2)

# 出队操作
dequeued_task1 = task_queue.dequeue()
dequeued_task2 = task_queue.dequeue()

# 打印队列状态
print(f"Queue size after dequeue: {task_queue.size()}")
