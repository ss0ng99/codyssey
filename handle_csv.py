import csv
import pickle

file_path = 'files/Mars_base_Inventory_list.csv'
mars_base_list = []

with open(file_path, 'r', encoding='utf-8') as file:
  reader = csv.reader(file) #csv 파일 읽기
  for row in reader:
    mars_base_list.append(row)

# 리스트 출력
def print_file(list):
  for item in mars_base_list:
    print(item)

# 인화성에 따라 정렬
def sort_flammability(list):
  sort_flamm = sorted(list, key=lambda item: item[-1], reverse=True)
  return sort_flamm

# 인화성 지구 0.7이상 분류
def filter_flammability(list):
  dangerous_item = []
  for item in list[1:]:
    item[-1] = float(item[-1])
    if(item[-1] > 0.7):
      dangerous_item.append(item)

  return dangerous_item

sort_list = sort_flammability(mars_base_list)

print('------ 원본 ------\n')
print(mars_base_list)

print('\n\n------ 위험 물품 목록 ------\n')
dagerous_list = filter_flammability(sort_list)
print(dagerous_list)

# 위험 물품 목록 새로운 csv 파일로 저장
with open('files/Mars_Base_Inventory_danger.csv', 'w', encoding="utf-8", newline="") as file:
  writer = csv.writer(file)
  writer.writerows(dagerous_list)  # 필터링된 데이터 쓰기



# 파일 읽기 및 리스트 변환
binary_inventory = []

with open(file_path, "r", encoding="utf-8") as file:
  reader = csv.reader(file)
  for row in reader:
    binary_inventory.append(row)

# 이진 파일로 저장
with open("files/Mars_Base_Inventory_List", "wb") as bin_file:
  pickle.dump(binary_inventory, bin_file)

# 이진 파일로부터 데이터 읽기
with open("files/Mars_Base_Inventory_List", "rb") as bin_file:
  binary_list = pickle.load(bin_file)

# 이진 파일로부터 읽은 데이터 출력
print('\n\n------ 이진 파일 형식 데이터 ------\n')
for item in binary_list:
    print(item)
