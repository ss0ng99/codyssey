import zipfile
import itertools
import string
import time
from multiprocessing import Process, Value, Array, cpu_count

CHARSET = string.digits + string.ascii_lowercase
ZIP_PATH = "emergency_storage_key.zip"
MAX_LENGTH = 6

def try_passwords(prefixes, found_flag, result_array, attempts_array, worker_index):
  try:
    with zipfile.ZipFile(ZIP_PATH) as zf:
      for prefix in prefixes:
        for suffix in itertools.product(CHARSET, repeat=MAX_LENGTH - len(prefix)):
          if found_flag.value:
            return
          password = prefix + ''.join(suffix)
          try:
            zf.extractall(pwd=password.encode('utf-8'))
            found_flag.value = True
            for i, c in enumerate(password):
              result_array[i] = ord(c)
            return
          except:
            attempts_array[worker_index] += 1
  except:
    return

def monitor_progress(attempts_array, found_flag, start_time):
  total_last = 0
  while not found_flag.value:
    time.sleep(2)
    total = sum(attempts_array)
    elapsed = time.time() - start_time
    speed = (total - total_last) / 2
    print(f"🔁 Attempts: {total} | Speed: {speed:.1f} tries/sec | Elapsed: {elapsed:.1f}s")
    total_last = total

def chunkify(data, n):
  k, m = divmod(len(data), n)
  return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def unlock_zip_parallel():
  print(f"🔓 Starting parallel brute-force on '{ZIP_PATH}'...")
  start_time = time.time()

  found_flag = Value('b', False)
  result_array = Array('b', MAX_LENGTH)  # 암호 저장용 (문자마다 아스키 코드 저장)
  num_workers = cpu_count()
  attempts_array = Array('i', [0] * num_workers)

  prefixes = [''.join(p) for p in itertools.product(CHARSET, repeat=2)]
  chunks = chunkify(prefixes, num_workers)

  workers = []
  for i, chunk in enumerate(chunks):
    p = Process(target=try_passwords, args=(chunk, found_flag, result_array, attempts_array, i))
    workers.append(p)
    p.start()

  monitor = Process(target=monitor_progress, args=(attempts_array, found_flag, start_time))
  monitor.start()

  for p in workers:
    p.join()
  monitor.join()

  if found_flag.value:
    password = ''.join([chr(c) for c in result_array])
    print(f"✅ Password found: {password}")
    try:
      with open("password.txt", "w") as f:
        f.write(password)
    except IOError:
      print("❌ Failed to write password.txt")
  else:
    print("❌ Password not found.")

  print(f"⏱️ Elapsed time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
  unlock_zip_parallel()
