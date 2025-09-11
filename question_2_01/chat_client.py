"""
단순 TCP 채팅 클라이언트
- 실행 시 닉네임을 서버에 전송
- '/종료' 입력 시 연결 종료
- 서버로부터 수신한 메시지 출력
- 표준 라이브러리만 사용
"""

import argparse
import socket
import sys
import threading


class ChatClient:
    """채팅 서버와 통신하는 간단한 클라이언트."""

    def __init__(self, host: str, port: int, name: str | None) -> None:
        self.host = host
        self.port = port
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alive = True

    def start(self) -> None:
        """서버에 연결하고 송수신 스레드를 시작한다."""
        try:
            self.sock.connect((self.host, self.port))
        except OSError as exc:
            print(f'[클라이언트] 서버 연결 실패: {exc}')
            return

        # 수신 스레드
        threading.Thread(target=self._recv_loop, daemon=True).start()

        # 서버의 닉네임 프롬프트 수신 후 닉네임 전송
        if self.name is None:
            try:
                prompt = self.sock.recv(1024).decode('utf-8')
                sys.stdout.write(prompt)
                sys.stdout.flush()
                nickname = sys.stdin.readline().strip()
            except Exception:
                nickname = ''
        else:
            # 서버가 먼저 '닉네임을 입력하세요: '를 보낸 뒤 읽힐 수 있도록 약간 대기 없이도 전송 가능
            nickname = self.name

        try:
            self.sock.sendall((nickname + '\n').encode('utf-8'))
        except OSError:
            print('[클라이언트] 닉네임 전송 실패')
            self.alive = False

        # 송신 루프
        self._send_loop()

        # 종료 정리
        try:
            self.sock.close()
        except OSError:
            pass

    def _recv_loop(self) -> None:
        """서버로부터 메시지를 계속 수신하여 출력한다."""
        try:
            while self.alive:
                data = self.sock.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8', errors='replace')
                sys.stdout.write(text)
                sys.stdout.flush()
        except OSError:
            pass
        finally:
            self.alive = False

    def _send_loop(self) -> None:
        """표준입력에서 메시지를 읽어 서버로 전송한다."""
        try:
            while self.alive:
                line = sys.stdin.readline()
                if not line:
                    break
                msg = line.rstrip('\n')
                try:
                    self.sock.sendall((msg + '\n').encode('utf-8'))
                except OSError:
                    break
                if msg == '/종료':
                    break
        finally:
            self.alive = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='TCP 채팅 클라이언트')
    parser.add_argument('--host', default='127.0.0.1', help='서버 호스트 (기본: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='서버 포트 (기본: 5000)')
    parser.add_argument('--name', help='닉네임(옵션, 미지정 시 실행 중 입력)', default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = ChatClient(args.host, args.port, args.name)
    client.start()


if __name__ == '__main__':
    main()
