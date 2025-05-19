import zipfile
import itertools
import string
import time
from multiprocessing import Process, Value, Array, cpu_count

CHARSET = string.digits + string.ascii_lowercase
ZIP_PATH = "question08/test2.zip"
BLOCK_SIZE = 1
TOTAL_LENGTH = 2

def generate_two_char_combinations():
  return [''.join(p) for p in itertools.product(CHARSET, repeat=BLOCK_SIZE)]

def try_passwords_block1(block1_list, found_flag, result_array):
  block2_list = generate_two_char_combinations()
#   block3_list = generate_two_char_combinations()

  try:
    with zipfile.ZipFile(ZIP_PATH) as zf:
      for block1 in block1_list:
        for block2 in block2_list:
        #   for block3 in block3_list:
            if found_flag.value:
              return
            password = block1 + block2 
            try:
              zf.extractall(pwd=password.encode('utf-8'))
              found_flag.value = True
              for i, c in enumerate(password):
                result_array[i] = ord(c)
              return
            except:
              continue
  except FileNotFoundError:
    print(f"❌ File '{ZIP_PATH}' not found.")
  except zipfile.BadZipFile:
    print(f"❌ Invalid ZIP file: '{ZIP_PATH}'.")

def chunkify(data, n):
  k, m = divmod(len(data), n)
  return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def unlock_zip_parallel_block():
  print(f"🔓 Starting block-based brute-force on '{ZIP_PATH}'...")
  start_time = time.time()

  block1_list = generate_two_char_combinations()
  num_workers = min(cpu_count(), len(block1_list))
  block1_chunks = chunkify(block1_list, num_workers)

  found_flag = Value('b', False)
  result_array = Array('b', TOTAL_LENGTH)

  workers = []
  for chunk in block1_chunks:
    p = Process(target=try_passwords_block1, args=(chunk, found_flag, result_array))
    workers.append(p)
    p.start()

  for p in workers:
    p.join()

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

  print(f"⏱️ Elapsed: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
  unlock_zip_parallel_block()
