#!/usr/local/bin/python3

import sys
import os
import csv
import re

class CourseCsvFileNotFoundException(Exception):
    """
    A custom exception for the cases that the course csv file does not exist.
    """
    pass

def check_filename_existence(func):
    """
    A decorator that catches the non-exiting filename argument and raises a custom `BabynameFileNotFoundException`.
    파일을 읽기 전 존재 유무를 확인하는 데코레이터
    """
    def decorated(self, dirname, filebase):
        filename = os.path.join(dirname, "{}.csv".format(filebase))
        if(not os.path.isfile(filename)):
            raise CourseCsvFileNotFoundException("No such file: {}".format(filename))

        return func(self, dirname, filebase)
    
    return decorated

# csv 데이터 파일을 읽어들이고, 적절한 형식으로 변환해주는 클래스
class CsvParser:

    @check_filename_existence
    def __init__(self, dirname, filebase):
        self.name_to_course_tuples = []
        
        filename = os.path.join(dirname, "{}.csv".format(filebase))
        
        with open(filename, newline='') as csvfile:
            # read csv 
            # csv 파일을 읽어들인다
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            # remove headings & locate name column
            # 헤더들을 제거하고, 이름이 적힌 열 인덱스를 기억한다
            name_index = next(spamreader).index('이름')
            # preprocessing
            # 데이터 전처리
            for row in spamreader:
                # find vess member's name
                # 이름 추출
                name = row.pop(name_index)
                # removes null('') elements
                # 공란 제거
                filtered_row_itr = filter(None, row[1:]) 
                # removes all white spaces(' ') & split course into name and number
                # 공백 문자 제거 & 강의명 / 분반번호 분리
                trimmed_elements = [elem.replace(' ', '').split('(') for elem in filtered_row_itr]
                # remove not numbers from course_num & adds up elements in records
                # 분반번호에 숫자만 남긴다
                # ("임은성", "초급프랑스어1", "003")과 같은 형식의 튜플로 모든 수강 데이터를 저장한다
                self.name_to_course_tuples += [(name, course_name, re.sub("[^0-9]", "", course_num)) for course_name, course_num in trimmed_elements] 
   

def filter_kor(course_full_name):
    # removes all characters other than korean
    # 문자열에서 한글만 남긴다. 강의명 분류용.
    kor_regex = re.compile("[^가-힣]+")
    return kor_regex.sub('', course_full_name)

# 각각의 강의에 해당하는 클래스. 수강자 목록을 포함한다.
class CourseRecord:
    def __init__(self, member_tuple):
        """
        Args:
            name: The name of the vess member.
            course_full_name: original full name of course.
            course_num: class number.
        """
        self.member_tuples = [member_tuple]
        self.course_name = filter_kor(member_tuple[1])

    # 새 수강자 추가
    def append(self, member):
        self.member_tuples.append(member)

    # 파일 출력용
    def to_txt_record(self):
        """
        Convert the record in to a well-formed string lines, as format of "이름: name, 강의명: course_name, 분반: course_num".
        The return value is a line of body of text file output.
        예시는 아래 콘솔 출력용 함수 참조
        """
        # 강의 풀네임 가나다 순으로 정렬
        self.member_tuples = sorted(self.member_tuples, key=lambda member: member[1])
        return "[강의분류명] {}\n".format(self.course_name) \
                + '\n'.join(["이름: %s, 강의명: %s, 분반: %s" % member for member in self.member_tuples]) \
                + '\n'
    # 콘솔 출력용
    def print_members(self):
        self.member_tuples = sorted(self.member_tuples, key=lambda member: member[1])
        # e.g. [강의분류명] 초급프랑스어
        # 이름: 임은성, 강의명: 초급프랑스어1, 분반: 003
        #
        # [강의분류명] 소프트웨어개발의원리와실제
        # 이름: 임은성, 강의명: 소프트웨어개발의원리와실제, 분반: 001
        print("[강의분류명]", self.course_name)
        for member in self.member_tuples: print("이름: %s, 강의명: %s, 분반: %s" % member)
        print()

# 겹강 정보를 파일에 적는다
def save(filename, records):
    """
    This function saves the parsed records in text format.

    Args:
        filename: The name of the output file.
        records: The list of records.
    """
    with open(filename, "w") as f:
        f.write("[VESS 5기] 당신의 겹강을 찾아드립니다\n\n")
        for key, record in records:
            f.write(record.to_txt_record())
            f.write("\n")

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print('usage: python find_your_classmate.py `filebase')
        sys.exit(1)

    filebase = args[0]
    records = {} # dictionary of CourseRecord objects
    
    # 데이터를 읽어들이고, 적절한 형식으로 변환한다
    parser = CsvParser(os.getcwd(), filebase)
    # e.g. elem = ("임은성", "초급프랑스어1", "003")
    for elem in parser.name_to_course_tuples:
        # e.g. course_name = "초급프랑스어"
        course_name = filter_kor(elem[1])
        # 강의명에 해당하는 객체가 이미 존재하면 수강목록에 추가하고, 아니면 새 강의 객체를 만든다
        try:
            records[course_name].append(elem)
        except KeyError:
            records[course_name] = CourseRecord(elem)

    # 가나다 순으로 콘솔에 출력
    for key, record in sorted(records.items()): record.print_members()
    # 가나다 순으로 현재 디렉토리의 '겹강목록.txt' 파일에 출력
    filename = os.path.join(os.getcwd(), "{}.txt".format('겹강목록'))
    save(filename, sorted(records.items()))

if __name__ == '__main__':
    main()
