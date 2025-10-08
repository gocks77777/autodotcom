import os
import pandas as pd
from datetime import datetime
from collections import defaultdict

def process_data(df):
    """엑셀 DataFrame 전체 데이터 처리 함수 (매물 번호 기준 그룹화 및 병합) (수정 없음)"""
    output = []
    current_item_data = defaultdict(list) # 현재 매물 데이터 저장 defaultdict (수정 없음)
    current_number = None # 현재 매물 번호 (수정 없음)

    for _, row in df.iterrows():
        number_value = row['번호'] # 번호 컬럼 값 직접 추출 (문자열 변환 X, 수정 없음)
        number_str = str(number_value).strip() # [수정] 문자열 변환은 여기서 한 번만 수행 (수정 없음)

        if number_str and number_str.replace('.', '', 1).isdigit(): # [수정] 소수점 허용 숫자 여부 체크 (수정 없음)
            if current_number and current_item_data: # 이전 매물 데이터가 있으면 처리 (유지)
                output.append(format_output_item(current_number, current_item_data)) # output 리스트에 추가 (유지)
                current_item_data = defaultdict(list) # current_item_data 초기화 (유지)
            current_number = str(int(float(number_str))) # [수정] 번호를 정수형 변환 후 문자열로 저장 (유지)
            current_item_data['번호'].append(current_number) # defaultdict 에 번호 정보 추가 (유지)

        # 빈칸 행 또는 번호가 숫자가 아닌 행: 현재 매물에 정보 추가 (유지)
        for col_name in row.index:
            cell_value = str(row[col_name]).strip()
            if cell_value and col_name != '번호': # 빈 값이 아니고, '번호' 컬럼이 아니면 defaultdict 에 추가 (유지)
                current_item_data[col_name].append(cell_value)

    if current_number and current_item_data: # 마지막 매물 처리 (for loop 종료 후, 유지)
        output.append(format_output_item(current_number, current_item_data)) # output 리스트에 추가 (유지)

    return output


def format_output_item(number, item_data):
    """개별 매물 데이터 dict 를 텍스트 형식으로 변환 (nan 값 제거 추가)"""
    line = [f"번호: {number}"]

    # 금액 필드 특수 처리 (유지)
    amount_values = item_data.get('금액', [])
    if amount_values:
        amount_parts = []
        for value in amount_values:
            for part in value.split('|'):
                part = part.strip()
                if part and part.lower() != 'nan' and part.lower() != 'nat': # [수정] nan 값 체크 추가 (금액 필드)
                    if ':' not in part:
                        part = f"금액: {part}"
                    amount_parts.append(part)
        if amount_parts: # [수정] 금액 파트가 있을 때만 추가
            line.append(" ".join(amount_parts))

    # 출력 필드 순서 (유지)
    field_order = [
        '종류', '거래', '주소', '방', '면적', '층', '입주', '용도',
        '기타사항', '상세설명', '보안메모', '등록자', '일자'
    ]

    # 일반 필드 처리 (nan 값 제거 추가)
    for field in field_order:
        values = item_data.get(field, [])
        if values:
            formatted_values = []
            for value in values:
                if value.lower() != 'nan' and value.lower() != 'nat': # [수정] nan 값 체크 추가 (일반 필드)
                    # 일자 필드 포맷팅 (시간 제거, 유지)
                    if field == '일자':
                        date_parts = []
                        for date_part in value.split('|'):
                            date_part = date_part.strip()
                            if ' ' in date_part:
                                date_part = date_part.split(' ')[0]
                            date_parts.append(date_part)
                        formatted_value = ' | '.join(date_parts)
                    else:
                        formatted_value = value
                    if formatted_value and formatted_value.lower() != 'nan' and formatted_value.lower() != 'nat': # [수정] 포맷팅 후 nan 값 다시 체크
                        formatted_values.append(formatted_value) # [수정] 포맷팅된 값 사용

            if formatted_values: # [수정] 유효한 값이 있을 때만 출력
                line.append(f"{field}: {' | '.join(formatted_values)}") # [수정] | 구분자 추가


    return "\n".join(line) # 필드별 줄바꿈 (수정 없음)


def analyze_excel_and_save(excel_path=None):
    """엑셀 파일 분석 및 메모장 저장 (서버 환경 대응)"""
    try:
        # 서버 환경에서는 현재 디렉토리의 엑셀 파일을 찾아서 처리
        if not excel_path:
            # 현재 디렉토리에서 .xlsx 파일 찾기
            excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
            if not excel_files:
                print("❌ 현재 디렉토리에 엑셀 파일(.xlsx)이 없습니다.")
                return None
            excel_path = excel_files[0]  # 첫 번째 엑셀 파일 사용
            print(f"📄 찾은 엑셀 파일: {excel_path}")

        # 엑셀 파일 읽기 (헤더=2행, 수정 없음)
        df = pd.read_excel(excel_path, header=1)

        # 첫 행이 숫자인 경우 제거 (수정 없음)
        if not df.empty and df.iloc[0].apply(lambda x: str(x).isdigit()).all():
            df = df.iloc[1:]

        # [수정] 컬럼명 재설정 (Unnamed 컬럼 처리, 수정 없음)
        new_columns = []
        for col in df.columns:
            if 'Unnamed' in str(col):
                new_columns.append(None) # Unnamed 컬럼은 None으로 처리
            else:
                new_columns.append(col)
        df.columns = new_columns
        df = df.rename(columns={None: 'temp_value'}) # None 컬럼 임시 컬럼명 지정

        # 데이터 처리 (process_data 함수 호출, 수정 없음)
        result = process_data(df)

        # 파일 저장 (서버 환경에 맞게 수정)
        filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        output_path = os.path.join('.', filename)  # 현재 디렉토리에 저장

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(result))  # 항목 간 2줄 띄움

        print(f"✅ 저장 완료: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_excel_and_save()
