import zipfile
import itertools
import string
import time
from multiprocessing import Process, Value, Queue, cpu_count

CHARSET = string.digits + string.ascii_lowercase  # '0-9a-z'
ZIP_PATH = "question08/emergency_storage_key.zip"
TEST_ZIP_PATH = 'question08/test_zip.zip'
MAX_LENGTH = 6


def try_passwords(prefixes, found_flag, result_queue):
  with zipfile.ZipFile(ZIP_PATH) as zf:
    for prefix in prefixes:
      for suffix in itertools.product(CHARSET, repeat=MAX_LENGTH - len(prefix)):
        if found_flag.value:
          return
        password = prefix + ''.join(suffix)
        try:
          zf.extractall(pwd=password.encode('utf-8'))
          found_flag.value = True
          result_queue.put(password)
          return
        except:
          continue

def chunkify(data, n):
  """ 데이터를 n개로 나누는 유틸 함수 """
  k, m = divmod(len(data), n)
  return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def unlock_zip_parallel():
  print(f"🔓 Starting parallel brute-force on {ZIP_PATH}...")

  start_time = time.time()
  manager_flag = Value('b', False)
  result_queue = Queue()

  # 접두어 생성: 앞 2자리로 분할
  prefixes = [''.join(p) for p in itertools.product(CHARSET, repeat=2)]

  # 현재 시스템 CPU 수 확인 후 그 수만큼 작업 분할
  num_workers = cpu_count()
  print(f"🧠 Detected CPU cores: {num_workers}")

  chunks = chunkify(prefixes, num_workers)

  # 병렬 처리
  workers = []
  for chunk in chunks:
    p = Process(target=try_passwords, args=(chunk, manager_flag, result_queue))
    workers.append(p)
    p.start()

  for p in workers:
    p.join()

  if not result_queue.empty():
    password = result_queue.get()
    print(f"✅ Password found: {password}")
    with open("password.txt", "w") as f:
      f.write(password)
  else:
    print("❌ Password not found.")

  print(f"⏱️ Elapsed time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
  unlock_zip_parallel()
