def read_file(filename):
  try:
    with open(filename, 'r', encoding='utf-8') as f:
      return f.read().strip()
  except FileNotFoundError:
    print(f"[에러] 파일을 찾을 수 없습니다: {filename}")
    return ''
  except Exception as e:
    print(f"[에러] {filename} 파일을 읽는 중 문제가 발생했습니다: {e}")
    return ''

def write_file(filename, content):
  try:
    with open(filename, 'w', encoding='utf-8') as f:
      f.write(content)
    print(f"[성공] 결과가 {filename}에 저장되었습니다.")
  except Exception as e:
    print(f"[에러] 결과 파일을 저장하는 중 문제가 발생했습니다: {e}")

def caesar_cipher_decode(target_text):
  alphabet = 'abcdefghijklmnopqrstuvwxyz'
  dict_words = set()
  dictionary_text = read_file('dictionary.txt')

  if dictionary_text:
    for word in dictionary_text.splitlines():
      dict_words.add(word.strip().lower())

  print("\n[알림] 자리수(0~25)를 하나씩 시도합니다. 사전 단어 포함 시 자동 중단됩니다.\n")

  for shift in range(26):
    decoded = ''

    for char in target_text:
      if char.isalpha():
        base = ord('A') if char.isupper() else ord('a')
        decoded += chr((ord(char) - base - shift) % 26 + base)
      else:
        decoded += char

    print(f"[{shift}] {decoded}")

    # 보너스: 사전 기반 자동 판단
    words = decoded.lower().split()
    if any(word in dict_words for word in words):
      print(f"\n[자동 중단] 사전 단어가 포함된 해독 결과 발견! shift={shift}")
      write_file('result.txt', decoded)
      return

  try:
    key = int(input("\n정상적으로 해독된 것으로 보이는 shift 값을 입력하세요 (0~25): "))
    if 0 <= key < 26:
      final_decoded = ''
      for char in target_text:
        if char.isalpha():
          base = ord('A') if char.isupper() else ord('a')
          final_decoded += chr((ord(char) - base - key) % 26 + base)
        else:
          final_decoded += char
      write_file('result.txt', final_decoded)
    else:
      print("올바른 숫자가 아닙니다.")
  except Exception as e:
    print(f"입력 오류: {e}")

if __name__ == '__main__':
  cipher_text = read_file('password.txt')
  
#   print(cipher_text)

  if cipher_text:
    caesar_cipher_decode(cipher_text)
