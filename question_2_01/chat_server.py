

"""
멀티스레드 TCP 채팅 서버
- 접속/퇴장 시 전체 공지
- '/종료' 입력 시 연결 종료
- 모든 메시지는 '사용자> 메시지' 형태로 브로드캐스트
- 보너스: 귓속말 '/w 대상닉 메시지' 또는 '/귓속말 대상닉 메시지'
- 표준 라이브러리만 사용
"""

import argparse
import socket
import threading
from typing import Dict, Tuple


class ChatServer:
    """클라이언트와의 멀티스레드 채팅을 제공하는 서버."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 재실행 시 TIME_WAIT 포트 바인딩 이슈 최소화
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 닉네임 -> (소켓, 주소)
        self.clients: Dict[str, Tuple[socket.socket, Tuple[str, int]]] = {}
        self.clients_lock = threading.Lock()

    def start(self) -> None:
        """서버를 시작하고 접속을 수락한다."""
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()
        print(f'[서버] {self.host}:{self.port} 에서 대기 중...')

        try:
            while True:
                client_sock, addr = self.server_sock.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, addr),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            print('\n[서버] 종료 신호 수신. 서버를 종료합니다.')
        finally:
            self._shutdown()

    def _handle_client(self, client_sock: socket.socket, addr: Tuple[str, int]) -> None:
        """개별 클라이언트와 통신한다."""
        nickname = ''
        try:
            client_sock.sendall('닉네임을 입력하세요: '.encode('utf-8'))
            raw = client_sock.recv(1024)
            if not raw:
                client_sock.close()
                return
            nickname = raw.decode('utf-8').strip()

            if not nickname:
                client_sock.sendall('올바른 닉네임이 아닙니다. 연결을 종료합니다.\n'.encode('utf-8'))
                client_sock.close()
                return

            with self.clients_lock:
                if nickname in self.clients:
                    client_sock.sendall('이미 사용 중인 닉네임입니다. 연결을 종료합니다.\n'.encode('utf-8'))
                    client_sock.close()
                    return
                self.clients[nickname] = (client_sock, addr)

            self._broadcast_system(f'{nickname}님이 입장하셨습니다.')

            # 안내
            help_text = (
                '안내: 일반 메시지는 모두에게 전송됩니다.\n'
                "안내: 종료하려면 '/종료' 를 입력하세요.\n"
                "안내: 귓속말은 '/w 대상닉 메시지' 또는 '/귓속말 대상닉 메시지' 를 사용하세요.\n"
            )
            client_sock.sendall(help_text.encode('utf-8'))

            while True:
                data = client_sock.recv(4096)
                if not data:
                    break

                msg = data.decode('utf-8').rstrip('\n').strip()
                if not msg:
                    continue

                # 명령 처리
                if msg == '/종료':
                    client_sock.sendall('연결을 종료합니다.\n'.encode('utf-8'))
                    break

                if msg.startswith('/w ') or msg.startswith('/귓속말 '):
                    self._handle_whisper(nickname, msg)
                    continue

                # 일반 메시지 브로드캐스트
                self._broadcast_chat(nickname, msg)

        except ConnectionResetError:
            # 클라이언트 비정상 종료
            pass
        finally:
            if nickname:
                self._remove_client(nickname)

    def _handle_whisper(self, sender: str, raw: str) -> None:
        """귓속말 처리: '/w 대상닉 메시지' 또는 '/귓속말 대상닉 메시지'."""
        parts = raw.split(maxsplit=2)
        if len(parts) < 3:
            self._send_to(sender, '형식: /w 대상닉 메시지\n')
            return

        _, target, message = parts[0], parts[1], parts[2]
        if not message:
            self._send_to(sender, '형식: /w 대상닉 메시지\n')
            return

        with self.clients_lock:
            target_entry = self.clients.get(target)

        if not target_entry:
            self._send_to(sender, f"'{target}' 닉네임을 찾을 수 없습니다.\n")
            return

        # 발신자에게 확인, 수신자에게 전달
        self._send_to(sender, f'(귓속말 -> {target}) {sender}> {message}\n')
        self._send_to(target, f'(귓속말) {sender}> {message}\n')

    def _broadcast_chat(self, nickname: str, message: str) -> None:
        """일반 채팅 메시지를 모든 접속자에게 전송한다."""
        text = f'{nickname}> {message}\n'
        with self.clients_lock:
            for other, (sock, _) in list(self.clients.items()):
                try:
                    sock.sendall(text.encode('utf-8'))
                except OSError:
                    # 전송 실패 시 제거
                    self._safe_close(other)

    def _broadcast_system(self, message: str) -> None:
        """시스템 공지 브로드캐스트."""
        text = f'[공지] {message}\n'
        with self.clients_lock:
            for nickname, (sock, _) in list(self.clients.items()):
                try:
                    sock.sendall(text.encode('utf-8'))
                except OSError:
                    self._safe_close(nickname)

    def _send_to(self, nickname: str, message: str) -> None:
        """특정 사용자에게 메시지를 보낸다."""
        with self.clients_lock:
            entry = self.clients.get(nickname)
        if entry:
            sock, _ = entry
            try:
                sock.sendall(message.encode('utf-8'))
            except OSError:
                self._safe_close(nickname)

    def _remove_client(self, nickname: str) -> None:
        """클라이언트 목록에서 제거하고 공지한다."""
        with self.clients_lock:
            entry = self.clients.pop(nickname, None)
        if entry:
            sock, _ = entry
            try:
                sock.close()
            except OSError:
                pass
            self._broadcast_system(f'{nickname}님이 퇴장하셨습니다.')

    def _safe_close(self, nickname: str) -> None:
        """전송 실패 등으로 인한 안전한 연결 해제."""
        with self.clients_lock:
            entry = self.clients.pop(nickname, None)
        if entry:
            sock, _ = entry
            try:
                sock.close()
            except OSError:
                pass

    def _shutdown(self) -> None:
        """서버 소켓을 종료한다."""
        with self.clients_lock:
            for _, (sock, _) in list(self.clients.items()):
                try:
                    sock.close()
                except OSError:
                    pass
            self.clients.clear()
        try:
            self.server_sock.close()
        except OSError:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='멀티스레드 TCP 채팅 서버')
    parser.add_argument('--host', default='0.0.0.0', help='바인드 호스트 (기본: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='포트 (기본: 5000)')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ChatServer(args.host, args.port)
    server.start()


if __name__ == '__main__':
    main()
