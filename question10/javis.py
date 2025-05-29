import os
import datetime
import sounddevice as sd
import scipy.io.wavfile as wavfile


def ensure_records_folder():
  if not os.path.exists('records'):
    os.makedirs('records')


def get_current_timestamp():
  now = datetime.datetime.now()
  return now.strftime('%Y%m%d-%H%M%S')


def record_voice(duration_seconds=5, sample_rate=44100):
  print('녹음 시작...')
  audio = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
  sd.wait()
  print('녹음 완료.')
  return audio, sample_rate


def save_recording(audio, sample_rate):
  ensure_records_folder()
  filename = get_current_timestamp() + '.wav'
  filepath = os.path.join('records', filename)
  wavfile.write(filepath, sample_rate, audio)
  print('저장됨:', filepath)


def list_recordings_by_date(start_date, end_date):
  """
  날짜 형식: 'YYYYMMDD'
  """
  ensure_records_folder()
  try:
    start = datetime.datetime.strptime(start_date, '%Y%m%d')
    end = datetime.datetime.strptime(end_date, '%Y%m%d')
  except ValueError:
    print('날짜 형식이 올바르지 않습니다. 예: 20240529')
    return

  print(f'{start_date} ~ {end_date} 사이의 녹음 파일 목록:')
  for file in os.listdir('records'):
    if file.endswith('.wav'):
      try:
        timestamp_str = file.replace('.wav', '')
        timestamp = datetime.datetime.strptime(timestamp_str, '%Y%m%d-%H%M%S')
        if start <= timestamp <= end:
          print(file)
      except ValueError:
        continue


def main():
  while True:
    print('\n1. 음성 녹음')
    print('2. 녹음 파일 조회')
    print('3. 종료')
    choice = input('선택하세요: ')

    if choice == '1':
      try:
        seconds = int(input('녹음 시간(초)을 입력하세요: '))
        audio, rate = record_voice(seconds)
        save_recording(audio, rate)
      except ValueError:
        print('숫자를 입력하세요.')
    elif choice == '2':
      start = input('시작 날짜 (YYYYMMDD): ')
      end = input('끝 날짜 (YYYYMMDD): ')
      list_recordings_by_date(start, end)
    elif choice == '3':
      print('프로그램 종료.')
      break
    else:
      print('올바른 선택이 아닙니다.')


if __name__ == '__main__':
  main()
