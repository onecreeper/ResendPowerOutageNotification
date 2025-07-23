import time
import os

HEARTBEAT_FILE_A = "/data/heartbeat_a.log"
HEARTBEAT_FILE_B = "/data/heartbeat_b.log"
HEARTBEAT_INTERVAL = 60  # 秒

print("--- 后台任务：心跳服务已启动---")
use_file_a = True

while True:
    target_file = HEARTBEAT_FILE_A if use_file_a else HEARTBEAT_FILE_B
    try:
        os.makedirs("/data", exist_ok=True)
        with open(target_file, 'w') as f:
            f.write(str(int(time.time())))
    except Exception as e:
        print(f"心跳错误：更新文件 {target_file} 失败: {e}")
    
    use_file_a = not use_file_a
    time.sleep(HEARTBEAT_INTERVAL)
