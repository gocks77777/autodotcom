# -*- coding: utf-8 -*-
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import os
import time
import traceback
import subprocess
import tkinter
from tkinter import filedialog
import re
import platform
import tempfile
from webdriver_manager.chrome import ChromeDriverManager
import chardet
from selenium.webdriver.common.keys import Keys

# Chrome 디버깅 모드로 실행

def start_chrome_with_debugging():
    print("DEBUG: Starting Chrome with debugging mode...")
    if platform.system() == "Windows":
        program_files = os.getenv("ProgramFiles", r"C:\\Program Files")
        program_files_x86 = os.getenv("ProgramFiles(x86)", r"C:\\Program Files (x86)")
        possible_paths = [
            os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        else:
            chrome_path = input("Chrome 실행 파일 경로를 입력하세요: ")
    elif platform.system() == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif platform.system() == "Linux":
        chrome_path = "/usr/bin/google-chrome"
    else:
        print("⚠️ 지원되지 않는 운영체제입니다.")
        exit()

    user_data_dir = os.path.join(tempfile.gettempdir(), "ChromeProfile")
    os.makedirs(user_data_dir, exist_ok=True)

    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=False)
        else:
            subprocess.run(["pkill", "-9", "chrome"], check=False)
    except Exception as e:
        print(f"⚠️ Chrome 종료 중 오류: {e}")

    chrome_cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "https://www.gongsil.com/ms/ms/msearchcondition.gongsil?menu_id=040100"
    ]
    try:
        subprocess.Popen(chrome_cmd)
        print("✓ Chrome 디버깅 모드로 실행 완료")
    except FileNotFoundError as e:
        print(f"❌ Chrome 실행 파일을 찾을 수 없습니다: {e}")
        exit()

def format_text_with_line_breaks(input_text):
    # 문자열을 구분자를 기준으로 분할
    parts = re.split(r'(\s*-\s*|\s*\*\s*|\s*->\s*)', input_text)
    
    formatted_parts = []
    for part in parts:
        if part.strip().startswith('-') or part.strip().startswith('*'):
            # 줄바꿈 추가
            formatted_parts.append('\n' + part.strip() + '\n')
        elif part.strip().startswith('->'):
            # 줄바꿈 없이 유지
            formatted_parts.append(part.strip())
        else:
            # 기본적으로 추가
            formatted_parts.append(part.strip())
    
    # 포맷팅된 문자열 조합
    formatted_text = ' '.join(formatted_parts)
    return formatted_text

# 예제 입력
input_text = "청담e-편한세상1차 [전세] - 올수리(내부깨끗) 확장형 방3,화1 - 고층 전망좋음 - 9월중순 입주협의 * 조건 정리 / 일정 조율 / 소유자 협의 * 현장답사 -> 조건조율 및 계약금입금 -> 잔금일까지 정확하고 깔끔한 진행 도와드리겠습니다. * 공동중개 감사합니다. ☎ 담당자 010-4331-2032"

# 포맷팅된 출력
formatted_output = format_text_with_line_breaks(input_text)
print(formatted_output)

