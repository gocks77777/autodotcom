import tkinter as tk
from tkinter import messagebox
import subprocess

def run_almostdone():
    try:
        subprocess.run(["python", "almostdone.py"], check=True)
        messagebox.showinfo("Success", "almostdone.py 실행 완료")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"almostdone.py 실행 중 오류 발생: {e}")

def run_analyzefinal():
    try:
        subprocess.run(["python", "analyzefinal.py"], check=True)
        messagebox.showinfo("Success", "analyzefinal.py 실행 완료")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"analyzefinal.py 실행 중 오류 발생: {e}")

# Update the check_txt_file function to use a Text widget for selectable content
def check_txt_file():
    try:
        with open("failed_listings.txt", "r", encoding="utf-8") as file:
            content = file.read()
            # Create a new window to display the content
            txt_window = tk.Toplevel(root)
            txt_window.title("TXT 파일 내용")
            txt_window.geometry("400x300")
            
            # Add a Text widget to display the content
            text_widget = tk.Text(txt_window, wrap="word")
            text_widget.insert("1.0", content)
            text_widget.config(state="normal")  # Allow text selection
            text_widget.pack(expand=True, fill="both")
    except FileNotFoundError:
        messagebox.showerror("Error", "failed_listings.txt 파일을 찾을 수 없습니다.")

root = tk.Tk()
root.title("My Application")
root.geometry("400x300")  # Set the window size to 400x300

# Use a Frame to organize buttons
button_frame = tk.Frame(root)
button_frame.pack(expand=True, fill="both", pady=50)  # Add padding to center vertically

# Adjust button width and center align
btn1 = tk.Button(button_frame, text="등록 자동화 시작", command=run_almostdone, width=30, height=2)
btn1.pack(pady=10, padx=10, side="top")

btn2 = tk.Button(button_frame, text="엑셀을 메모장으로 변환 시작", command=run_analyzefinal, width=30, height=2)
btn2.pack(pady=10, padx=10, side="top")

btn3 = tk.Button(button_frame, text="미등록 매물 확인", command=check_txt_file, width=30, height=2)
btn3.pack(pady=10, padx=10, side="top")

root.mainloop()
