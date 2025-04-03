import random
import time
import json

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

  def get_sensor_data(self):
    while not self.stop_flag:
      self.sensor.set_env()
      self.env_values = self.sensor.get_env()

      # 현재 시간으로 환경 값 출력
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
RunComputer = MissionComputer(ds)

try:
  RunComputer.get_sensor_data()
except KeyboardInterrupt:
  # Ctrl+C 입력 시 stop 메소드 호출출
  RunComputer.stop()
