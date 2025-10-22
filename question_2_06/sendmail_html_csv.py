#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sendmail_html_csv.py

CSV(이름, 이메일) 명단을 읽어 HTML 메일을 발송하는 스크립트.
- 표준 라이브러리만 사용(smtplib, ssl, csv, email 등)
- Gmail/네이버 SMTP 지원
- 발송 모드: bulk_to, bulk_bcc, per_recipient
- HTML 본문 + 텍스트 대체(멀티파트/알터너티브)

CSV 형식:
    이름, 이메일
    홍길동, gildong@example.com
    이지은, iu@example.com

##네이버 메일 보내기 팁

    네이버 메일 환경설정에서 POP3/IMAP 사용함으로 설정
    앱 비밀번호(또는 외부 메일 클라이언트용 비밀번호) 생성

    실행 시 --provider naver 선택

    호스트: smtp.naver.com

    포트: 465(SMTPS)

    네이버도 스팸 정책이 엄격해 **per_recipient**가 더 안정적
"""

import argparse
import csv
import getpass
import os
import ssl
import sys
from typing import List, Tuple, Dict

import smtplib
from email.message import EmailMessage


PROVIDERS = {
    'gmail': {
        'host': 'smtp.gmail.com',
        'port': 465,       # SMTPS(SSL)
        'ssl': True
    },
    'naver': {
        'host': 'smtp.naver.com',
        'port': 465,       # SMTPS(SSL)
        'ssl': True
    }
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Send HTML emails from CSV recipient list via Gmail or Naver.'
    )
    parser.add_argument(
        '--csv',
        required=True,
        help='Path to CSV file with columns: 이름, 이메일'
    )
    parser.add_argument(
        '--provider',
        choices=list(PROVIDERS.keys()),
        default='gmail',
        help='SMTP provider (default: gmail)'
    )
    parser.add_argument(
        '--mode',
        choices=['bulk_to', 'bulk_bcc', 'per_recipient'],
        default='per_recipient',
        help='Sending mode (default: per_recipient)'
    )
    parser.add_argument(
        '--html-file',
        help='Path to an HTML file used as email body (optional).'
    )
    return parser.parse_args()


def prompt_account(provider_key: str) -> Tuple[str, str, str]:
    cfg = PROVIDERS[provider_key]
    print(f'발송 계정 정보 입력 ({provider_key} / {cfg["host"]}:{cfg["port"]})')
    print('보내는 사람 이메일 주소(로그인 계정)를 입력하세요:')
    login_email = input().strip()

    print('표시될 보내는 사람 주소(미입력 시 로그인 계정 사용):')
    from_email = input().strip() or login_email

    password = getpass.getpass('비밀번호 또는 앱 비밀번호를 입력하세요: ').strip()
    return login_email, from_email, password


def prompt_subject_and_html(html_file: str = '') -> Tuple[str, str]:
    print('메일 제목을 입력하세요:')
    subject = input().strip()

    if html_file:
        if not os.path.isfile(html_file):
            print(f'HTML 파일을 찾지 못했습니다: {html_file}')
            sys.exit(1)
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        return subject, html

    print('HTML 본문을 입력하세요(빈 줄로 종료):')
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == '':
            break
        lines.append(line.rstrip('\n'))
    html = '\n'.join(lines) if lines else '<p></p>'
    return subject, html


def read_csv_targets(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    # BOM 가능성 고려해 utf-8-sig
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        # 컬럼명 표준화: '이름', '이메일'
        expected = {'이름', '이메일'}
        header = {h.strip() for h in reader.fieldnames or []}
        if not expected.issubset(header):
            print('CSV 헤더는 "이름, 이메일" 이어야 합니다.')
            print(f'현재 헤더: {header}')
            sys.exit(1)

        for row in reader:
            name = (row.get('이름') or '').strip()
            email = (row.get('이메일') or '').strip()
            if not email:
                continue
            rows.append({'이름': name, '이메일': email})
    if not rows:
        print('CSV에 유효한 수신자가 없습니다.')
        sys.exit(1)
    return rows


def make_message(
    from_email: str,
    to_emails: List[str],
    subject: str,
    html_body: str,
    text_body: str
) -> EmailMessage:
    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails) if to_emails else ''
    msg['Subject'] = subject

    # 멀티파트/알터너티브: 텍스트 대체 + HTML
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype='html')
    return msg


def plain_from_html(html: str) -> str:
    """
    아주 단순한 텍스트 대체 생성(정교한 파서는 표준 외라 사용하지 않음).
    """
    text = html.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    # 태그 제거(최소한)
    out = []
    inside = False
    for ch in text:
        if ch == '<':
            inside = True
            continue
        if ch == '>':
            inside = False
            continue
        if not inside:
            out.append(ch)
    result = ''.join(out)
    # 공백 정리
    lines = [line.strip() for line in result.splitlines()]
    return '\n'.join([ln for ln in lines if ln])


def connect_smtp(provider_key: str) -> smtplib.SMTP:
    cfg = PROVIDERS[provider_key]
    host = cfg['host']
    port = cfg['port']
    use_ssl = cfg['ssl']

    context = ssl.create_default_context()
    if use_ssl:
        server = smtplib.SMTP_SSL(host, port, context=context, timeout=30)
    else:
        server = smtplib.SMTP(host, port, timeout=30)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
    return server


def send_bulk_to(
    server: smtplib.SMTP,
    login_email: str,
    password: str,
    from_email: str,
    targets: List[Dict[str, str]],
    subject: str,
    html_body: str
) -> None:
    server.login(login_email, password)
    to_list = [t['이메일'] for t in targets]
    text_body = plain_from_html(html_body)
    msg = make_message(from_email, to_list, subject, html_body, text_body)
    server.send_message(msg, from_addr=from_email, to_addrs=to_list)


def send_bulk_bcc(
    server: smtplib.SMTP,
    login_email: str,
    password: str,
    from_email: str,
    targets: List[Dict[str, str]],
    subject: str,
    html_body: str
) -> None:
    server.login(login_email, password)
    bcc_list = [t['이메일'] for t in targets]
    text_body = plain_from_html(html_body)
    # BCC는 헤더에 드러나지 않게, 대표 수신자(To)는 발신자 혹은 안내 주소로 설정
    msg = make_message(from_email, [from_email], subject, html_body, text_body)
    # 실제 전송 대상에 BCC를 병합
    server.send_message(msg, from_addr=from_email, to_addrs=[from_email] + bcc_list)


def send_per_recipient(
    server: smtplib.SMTP,
    login_email: str,
    password: str,
    from_email: str,
    targets: List[Dict[str, str]],
    subject: str,
    html_body: str
) -> None:
    server.login(login_email, password)
    text_body = plain_from_html(html_body)

    for t in targets:
        to_addr = t['이메일']
        # 필요시 간단 개인화 예: {name} 치환
        html = html_body.replace('{name}', t['이름'] or '')
        text = text_body.replace('{name}', t['이름'] or '')

        msg = make_message(from_email, [to_addr], subject, html, text)
        server.send_message(msg, from_addr=from_email, to_addrs=[to_addr])


def main() -> None:
    args = parse_args()

    login_email, from_email, password = prompt_account(args.provider)
    subject, html_body = prompt_subject_and_html(args.html_file)
    targets = read_csv_targets(args.csv)

    try:
        with connect_smtp(args.provider) as server:
            if args.mode == 'bulk_to':
                send_bulk_to(server, login_email, password, from_email, targets, subject, html_body)
            elif args.mode == 'bulk_bcc':
                send_bulk_bcc(server, login_email, password, from_email, targets, subject, html_body)
            else:
                send_per_recipient(server, login_email, password, from_email, targets, subject, html_body)
        print('메일 전송이 완료되었습니다.')
    except smtplib.SMTPAuthenticationError:
        print('인증 실패: 아이디/비밀번호(앱 비밀번호)를 확인하세요.')
        sys.exit(1)
    except smtplib.SMTPRecipientsRefused as exc:
        print('수신자 주소가 거부되었습니다.')
        print(f'자세한 정보: {exc.recipients}')
        sys.exit(1)
    except smtplib.SMTPException as exc:
        print('SMTP 처리 중 오류가 발생했습니다.')
        print(f'자세한 정보: {exc}')
        sys.exit(1)
    except Exception as exc:
        print('예상치 못한 오류가 발생했습니다.')
        print(f'자세한 정보: {exc}')
        sys.exit(1)


if __name__ == '__main__':
    main()
