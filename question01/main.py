import re

file_path = 'logs/mission_computer_main.log'

# 로그 파일을 열고 내용 배열 형식으로 저장
def read_file(file_path):
  log_lines = []
  try:
    with open(file_path, 'r') as file:
      logs = file.readlines()
      for log in logs:
        log_lines.append(log)
    return log_lines
  except:
    return 'No such file or directory'
  
# 로그 파일 열고 내용 오브젝트 형식으로 저장
def read_file_dictionary(file_path):
  dictionary_lines = []
  try:
    with open(file_path, 'r') as file:
      for line in file:
        line = line.strip()
        if line:
          lines = line.split(',')
          dictionary_lines.append({
            'timestamp': lines[0],
            'event': lines[1],
            'message': lines[2]
          })
    return dictionary_lines
  except:
    return 'No such file or directory'
  
# 시간 역순으로 출력
def print_revers(logs):
  for log in reversed(logs):
    print(log)

logs = read_file(file_path)
logs_dictionary = read_file_dictionary(file_path)

# 로그파일 마크다운 형식으로 변환
def generate_markdown_report(logs_dictionary):
  md_content = "# Log Report \n\n"
  md_content += "| Timestamp | Event | Message |\n"
  
  for item in logs_dictionary[1:]:
    md_content += f"| {item['timestamp']} | {item['event']} | {item['message']} |\n"
  return md_content

# 보고서 파일 저장
def save_markdown_report(md_content, output_file):
  with open(output_file, 'w', encoding='utf-8') as file:
    file.write(md_content)

report = generate_markdown_report(logs_dictionary)
save_markdown_report(report, 'log_analysis.md')