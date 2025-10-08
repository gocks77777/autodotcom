from flask import Flask, jsonify, request
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)

# 기본 경로
@app.route('/')
def home():
    """기본 홈페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>부동산 매물 자동화 서비스</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; }
            .btn { padding: 15px 30px; margin: 10px; font-size: 16px; text-decoration: none; 
                   background-color: #4CAF50; color: white; border-radius: 5px; }
            .btn:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 부동산 매물 자동화 서비스</h1>
            <p>서비스가 정상적으로 실행 중입니다.</p>
            
            <h3>📋 사용 가능한 기능</h3>
            <p><a href="/admin" class="btn">🎛️ 관리자 패널</a></p>
            <p><a href="/check_permission" class="btn">🔐 권한 확인</a></p>
            
            <h3>📡 API 엔드포인트</h3>
            <ul style="text-align: left;">
                <li><strong>GET /check_permission</strong> - 클라이언트 권한 확인</li>
                <li><strong>POST /control_permission</strong> - 권한 제어 (관리자용)</li>
                <li><strong>GET /admin</strong> - 관리자 웹 패널</li>
                <li><strong>GET /run_almostdone</strong> - almostdone.py 실행</li>
                <li><strong>GET /run_analyzefinal</strong> - analyzefinal.py 실행</li>
                <li><strong>GET /check_txt_file</strong> - TXT 파일 확인</li>
            </ul>
            
            <p><small>🚀 Powered by Flask & Render</small></p>
        </div>
    </body>
    </html>
    """

# 권한 제어 파일
PERMISSION_FILE = "permission_control.json"

def load_permission_status():
    """권한 상태를 로드합니다."""
    try:
        if os.path.exists(PERMISSION_FILE):
            with open(PERMISSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 기본값: 허용
            default_permission = {
                "enabled": True,
                "message": "프로그램 사용이 허용되었습니다.",
                "last_updated": datetime.now().isoformat()
            }
            save_permission_status(default_permission)
            return default_permission
    except Exception as e:
        # 오류 시 기본값 반환
        return {
            "enabled": True,
            "message": "권한 확인 중 오류가 발생했습니다.",
            "last_updated": datetime.now().isoformat()
        }

def save_permission_status(permission_data):
    """권한 상태를 저장합니다."""
    try:
        with open(PERMISSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(permission_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"권한 저장 오류: {e}")

# 권한 확인 API
@app.route('/check_permission')
def check_permission():
    """클라이언트가 프로그램 실행 권한을 확인합니다."""
    permission = load_permission_status()
    return jsonify(permission)

# 권한 제어 API (관리자용)
@app.route('/control_permission', methods=['POST'])
def control_permission():
    """권한을 활성화/비활성화합니다."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        message = data.get('message', '')
        
        if enabled:
            message = message or "프로그램 사용이 허용되었습니다."
        else:
            message = message or "프로그램 사용이 일시적으로 중단되었습니다."
        
        permission_data = {
            "enabled": enabled,
            "message": message,
            "last_updated": datetime.now().isoformat()
        }
        
        save_permission_status(permission_data)
        
        status_text = "활성화" if enabled else "비활성화"
        return jsonify({
            "status": "success", 
            "message": f"권한이 {status_text}되었습니다.",
            "permission": permission_data
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"권한 제어 중 오류 발생: {str(e)}"})

# 권한 상태 확인 페이지 (관리자용)
@app.route('/admin')
def admin_page():
    """간단한 관리자 페이지"""
    permission = load_permission_status()
    status_color = "green" if permission["enabled"] else "red"
    status_text = "활성화됨" if permission["enabled"] else "비활성화됨"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>프로그램 권한 제어</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .status {{ color: {status_color}; font-weight: bold; font-size: 18px; }}
            button {{ padding: 10px 20px; margin: 10px; font-size: 16px; }}
            .enable {{ background-color: #4CAF50; color: white; border: none; }}
            .disable {{ background-color: #f44336; color: white; border: none; }}
            .info {{ background-color: #f0f0f0; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>🎛️ 프로그램 권한 제어 패널</h1>
        
        <div class="info">
            <h3>현재 상태: <span class="status">{status_text}</span></h3>
            <p><strong>메시지:</strong> {permission["message"]}</p>
            <p><strong>마지막 업데이트:</strong> {permission["last_updated"]}</p>
        </div>
        
        <h3>권한 제어</h3>
        <button class="enable" onclick="setPermission(true)">✅ 프로그램 활성화</button>
        <button class="disable" onclick="setPermission(false)">❌ 프로그램 비활성화</button>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
        function setPermission(enabled) {{
            const message = enabled ? 
                "프로그램 사용이 허용되었습니다." : 
                "프로그램 사용이 일시적으로 중단되었습니다.";
                
            fetch('/control_permission', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ enabled: enabled, message: message }})
            }})
            .then(response => response.json())
            .then(data => {{
                document.getElementById('result').innerHTML = 
                    '<p style="color: green;">✅ ' + data.message + '</p>';
                setTimeout(() => location.reload(), 1500);
            }})
            .catch(error => {{
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">❌ 오류: ' + error + '</p>';
            }});
        }}
        </script>
    </body>
    </html>
    """
    return html

@app.route('/run_almostdone')
def run_almostdone():
    try:
        subprocess.run(["python", "almostdone.py"], check=True)
        return jsonify({"status": "success", "message": "almostdone.py 실행 완료"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"almostdone.py 실행 중 오류 발생: {e}"})

@app.route('/run_analyzefinal')
def run_analyzefinal():
    try:
        subprocess.run(["python", "analyzefinal.py"], check=True)
        return jsonify({"status": "success", "message": "analyzefinal.py 실행 완료"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"analyzefinal.py 실행 중 오류 발생: {e}"})

@app.route('/check_txt_file')
def check_txt_file():
    try:
        with open("failed_listings.txt", "r", encoding="utf-8") as file:
            content = file.read()
            return jsonify({"status": "success", "content": content})
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "failed_listings.txt 파일을 찾을 수 없습니다."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)