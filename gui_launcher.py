from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

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
