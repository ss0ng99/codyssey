import random
import time
import json
import os
import platform

class DummySensor:
  def __init__(self):
    self.env_values = {
      "mars_base_internal_temperature": 0.0,
      "mars_base_external_temperature": 0.0,
      "mars_base_internal_humidity": 0.0,
      "mars_base_external_illuminance": 0.0,
      "mars_base_internal_co2": 0.0,
      "mars_base_internal_oxygen": 0.0
    }

  def set_env(self):
    self.env_values["mars_base_internal_temperature"] = random.uniform(18, 30)
    self.env_values["mars_base_external_temperature"] = random.uniform(0, 21)
    self.env_values["mars_base_internal_humidity"] = random.uniform(50, 60)
    self.env_values["mars_base_external_illuminance"] = random.uniform(500, 715)
    self.env_values["mars_base_internal_co2"] = random.uniform(0.02, 0.1)
    self.env_values["mars_base_internal_oxygen"] = random.uniform(4, 7)

  def get_env(self):
    return self.env_values

class MissionComputer:
  def __init__(self, sensor):
    self.env_values = {}
    self.sensor = sensor
    self.history = []
    self.stop_flag = False
    self.config = self.load_config()

  def load_config(self):
    config = {
      "system_info": True,
      "system_load": True
    }
    if os.path.exists("setting.txt"):
      with open("setting.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
          key, value = line.strip().split('=')
          config[key.strip()] = value.strip().lower() == 'true'
    return config

  def get_mission_computer_info(self):
    if not self.config.get("system_info", False):
      return

    info = {
      "os": platform.system(),
      "os_version": platform.version(),
      "cpu_type": platform.processor(),
      "cpu_cores": os.cpu_count(),
      "memory": self.get_memory_info()
    }

    print("Mission Computer Info:")
    print(json.dumps(info, indent=4))

  def get_memory_info(self):
    try:
      if platform.system() == "Windows":
        # Windows에서 메모리 정보를 가져오기 위해 psutil 사용
        import psutil
        memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)
        return f"{memory:.2f} GB"
      elif platform.system() == "Linux" or platform.system() == "Darwin":  # Linux/Unix 계열
        total_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 3)
        return f"{total_memory:.2f} GB"
      else:
        return "N/A"
    except Exception as e:
      return f"Error retrieving memory info: {str(e)}"

  def get_mission_computer_load(self):
    if not self.config.get("system_load", False):
      return

    cpu_usage = self.get_cpu_usage()
    memory_usage = self.get_memory_usage()

    load_info = {
      "cpu_usage_percent": cpu_usage,
      "memory_usage_percent": memory_usage
    }
    print("Mission Computer Load Info:")
    print(json.dumps(load_info, indent=4))

  def get_cpu_usage(self):
    cpu_idle_before = os.times()[4]  
    time.sleep(1) 
    cpu_idle_after = os.times()[4]  
    total_cpu_time = os.times()[0] + os.times()[1] + os.times()[2] + os.times()[3]  # 총 CPU 사용 시간
    cpu_usage = (cpu_idle_before - cpu_idle_after) / total_cpu_time * 100
    return 100 - cpu_usage  # CPU 사용량 계산

  def get_memory_usage(self):
    if platform.system() == "Windows": # 윈도우 계열열
      import psutil
      total_memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)
      used_memory = (psutil.virtual_memory().total - psutil.virtual_memory().available) / (1024 * 1024 * 1024)
      return (used_memory / total_memory) * 100  # 메모리 사용량 퍼센트
    elif platform.system() == "Linux" or platform.system() == "Darwin":  # Linux/Unix 계열
      total_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 3)
      used_memory = total_memory - (os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES') / (1024. ** 3))
      return (used_memory / total_memory) * 100  # 메모리 사용량 퍼센트
    else:
      return "N/A"

  def get_sensor_data(self):
    while not self.stop_flag:
      self.sensor.set_env()
      self.env_values = self.sensor.get_env()

      print("Current Sensor Data:")
      print(json.dumps(self.env_values, indent=4))

      # 5분 평균 출력
      self.history.append(self.env_values)
      if len(self.history) == 60:
        self.print_avg_data()
        self.history = []

      # 5초마다 반복
      time.sleep(5)

      # 사용자 입력 확인
      if self.stop_flag:
        break

  def print_avg_data(self):
    avg_values = {
      "mars_base_internal_temperature": 0.0,
      "mars_base_external_temperature": 0.0,
      "mars_base_internal_humidity": 0.0,
      "mars_base_external_illuminance": 0.0,
      "mars_base_internal_co2": 0.0,
      "mars_base_internal_oxygen": 0.0
    }

    for entry in self.history:
      for key in avg_values:
        avg_values[key] += entry[key]

    # 평균 계산
    for key in avg_values:
      avg_values[key] /= len(self.history)

    print("5-Minute Average Sensor Data:")
    print(json.dumps(avg_values, indent=4))

  def stop(self):
    self.stop_flag = True
    print("System stopped...")


ds = DummySensor()
runComputer = MissionComputer(ds)

try:
  runComputer.get_mission_computer_info()
  runComputer.get_mission_computer_load()
  print('--------------- If you want stop it, plese input Ctrl+C ---------------')
  runComputer.get_sensor_data()
except KeyboardInterrupt:
  runComputer.stop()
