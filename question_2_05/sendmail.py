#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sendmail.py

Gmail SMTP 서버를 사용해 메일을 전송하는 예제 스크립트.
- 표준 라이브러리만 사용
- PEP 8 스타일 가이드 준수
- 기본 문자열은 ' ' 사용
- 예외 처리 포함
- 보너스: --attach 옵션으로 첨부파일 전송 지원

사용 예:
    python3 sendmail.py
    python3 sendmail.py --attach ./report.pdf ./image.png
"""

import argparse
import getpass
import mimetypes
import os
import socket
import ssl
import sys
from email.message import EmailMessage
from typing import List, Tuple
import smtplib


SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587  # 권장: STARTTLS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Send an email via Gmail SMTP (supports attachments).'
    )
    parser.add_argument(
        '--attach',
        nargs='*',
        default=[],
        help='Paths of files to attach (optional).'
    )
    return parser.parse_args()


def prompt_account_info() -> Tuple[str, str]:
    print('보내는 사람의 Gmail 주소를 입력하세요:')
    sender = input().strip()

    # 비밀번호(또는 앱 비밀번호)는 화면에 표시되지 않게 입력
    password = getpass.getpass('Gmail 비밀번호(또는 앱 비밀번호)를 입력하세요: ').strip()
    return sender, password


def prompt_mail_content() -> Tuple[List[str], str, str]:
    print('받는 사람 이메일 주소를 입력하세요(쉼표로 여러 명 가능):')
    to_raw = input().strip()
    recipients = [addr.strip() for addr in to_raw.split(',') if addr.strip()]

    print('메일 제목을 입력하세요:')
    subject = input().strip()

    print('메일 본문을 입력하세요(입력 종료는 빈 줄 + Enter):')
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == '':
            break
        lines.append(line.rstrip('\n'))
    body = '\n'.join(lines) if lines else ''

    return recipients, subject, body


def build_message(
    sender: str,
    recipients: List[str],
    subject: str,
    body: str,
    attachments: List[str]
) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    msg.set_content(body)

    for path in attachments:
        add_attachment(msg, path)

    return msg


def add_attachment(msg: EmailMessage, file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'첨부파일을 찾을 수 없습니다: {file_path}')

    mime_type, encoding = mimetypes.guess_type(file_path)
    if mime_type is None or encoding is not None:
        maintype, subtype = 'application', 'octet-stream'
    else:
        maintype, subtype = mime_type.split('/', 1)

    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_data = f.read()

    msg.add_attachment(
        file_data,
        maintype=maintype,
        subtype=subtype,
        filename=filename
    )


def send_email(
    sender: str,
    password: str,
    recipients: List[str],
    message: EmailMessage
) -> None:
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            # 서버 인사
            server.ehlo()

            # TLS 업그레이드
            server.starttls(context=context)
            server.ehlo()

            # 로그인
            server.login(sender, password)

            # 전송
            server.send_message(message, from_addr=sender, to_addrs=recipients)

    except smtplib.SMTPAuthenticationError:
        print('인증에 실패했습니다. Gmail 비밀번호 또는 앱 비밀번호를 확인하세요.')
        raise
    except smtplib.SMTPConnectError:
        print('SMTP 서버에 연결하지 못했습니다. 네트워크 상태를 확인하세요.')
        raise
    except smtplib.SMTPRecipientsRefused as exc:
        print('수신자 주소가 거부되었습니다.')
        print(f'자세한 정보: {exc.recipients}')
        raise
    except smtplib.SMTPException as exc:
        print('SMTP 처리 중 오류가 발생했습니다.')
        print(f'자세한 정보: {exc}')
        raise
    except socket.gaierror:
        print('호스트 이름을 확인하지 못했습니다. 인터넷 연결을 확인하세요.')
        raise
    except TimeoutError:
        print('SMTP 연결이 시간 초과되었습니다.')
        raise


def main() -> None:
    args = parse_args()

    print('=== Gmail SMTP 메일 보내기 ===')
    sender, password = prompt_account_info()
    recipients, subject, body = prompt_mail_content()

    if not recipients:
        print('오류: 최소 한 명의 수신자 이메일이 필요합니다.')
        sys.exit(1)

    try:
        msg = build_message(
            sender=sender,
            recipients=recipients,
            subject=subject,
            body=body,
            attachments=args.attach
        )
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)
    except Exception as exc:
        print('메시지 구성 중 알 수 없는 오류가 발생했습니다.')
        print(f'자세한 정보: {exc}')
        sys.exit(1)

    try:
        send_email(sender, password, recipients, msg)
        print('메일이 성공적으로 전송되었습니다.')
    except Exception:
        # 위에서 이미 사용자 친화적 메시지를 출력했으므로 여기서는 종료 코드만.
        sys.exit(1)


if __name__ == '__main__':
    main()
