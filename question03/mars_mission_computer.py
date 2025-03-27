import random
import datetime

seed = 12345  # 초기값(Seed) - 변경하면 난수의 패턴이 달라짐

def lcg(min, max):
  global seed
  a = 1103515245  # 곱셈 상수
  c = 12345  # 덧셈 상수
  m = 2**31  # 모듈러 값 (2의 거듭제곱 사용)

  #lcg 알고리즘 변형
  # 객체의 메모리 주소를 이용해 seed 설정 seed 값 변경을 위함
  seed = (a * seed + c + id(seed)) % m 

  return min + (seed % (max - min + 1))

def get_random_number(min, max):
  return lcg(min, max)

class DummySensor: 
  def __init__(self):
    self.env_values = {
      'mars_base_internal_temperature': 0,
      'mars_base_external_temperature': 0,
      'mars_base_internal_humidity': 0,
      'mars_base_external_illuminance': 0,
      'mars_base_internal_co2': 0,
      'mars_base_internal_oxygen': 0
    }
  
  def set_env(self):
    self.env_values['mars_base_internal_temperature'] = get_random_number(18,30)
    self.env_values['mars_base_external_temperature'] = get_random_number(0,21)
    self.env_values['mars_base_internal_humidity'] = get_random_number(50, 60)
    self.env_values['mars_base_external_illuminance'] = get_random_number(500, 715)
    self.env_values['mars_base_internal_co2'] = get_random_number(0.02, 0.1)
    # self.env_values['mars_base_internal_oxygen'] = get_random_number(4, 7)
    self.env_values["mars_base_internal_oxygen"] = random.uniform(4, 7)

  def get_env(self):
    self.log_env_data()
    return self.env_values

  def log_env_data(self):
    log_filename = "logs/mars_base_log.txt"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
    with open(log_filename, "a") as log_file:
      log_file.write(f"{current_time} - ")
      log_file.write(f"Internal Temperature: {self.env_values['mars_base_internal_temperature']:.2f} °C, ")
      log_file.write(f"External Temperature: {self.env_values['mars_base_external_temperature']:.2f} °C, ")
      log_file.write(f"Internal Humidity: {self.env_values['mars_base_internal_humidity']:.2f} %, ")
      log_file.write(f"External Illuminance: {self.env_values['mars_base_external_illuminance']:.2f} W/m2, ")
      log_file.write(f"Internal CO2: {self.env_values['mars_base_internal_co2']:.2f} %, ")
      log_file.write(f"Internal Oxygen: {self.env_values['mars_base_internal_oxygen']:.2f} %\n")

ds = DummySensor()

ds.set_env()
env_data = ds.get_env()

print(env_data)