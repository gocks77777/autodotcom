from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World! Flask is working!"

@app.route('/admin')
def admin():
    return "Admin page is working!"

@app.route('/check_permission')
def check_permission():
    return {"enabled": True, "message": "Test permission check"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