def run_automation(listing, driver):
    print(f"DEBUG: Starting automation for listing: {listing['property_type']}")
    print(f"DEBUG: 매물 데이터 - {listing}")
    
    try:
        # 1단계: 매물 종류 선택
        print("DEBUG: 1단계 - 매물 종류 선택 시작")
        property_type_xpath_map = {
            '아파트/주상복합': '//*[@id="MY_BODY_RIGHT"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/span/a[1]',
            '오피스텔': '//*[@id="MY_BODY_RIGHT"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/span/a[2]',
            '아파트/주상복합분양권': '//*[@id="MY_BODY_RIGHT"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/span/a[3]',
            '오피스텔분양권': '//*[@id="MY_BODY_RIGHT"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/span/a[4]',
            '사무실': '//*[@id="MY_BODY_RIGHT"]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[2]/span/a[1]',
            '상가/점포': '//*[@id="MY_BODY_RIGHT"]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[2]/span/a[2]',
        }

        if listing['property_type'] in property_type_xpath_map:
            print(f"DEBUG: 매물 종류 '{listing['property_type']}' 선택 시도")
            el = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, property_type_xpath_map[listing['property_type']])))
            el.click()
            time.sleep(2)
            print(f"DEBUG: 매물 종류 '{listing['property_type']}' 선택 완료")
            
            if listing['property_type'] == '아파트/주상복합':
                print("DEBUG: 아파트/주상복합 추가 설정")
                dd = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//select[@name="build_type"]')))
                driver.execute_script("arguments[0].value = '1'; arguments[0].dispatchEvent(new Event('change'));", dd)
        else:
            print(f"⚠️ 지원되지 않는 매물 종류: {listing['property_type']}")

        # 2단계: 용도 선택 (오피스텔인 경우)
        if listing['property_type'] in ['오피스텔', '오피스텔분양권'] and listing['usage']:
            print(f"DEBUG: 2단계 - 용도 선택 시작: {listing['usage']}")
            usage_map = {'주거용': 'used1', '업무용': 'used2', '주거업무겸용': 'used3'}
            uid = usage_map.get(listing['usage'])
            if uid:
                WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, uid))).click()
                print(f"DEBUG: 용도 '{listing['usage']}' 선택 완료")
            else:
                print(f"⚠️ 지원되지 않는 용도: {listing['usage']}")

        # 3단계: 지역 선택
        print(f"DEBUG: 3단계 - 지역 선택 시작: {listing['district']} {listing['dong']}")
        try:
            Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "gugun")))).select_by_visible_text(listing['district'])
            print(f"DEBUG: 구 선택 완료: {listing['district']}")
            
            # 구 선택 후 알림 확인
            time.sleep(1)
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"⚠️ 구 선택 후 Alert: {alert_text}")
                if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '선택']):
                    print(f"❌ 구 선택 오류 Alert: {alert_text}")
                    alert.accept()
                    return False
                else:
                    alert.accept()
            except:
                pass
                
        except Exception as e:
            print(f"❌ 구 선택 실패: {listing['district']} - {e}")
            return False
            
        try:
            WebDriverWait(driver, 30).until(lambda d: listing['dong'] in [o.text for o in Select(d.find_element(By.ID, "dong")).options])
            Select(driver.find_element(By.ID, "dong")).select_by_visible_text(listing['dong'])
            print(f"DEBUG: 동 선택 완료: {listing['dong']}")
            
            # 동 선택 후 알림 확인
            time.sleep(1)
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"⚠️ 동 선택 후 Alert: {alert_text}")
                if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '선택']):
                    print(f"❌ 동 선택 오류 Alert: {alert_text}")
                    alert.accept()
                    return False
                else:
                    alert.accept()
            except:
                pass
                
        except Exception as e:
            print(f"❌ 동 선택 실패: {listing['dong']} - {e}")
            return False

        # 4단계: 단지 선택
        print(f"DEBUG: 4단계 - 단지 선택 시작: {listing['address']}")
        try:
            WebDriverWait(driver, 30).until(lambda d: len(Select(d.find_element(By.ID, "bid")).options) > 1)
            sb = Select(driver.find_element(By.ID, "bid"))
            complexes = [o.text for o in sb.options if o.text != "단지리스트"]
            print(f"DEBUG: 사용 가능한 단지 목록: {complexes}")
            
            # Remove spaces and special characters for comparison
            def normalize_string(s):
                return re.sub(r'[^\w]', '', s).lower()

            # Extract complex name from the address
            complex_name = listing['address'].split()[-1]
            normalized_complex_name = normalize_string(complex_name)
            print(f"DEBUG: Extracted complex name: {complex_name}")
            print(f"DEBUG: Normalized complex name: {normalized_complex_name}")

            # Match using the extracted complex name
            match = next((c for c in complexes if normalized_complex_name in normalize_string(c)), None)
            if not match:
                print(f"⚠️ 주소 '{listing['address']}'에서 단지리스트와 일치하는 단지를 찾을 수 없습니다.")
                print(f"DEBUG: 매칭 시도한 단지들: {complexes}")
                return False
            sb.select_by_visible_text(match)
            print(f"DEBUG: 단지 선택 완료: {match}")

            # 면적 입력 후 알림 확인
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"⚠️ 공급면적 입력 후 Alert 발생: {alert_text}")
                error_keywords = ['오류', '실패', '잘못', '입력', '면적', 'size', 'Size', 'SIZE', '필수', '선택', '숫자']
                if any(keyword in alert_text for keyword in error_keywords):
                    print(f"❌ 공급면적 입력 실패로 판단: {alert_text}")
                    alert.accept()
                    return False
                else:
                    print(f"✓ 공급면적과 무관한 Alert 처리: {alert_text}")
                    alert.accept()
            except:
                pass
            
        except Exception as e:
            print(f"❌ 단지 선택 실패: {e}")
            return False

        # 5단계: 면적 선택은 나중에 처리 (매물 등록 완료 버튼 바로 전)
        print(f"DEBUG: 5단계 - 면적 선택은 나중에 처리 예정: {listing['size_type']}")

        # 6단계: 방 구조 선택
        print(f"DEBUG: 6단계 - 방 구조 선택 시작: {listing['room_structure']}")
        try:
            room_select = Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "room_struc"))))
            available_structures = [o.text for o in room_select.options]
            print(f"DEBUG: 사용 가능한 방 구조 옵션: {available_structures}")
            
            # 방 구조 매핑 테이블
            structure_mapping = {
                '욕실 : 1': '분리형',  # 잘못 파싱된 경우
                '분리형': '분리형',
                '오픈형': '오픈형',
                '세미오픈형': '세미오픈형',
                '복층형': '복층형',
                '베란다확장': '베란다확장'
            }
            
            mapped_structure = structure_mapping.get(listing['room_structure'], listing['room_structure'])
            
            if mapped_structure in available_structures:
                room_select.select_by_visible_text(mapped_structure)
                print(f"DEBUG: 방 구조 선택 완료: {listing['room_structure']} → {mapped_structure}")
            else:
                print(f"❌ 방 구조 옵션에 없음: {listing['room_structure']} (매핑: {mapped_structure})")
                print(f"DEBUG: 사용 가능한 방 구조: {available_structures}")
                return False
        except Exception as e:
            print(f"❌ 방 구조 선택 실패: {e}")
            return False

        # 7단계: 방 개수 입력
        print(f"DEBUG: 7단계 - 방 개수 입력: {listing['room_count']}")
        try:
            ri = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "room")))
            ri.clear()
            ri.send_keys(str(listing['room_count']))
            print(f"DEBUG: 방 개수 입력 완료: {listing['room_count']}")
        except Exception as e:
            print(f"❌ 방 개수 입력 실패: {e}")
            return False

        # 8단계: 욕실 개수 입력
        print(f"DEBUG: 8단계 - 욕실 개수 입력: {listing['bathroom_count']}")
        try:
            bi = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "bathroom")))
            bi.clear()
            bi.send_keys(str(listing['bathroom_count']))
            print(f"DEBUG: 욕실 개수 입력 완료: {listing['bathroom_count']}")
        except Exception as e:
            print(f"❌ 욕실 개수 입력 실패: {e}")
            return False

        # 9단계: 입주 정보 선택
        print(f"DEBUG: 9단계 - 입주 정보 선택: {listing.get('move_in_value', '')}")
        try:
            move_id = f"move_in{listing.get('move_in_value', '')}"
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, move_id))).click()
            print(f"DEBUG: 입주 정보 선택 완료: {move_id}")
            
            if listing.get('move_in_value') == "3" and 'move_in_day' in listing:
                date_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "move_day")))
                date_input.clear()
                date_input.send_keys(listing['move_in_day'])
                print(f"DEBUG: 입주 날짜 입력 완료: {listing['move_in_day']}")
        except Exception as e:
            print(f"❌ 입주 정보 선택 실패: {e}")
            return False

        # 10단계: 상세 설명 입력
        print(f"DEBUG: 10단계 - 상세 설명 입력: {listing['content'][:50]}...")
        try:
            ta = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "content")))
            ta.clear()
            ta.send_keys(listing['content'])
            print(f"DEBUG: 상세 설명 입력 완료")
        except Exception as e:
            print(f"❌ 상세 설명 입력 실패: {e}")
            return False

        # 11단계: 거래 유형 및 가격 입력
        print(f"DEBUG: 11단계 - 거래 유형 선택: {listing['transaction_type']}")
        try:
            # 거래 유형 매핑 (단기임대 → 단기임대/풀옵션)
            transaction_mapping = {
                '매매': '매매',
                '전세': '전세', 
                '월세': '월세',
                '단기임대': '단기임대/풀옵션'
            }
            
            mapped_transaction = transaction_mapping.get(listing['transaction_type'], listing['transaction_type'])
            tmap = {'매매': 'b_type1', '전세': 'b_type2', '월세': 'b_type3', '단기임대/풀옵션': 'b_type4'}
            
            if mapped_transaction in tmap:
                WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, tmap[mapped_transaction]))).click()
                print(f"DEBUG: 거래 유형 선택 완료: {listing['transaction_type']} → {mapped_transaction}")
                
                # 거래 유형 선택 후 알림 확인
                time.sleep(1)
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    print(f"⚠️ 거래 유형 선택 후 Alert: {alert_text}")
                    if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '선택']):
                        print(f"❌ 거래 유형 선택 오류 Alert: {alert_text}")
                        alert.accept()
                        return False
                    else:
                        alert.accept()
                except:
                    pass
                
                if mapped_transaction == '매매':
                    si = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "sprice")))
                    si.clear()
                    # TXT 파일의 값이 이미 만원 단위 (예: 260 → 260만원)
                    si.send_keys(str(listing['sale_price']))
                    print(f"DEBUG: 매매가 입력 완료: {listing['sale_price']}만원")
                    
                    # 매매가 입력 후 알림 확인
                    time.sleep(1)
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f"⚠️ 매매가 입력 후 Alert: {alert_text}")
                        if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '입력', '가격']):
                            print(f"❌ 매매가 입력 오류 Alert: {alert_text}")
                            alert.accept()
                            return False
                        else:
                            alert.accept()
                    except:
                        pass
                elif mapped_transaction == '전세':
                    yi = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "yprice")))
                    yi.clear()
                    # TXT 파일의 값이 이미 만원 단위
                    yi.send_keys(str(listing['lease_price']))
                    print(f"DEBUG: 전세가 입력 완료: {listing['lease_price']}만원")
                    
                    # 전세가 입력 후 알림 확인
                    time.sleep(1)
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f"⚠️ 전세가 입력 후 Alert: {alert_text}")
                        if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '입력', '가격']):
                            print(f"❌ 전세가 입력 오류 Alert: {alert_text}")
                            alert.accept()
                            return False
                        else:
                            alert.accept()
                    except:
                        pass
                elif mapped_transaction == '단기임대/풀옵션':
                    # 단기임대는 보증금/월세와 동일한 방식으로 처리
                    di = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dprice")))
                    di.clear()
                    # TXT 파일의 값이 이미 만원 단위
                    di.send_keys(str(listing['deposit']))
                    ri2 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "rprice")))
                    ri2.clear()
                    # 월세는 그대로 입력
                    ri2.send_keys(str(listing['monthly_rent']))
                    print(f"DEBUG: 단기임대 가격 입력 완료: {listing['deposit']}만원 / {listing['monthly_rent']}")
                    
                    # 단기임대 가격 입력 후 알림 확인
                    time.sleep(1)
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f"⚠️ 단기임대 가격 입력 후 Alert: {alert_text}")
                        if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '입력', '가격']):
                            print(f"❌ 단기임대 가격 입력 오류 Alert: {alert_text}")
                            alert.accept()
                            return False
                        else:
                            alert.accept()
                    except:
                        pass
                else:
                    di = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dprice")))
                    di.clear()
                    # TXT 파일의 값이 이미 만원 단위
                    di.send_keys(str(listing['deposit']))
                    ri2 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "rprice")))
                    ri2.clear()
                    # 월세는 그대로 입력
                    ri2.send_keys(str(listing['monthly_rent']))
                    print(f"DEBUG: 보증금/월세 입력 완료: {listing['deposit']}만원 / {listing['monthly_rent']}")
                    
                    # 보증금/월세 입력 후 알림 확인
                    time.sleep(1)
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f"⚠️ 보증금/월세 입력 후 Alert: {alert_text}")
                        if any(keyword in alert_text for keyword in ['오류', '실패', '잘못', '입력', '가격']):
                            print(f"❌ 보증금/월세 입력 오류 Alert: {alert_text}")
                            alert.accept()
                            return False
                        else:
                            alert.accept()
                    except:
                        pass
            else:
                print(f"⚠️ 지원되지 않는 거래 유형: {listing['transaction_type']} (매핑: {mapped_transaction})")
        except Exception as e:
            print(f"❌ 거래 유형/가격 입력 실패: {e}")
            return False

        # 면적 선택 (매물 등록 완료 버튼 바로 전)
        print(f"DEBUG: 면적 선택 시작: {listing['size_type']}")
        try:
            # 1차 시도: 면적 드롭다운 사용
            size_select = Select(driver.find_element(By.ID, "size_type"))
            available_sizes = [o.get_attribute('value') for o in size_select.options if o.get_attribute('value')]
            print(f"DEBUG: 1차 시도 - 사용 가능한 면적 옵션: {available_sizes}")
            
            # 정확히 일치하는 면적 확인
            if listing['size_type'] in available_sizes:
                size_select.select_by_value(listing['size_type'])
                print(f"DEBUG: 면적 선택 완료 (1차 성공): {listing['size_type']}")
            else:
                print(f"⚠️ 1차 시도 실패 - 정확히 일치하는 면적 옵션이 없음: {listing['size_type']}")
                print(f"DEBUG: 1차 시도 - 사용 가능한 면적: {available_sizes}")
                
                # 2차 시도: 추가 대기 후 재시도
                print("DEBUG: 2차 시도 - 추가 대기 후 재시도...")
                time.sleep(5)  # 5초 추가 대기
                
                # 면적 드롭다운 다시 확인
                size_select = Select(driver.find_element(By.ID, "size_type"))
                available_sizes_2nd = [o.get_attribute('value') for o in size_select.options if o.get_attribute('value')]
                print(f"DEBUG: 2차 시도 - 사용 가능한 면적 옵션: {available_sizes_2nd}")
                
                # 2차 시도에서 정확히 일치하는 면적 확인
                if listing['size_type'] in available_sizes_2nd:
                    size_select.select_by_value(listing['size_type'])
                    print(f"DEBUG: 면적 선택 완료 (2차 성공): {listing['size_type']}")
                else:
                    print(f"⚠️ 2차 시도도 실패 - 공급면적 직접 입력으로 대체: {listing['size_type']}")
                    print(f"DEBUG: 2차 시도 - 사용 가능한 면적: {available_sizes_2nd}")
                    
                    # 3차 시도: 공급면적 직접 입력
                    try:
                        sale_size_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sale_size"]')))
                        sale_size_input.clear()
                        sale_size_input.send_keys(str(listing['size_type']))
                        print(f"DEBUG: 공급면적 직접 입력 완료: {listing['size_type']}")
                        
                        # 공급면적 입력 후 잠시 대기하여 알림 확인
                        time.sleep(2)
                        
                        # Alert 확인 (공급면적 입력 실패 알림이 있는지)
                        try:
                            alert = driver.switch_to.alert
                            alert_text = alert.text
                            print(f"⚠️ 공급면적 입력 후 Alert 발생: {alert_text}")
                            
                            # 오류 알림인지 확인 (성공 알림이 아닌 경우)
                            error_keywords = ['오류', '실패', '잘못', '입력', '면적', 'size', 'Size', 'SIZE', '필수', '선택', '숫자']
                            if any(keyword in alert_text for keyword in error_keywords):
                                print(f"❌ 공급면적 입력 실패로 판단: {alert_text}")
                                alert.accept()
                                return False
                            else:
                                print(f"✓ 공급면적과 무관한 Alert 처리: {alert_text}")
                                alert.accept()
                        except:
                            # Alert가 없으면 정상 처리
                            pass
                            
                    except Exception as e:
                        print(f"❌ 공급면적 직접 입력 실패: {e}")
                        return False
            
        except Exception as e:
            print(f"❌ 면적 선택 실패: {e}")
            return False

        # 최종 알림 확인 (매물 처리 완료 후)
        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"⚠️ 매물 처리 완료 후 Alert 발생: {alert_text}")
            
            # 오류 알림인지 확인 (성공 알림이 아닌 경우)
            error_keywords = ['오류', '실패', '잘못', '오류가', '실패했습니다', '잘못되었습니다', '입력', '선택', '필수']
            if any(keyword in alert_text for keyword in error_keywords):
                print(f"❌ 오류 Alert로 판단하여 실패 처리: {alert_text}")
                alert.accept()
                return False
            else:
                print(f"✓ 성공/정보 Alert로 판단: {alert_text}")
                alert.accept()
        except:
            # Alert가 없으면 정상 처리
            pass

        print(f"✅ 매물 처리 완료: {listing['property_type']} - {listing['address']}")
        return True
        
    except Exception as e:
        print(f"❌ 자동화 오류: {e}")
        print(f"DEBUG: 오류 발생 위치 - 매물 데이터: {listing}")
        traceback.print_exc()
        return False

