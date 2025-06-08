import os
import datetime
import sounddevice as sd
import scipy.io.wavfile as wavfile
import speech_recognition as sr
from pydub import AudioSegment
import pandas as pd


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


def transcribe_audio_to_csv(filepath):
  recognizer = sr.Recognizer()
  audio = AudioSegment.from_wav(filepath)
  duration = len(audio) / 1000
# 녹음 시간대를 짧게 해서 5로 바꿈   
  step = 5 
  results = []

  print('STT 변환 중:', os.path.basename(filepath))

  for i in range(0, int(duration), step):
    chunk = audio[i * 1000:(i + step) * 1000]
    chunk_path = filepath.replace('.wav', f'_{i}.wav')
    chunk.export(chunk_path, format='wav')
    print(f'처리 중: {chunk_path}')

    with sr.AudioFile(chunk_path) as source:
      try:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        timestamp = f'{i:02d}:00'
        results.append((timestamp, text))
        print(f'{timestamp}: {text}')
      except sr.UnknownValueError:
        # 너무 짧은 음성들은 인식이 잘 안됨
        print(f'{chunk_path}: 음성 인식 실패 (무시됨)')
      except sr.RequestError as e:
        print(f'STT API 오류: {e}')
    os.remove(chunk_path)

  if results:
    csv_path = filepath.replace('.wav', '.csv')
    df = pd.DataFrame(results, columns=['시간', '텍스트'])
    try:
      df.to_csv(csv_path, index=False)
      print('CSV 저장 완료:', csv_path)
    except Exception as e:
      print('CSV 저장 실패:', e)
  else:
    print('인식된 텍스트가 없습니다.')



def search_keyword_in_csv(keyword):
  print(f'키워드 "{keyword}" 검색 결과:')
  for file in os.listdir('records'):
    if file.endswith('.csv'):
      path = os.path.join('records', file)
      try:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
          if keyword in str(row['텍스트']):
            print(f'{file} - {row["시간"]}: {row["텍스트"]}')
      except Exception:
        continue


def main():
  while True:
    print('\n1. 음성 녹음')
    print('2. 녹음 파일 조회')
    print('3. STT 변환 및 CSV 저장')
    print('4. 키워드 검색')
    print('5. 종료')
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
      for file in os.listdir('records'):
        if file.endswith('.wav'):
          path = os.path.join('records', file)
          transcribe_audio_to_csv(path)
    elif choice == '4':
      keyword = input('검색할 키워드를 입력하세요: ')
      search_keyword_in_csv(keyword)
    elif choice == '5':
      print('프로그램 종료.')
      break
    else:
      print('올바른 선택이 아닙니다.')


if __name__ == '__main__':
  main()
