#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mars_weather_summary.py

- CSV 파일을 읽어서 mars.mars_weather 테이블에 INSERT
- 삽입된 데이터를 시계열 그래프로 그려 PNG로 저장
"""

import csv
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt


class MySQLHelper:
    """데이터베이스 연결 및 쿼리 실행을 도와주는 클래스."""

    def __init__(self, host, user, password, database, port=3306):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': 'utf8'
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """MySQL 서버에 연결."""
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
        except Error as e:
            print(f'Error 연결 실패: {e}')
            raise

    def execute(self, query, params=None):
        """단일 쿼리 실행."""
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def executemany(self, query, seq_params):
        """복수 쿼리 실행."""
        self.cursor.executemany(query, seq_params)
        self.conn.commit()

    def fetchall(self, query):
        """SELECT 결과 전체 반환."""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        """연결 종료."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def load_csv_to_db(helper, csv_path):
    """CSV를 읽어서 DB에 INSERT. 날짜 포맷과 소수점 온도, 컬럼명 오타 자동 보정 포함."""
    insert_sql = (
        'INSERT INTO mars_weather (mars_date, temp, storm) '
        'VALUES (%s, %s, %s)'
    )
    rows = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []

        # storm 컬럼명이 없으면 'stom' 으로 보정
        if 'storm' in fields:
            storm_col = 'storm'
        elif 'stom' in fields:
            storm_col = 'stom'
            print("경고: 'storm' 컬럼 대신 'stom'을 사용합니다.")
        else:
            raise KeyError(f"CSV에 'storm' 또는 'stom' 컬럼이 없습니다. 현재 헤더: {fields}")

        for row in reader:
            # 날짜 파싱
            date_str = row['mars_date']
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                dt = datetime.strptime(date_str, '%Y-%m-%d')

            # temp 처리
            raw_temp = row['temp']
            try:
                temp = int(raw_temp)
            except ValueError:
                temp = int(float(raw_temp))

            # storm/stom 처리
            raw_storm = row[storm_col]
            try:
                storm = int(raw_storm)
            except ValueError:
                storm = int(float(raw_storm))

            rows.append((dt, temp, storm))

    helper.executemany(insert_sql, rows)
    print(f'{len(rows)}개 레코드를 삽입했습니다.')





def plot_and_save(helper, output_png):
    """삽입된 데이터를 꺾은선 그래프로 그리고 PNG로 저장."""
    data = helper.fetchall(
        'SELECT mars_date, temp FROM mars_weather ORDER BY mars_date'
    )
    dates = [row[0] for row in data]
    temps = [row[1] for row in data]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, temps, marker='o')
    plt.title('Mars Surface Temperature Over Time')
    plt.xlabel('Mars Date')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_png)
    print(f'그래프를 {output_png} 로 저장했습니다.')


def main():
    helper = MySQLHelper(
        host='localhost',
        user='root',
        password='',
        database='mars'
    )
    try:
        helper.connect()
        load_csv_to_db(helper, 'question12/mars_weathers_data.csv')
        plot_and_save(helper, 'question12/mars_temperature_trend.png')
    finally:
        helper.close()


if __name__ == '__main__':
    main()