def extract_listings_from_txt(txt_path, encoding):
    print("DEBUG: Starting extraction of all listings from txt file.")
    listings = []
    try:
        with open(txt_path, 'r', encoding=encoding) as f:
            content = f.read()
            raw_listings = content.strip().split('번호:')[1:]
            print(f"DEBUG: 발견된 매물 개수: {len(raw_listings)}")
            
            for idx, raw_listing in enumerate(raw_listings, 1):
                print(f"DEBUG: 매물 {idx} 파싱 시작")
                lines = raw_listing.strip().splitlines()
                listing_data = {
                    'property_type': None, 'address': None, 'transaction_type': None,
                    'deposit': None, 'monthly_rent': None, 'sale_price': None, 'lease_price': None,
                    'size_type': None, 'room_structure': None, 'room_count': None,
                    'bathroom_count': None, 'move_in_info': None, 'move_in_value': None, 'move_in_day': None,
                    'content': None, 'usage': None
                }
                
                for line in lines:
                    if line.startswith("종류:"):
                        listing_data['property_type'] = line.split("종류:")[1].strip()
                        print(f"DEBUG: 매물 {idx} - 종류: {listing_data['property_type']}")
                    elif line.startswith("주소:"):
                        listing_data['address'] = line.split("주소:")[1].strip()
                        print(f"DEBUG: 매물 {idx} - 주소: {listing_data['address']}")
                    elif line.startswith("거래:"):
                        listing_data['transaction_type'] = line.split("거래:")[1].strip()
                        print(f"DEBUG: 매물 {idx} - 거래: {listing_data['transaction_type']}")
                    elif "보증금:" in line or "월세:" in line:
                        dep = re.search(r'보증금:\s*([\d,]+)', line)
                        if dep:
                            listing_data['deposit'] = int(dep.group(1).replace(',', ''))
                            print(f"DEBUG: 매물 {idx} - 보증금: {listing_data['deposit']}")
                        rent = re.search(r'월세:\s*([\d,]+)', line)
                        if rent:
                            listing_data['monthly_rent'] = int(rent.group(1).replace(',', ''))
                            print(f"DEBUG: 매물 {idx} - 월세: {listing_data['monthly_rent']}")
                    elif line.startswith("매매가:"):
                        sp = re.search(r'매매가:\s*([\d,]+)', line)
                        if sp:
                            listing_data['sale_price'] = int(sp.group(1).replace(',', ''))
                            print(f"DEBUG: 매물 {idx} - 매매가: {listing_data['sale_price']}")
                    elif line.startswith("전세가:"):
                        lp = re.search(r'전세가:\s*([\d,]+)', line)
                        if lp:
                            listing_data['lease_price'] = int(lp.group(1).replace(',', ''))
                            print(f"DEBUG: 매물 {idx} - 전세가: {listing_data['lease_price']}")
                    elif line.startswith("면적:"):
                        listing_data['size_type'] = line.split("면적:")[1].strip().split()[0]
                        print(f"DEBUG: 매물 {idx} - 면적: {listing_data['size_type']}")
                    elif line.startswith("방:"):
                        # "방: 방 : 2 / 욕실 : 1" 형식 파싱
                        part = line.split("방:")[1].strip()
                        parts = part.split("/")
                        
                        # 방 개수 추출
                        room_part = parts[0].strip()  # "방 : 2"
                        room_count_match = re.search(r'방\s*:\s*(\d+)', room_part)
                        listing_data['room_count'] = room_count_match.group(1) if room_count_match else ""
                        
                        # 욕실 개수 추출
                        bathroom_part = parts[1].strip() if len(parts) > 1 else ""  # "욕실 : 1"
                        bathroom_count_match = re.search(r'욕실\s*:\s*(\d+)', bathroom_part)
                        listing_data['bathroom_count'] = bathroom_count_match.group(1) if bathroom_count_match else ""
                        
                        # 방 구조는 기본값으로 설정 (나중에 매핑에서 처리)
                        listing_data['room_structure'] = "분리형"  # 기본값
                        
                        print(f"DEBUG: 매물 {idx} - 방: {listing_data['room_count']}개, 욕실: {listing_data['bathroom_count']}개, 구조: {listing_data['room_structure']}")
                    elif line.startswith("입주:"):
                        move_in_text = line.split("입주:")[1].strip()
                        listing_data['move_in_info'] = move_in_text
                        if move_in_text == "즉시":
                            listing_data['move_in_value'] = "1"
                        elif move_in_text == "협의":
                            listing_data['move_in_value'] = "2"
                        elif move_in_text == "기타":
                            listing_data['move_in_value'] = "3"
                        elif move_in_text.startswith("기타 /"):
                            listing_data['move_in_value'] = "3"
                            listing_data['move_in_day'] = move_in_text.split("/")[1].strip()
                        else:
                            print(f"⚠️ 매물 {idx} - 입주 정보가 예상과 다릅니다: {move_in_text}")
                        print(f"DEBUG: 매물 {idx} - 입주: {move_in_text} (값: {listing_data['move_in_value']})")
                    elif line.startswith("상세설명:"):
                        listing_data['content'] = line.split("상세설명:")[1].strip()
                        print(f"DEBUG: 매물 {idx} - 상세설명: {listing_data['content'][:30]}...")
                    elif line.startswith("용도:"):
                        listing_data['usage'] = line.split("용도:")[1].strip()
                        print(f"DEBUG: 매물 {idx} - 용도: {listing_data['usage']}")
                
                # 주소에서 구/동 추출
                if listing_data['address']:
                    parts = listing_data['address'].split()
                    listing_data['district'] = next((p for p in parts if p.endswith("구")), None)
                    listing_data['dong'] = next((p for p in parts if p.endswith("동")), None)
                    print(f"DEBUG: 매물 {idx} - 추출된 지역: {listing_data['district']} {listing_data['dong']}")
                
                # 필수 데이터 검증
                missing_fields = []
                if not listing_data['property_type']:
                    missing_fields.append('종류')
                if not listing_data['address']:
                    missing_fields.append('주소')
                if not listing_data['transaction_type']:
                    missing_fields.append('거래')
                
                if missing_fields:
                    print(f"⚠️ 매물 {idx} - 필수 데이터 누락: {missing_fields}")
                else:
                    print(f"DEBUG: 매물 {idx} - 파싱 완료")
                
                listings.append(listing_data)
        
        print(f"✓ 파일 읽기 완료, 총 {len(listings)}개 매물 추출")
        return listings
    except Exception as e:
        print(f"❌ TXT 파일 읽기 오류: {e}")
        print(f"DEBUG: 오류 발생 위치 - 파일: {txt_path}")
        traceback.print_exc()
        exit()

if __name__ == "__main__":
    start_chrome_with_debugging()
    time.sleep(5)

    root = tkinter.Tk()
    root.withdraw()
    TXT_FILE_PATH = filedialog.askopenfilename(title="TXT 파일 선택", filetypes=(("TXT 파일","*.txt"),("모든 파일","*.*")))
    root.destroy()

    if not TXT_FILE_PATH:
        print("❌ 파일 선택 취소")
        exit()

    print(f"✓ 선택된 TXT 파일: {TXT_FILE_PATH}")
    encoding = chardet.detect(open(TXT_FILE_PATH,'rb').read())['encoding']
    print(f"✓ 파일 인코딩 감지: {encoding}")

    listings = extract_listings_from_txt(TXT_FILE_PATH, encoding)

    # 포맷팅된 출력 예시
    example_text = "청담e-편한세상1차 [전세] - 올수리(내부깨끗) 확장형 방3,화1 - 고층 전망좋음 - 9월중순 입주협의 * 조건 정리 / 일정 조율 / 소유자 협의 * 현장답사 -> 조건조율 및 계약금입금 -> 잔금일까지 정확하고 깔끔한 진행 도와드리겠습니다. * 공동중개 감사합니다. ☎ 담당자 010-4331-2032"
    formatted_example = format_text_with_line_breaks(example_text)
    print("포맷팅된 예시 출력:")
    print(formatted_example)

    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
        
        print("브라우저 연결 시도 중...")
        # ChromeDriver 없이 직접 연결 시도
        driver = webdriver.Chrome(options=chrome_options)
        print("✓ 브라우저 연결 성공")
        
        # '시작'을 입력하여 자동화를 시작
        user_input = input("'시작'을 입력하여 자동화를 시작하세요: ")
        if user_input.strip().lower() != "시작":
            print("❌ '시작'을 입력하지 않아 자동화를 종료합니다.")
            exit()

        # 웹 페이지의 입력 필드에 줄바꿈이 포함된 텍스트 입력
        try:
            input_field = driver.find_element(By.XPATH, '//*[@id="tr42"]/td[2]/textarea')
            # 외부 입력으로부터 텍스트를 받아옴
            raw_text = listing['content']  # 예시로 listing 데이터의 'content' 필드를 사용
            parts = re.split(r'(\s*-\s*|\s*\*\s*|\s*->\s*|\s*☎\s*)', raw_text)
            text_with_line_breaks = ''
            for part in parts:
                if part.strip() in ['-', '*', '->', '☎']:
                    text_with_line_breaks += Keys.ENTER + part.strip() + Keys.ENTER
                else:
                    text_with_line_breaks += part.strip() + ' '
            
            print("DEBUG: Final text with line breaks:", text_with_line_breaks)  # 디버깅용 로그
            input_field.send_keys(text_with_line_breaks)
            print("✓ 입력 필드에 텍스트 입력 완료")
        except Exception as e:
            print(f"❌ 입력 필드에 텍스트 입력 실패: {e}")

    except Exception as e:
        print(f"❌ 브라우저 연결 실패 또는 입력 필드에 텍스트 입력 실패: {e}")
        print("Chrome이 디버깅 모드로 실행되었는지 확인해주세요.")
        print("Chrome 브라우저 버전을 확인해주세요.")
        exit()

    # 통계 변수 초기화
    success_count = 0
    failed_count = 0
    failed_listings = []

    for idx, listing in enumerate(listings, 1):
        print(f"\n처리 중: 매물 {idx}/{len(listings)}")
        success = run_automation(listing, driver)
        
        if success:
            success_count += 1
            print(f"✅ 매물 {idx} 등록 성공!")
            
            # 등록 완료 버튼 클릭
            try:
                submit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="at_submit"]')))
                submit_btn.click()
                print("✓ 등록 완료 버튼 클릭")
                time.sleep(2)
                
                # 신규 매물 등록 버튼 클릭
                new_listing_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MY_AT_BTN1"]/div[1]/a/img')))
                new_listing_btn.click()
                print("✓ 신규 매물 등록 버튼 클릭")
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ 버튼 클릭 중 오류: {e}")
                # 수동으로 다음 진행
                input("수동으로 다음 매물을 준비한 후 Enter를 눌러주세요...")
        else:
            failed_count += 1
            failed_info = {
                'index': idx,
                'property_type': listing['property_type'],
                'address': listing['address'],
                'transaction_type': listing['transaction_type'],
                'size_type': listing['size_type'],
                'error_reason': '자동화 실패',
                'full_data': listing  # 전체 매물 데이터 추가
            }
            failed_listings.append(failed_info)
            print(f"❌ 매물 {idx} 등록 실패")
            
            # 취소 버튼 클릭
            try:
                cancel_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="farticle"]/div[3]/button[2]')))
                cancel_btn.click()
                print("✓ 취소 버튼 클릭")
                time.sleep(2)
                
                # 신규 매물 등록 버튼 클릭
                new_listing_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MY_AT_BTN1"]/div[1]/a/img')))
                new_listing_btn.click()
                print("✓ 신규 매물 등록 버튼 클릭")
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ 버튼 클릭 중 오류: {e}")
                # 수동으로 다음 진행
                input("수동으로 다음 매물을 준비한 후 Enter를 눌러주세요...")

    # 최종 통계 출력
    print("\n" + "="*60)
    print("📊 매물 등록 완료 통계")
    print("="*60)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {failed_count}개")
    print(f"📈 성공률: {success_count/(success_count+failed_count)*100:.1f}%")
    
    if failed_listings:
        print(f"\n❌ 실패한 매물 목록:")
        print("-" * 60)
        for failed in failed_listings:
            print(f"매물 {failed['index']}: {failed['property_type']} - {failed['address']}")
            print(f"  거래유형: {failed['transaction_type']}, 면적: {failed['size_type']}")
            print(f"  실패사유: {failed['error_reason']}")
            print()
    
    # 실패 매물 상세 정보를 파일로 저장
    if failed_listings:
        failed_file = "failed_listings.txt"
        with open(failed_file, 'w', encoding='utf-8') as f:
            f.write("실패한 매물 상세 정보\n")
            f.write("="*50 + "\n\n")
            for failed in failed_listings:
                f.write(f"매물 {failed['index']}:\n")
                f.write(f"  종류: {failed['property_type']}\n")
                f.write(f"  주소: {failed['address']}\n")
                f.write(f"  거래유형: {failed['transaction_type']}\n")
                f.write(f"  면적: {failed['size_type']}\n")
                f.write(f"  실패사유: {failed['error_reason']}\n")
                f.write("\n  📋 전체 매물 정보:\n")
                
                # 전체 매물 데이터 저장
                full_data = failed['full_data']
                f.write(f"    종류: {full_data.get('property_type', 'N/A')}\n")
                f.write(f"    주소: {full_data.get('address', 'N/A')}\n")
                f.write(f"    거래유형: {full_data.get('transaction_type', 'N/A')}\n")
                f.write(f"    보증금: {full_data.get('deposit', 'N/A')}\n")
                f.write(f"    월세: {full_data.get('monthly_rent', 'N/A')}\n")
                f.write(f"    매매가: {full_data.get('sale_price', 'N/A')}\n")
                f.write(f"    전세가: {full_data.get('lease_price', 'N/A')}\n")
                f.write(f"    면적: {full_data.get('size_type', 'N/A')}\n")
                f.write(f"    방구조: {full_data.get('room_structure', 'N/A')}\n")
                f.write(f"    방개수: {full_data.get('room_count', 'N/A')}\n")
                f.write(f"    욕실개수: {full_data.get('bathroom_count', 'N/A')}\n")
                f.write(f"    입주정보: {full_data.get('move_in_info', 'N/A')}\n")
                f.write(f"    입주값: {full_data.get('move_in_value', 'N/A')}\n")
                f.write(f"    입주날짜: {full_data.get('move_in_day', 'N/A')}\n")
                f.write(f"    용도: {full_data.get('usage', 'N/A')}\n")
                f.write(f"    상세설명: {full_data.get('content', 'N/A')[:100]}...\n")
                f.write("-" * 50 + "\n")
        print(f"📄 실패 매물 상세 정보가 '{failed_file}' 파일에 저장되었습니다.")

    driver.quit()
    if platform.system() == "Windows":
        subprocess.run(["taskkill","/f","/im","chrome.exe"],check=False)
    else:
        subprocess.run(["pkill","-9","chrome"],check=False)
    print("✅ 모든 작업 완료")
