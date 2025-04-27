import os
import shutil
import smtplib
from datetime import datetime
from time import sleep
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load thông tin từ .env
load_dotenv()

# Lấy thông tin email từ file .env
SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("EMAIL_RECEIVER")

def send_email(subject, body):
    """Hàm gửi email thông báo kết quả backup."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = RECEIVER

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
        print("Email đã được gửi thành công.")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")

def backup():
    """Hàm sao lưu file database và gửi email thông báo kết quả."""
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    src_folder = "databases"
    dst_folder = "backups"
    os.makedirs(dst_folder, exist_ok=True)

    success = []
    fail = []

    for file in os.listdir(src_folder):
        if file.endswith('.sql') or file.endswith('.sqlite3'):
            try:
                src_path = os.path.join(src_folder, file)
                new_name = f"{file.rsplit('.', 1)[0]}_{now}.{file.rsplit('.', 1)[1]}"
                dst_path = os.path.join(dst_folder, new_name)
                shutil.copy2(src_path, dst_path)
                success.append(file)
            except Exception as e:
                fail.append(f"{file} - Lỗi: {e}")

    # Gửi email thông báo kết quả
    if success:
        subject = "✅ Backup Thành Công"
        body = "Backup thành công các file:\n" + "\n".join(success)
    else:
        subject = "❌ Backup Thất Bại"
        body = "Không có file nào được sao lưu."

    if fail:
        body += "\n\nLỗi với các file:\n" + "\n".join(fail)

    send_email(subject, body)

def run_backup_at_midnight():
    """Hàm thực hiện backup lúc 00:00 AM mỗi ngày."""
    while True:
        now = datetime.now()
        # Tính số giây còn lại đến 00:00 AM
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= target_time:
            # Nếu đã qua nửa đêm, lên lịch cho ngày hôm sau
            target_time = target_time.replace(day=now.day + 1)

        # Tính thời gian chờ để đến 00:00 AM
        wait_time = (target_time - now).total_seconds()
        print(f"Chờ {wait_time} giây để đến nửa đêm và backup...")
        sleep(wait_time)  # Dừng lại cho đến 00:00 AM
        backup()

if __name__ == "__main__":
    run_backup_at_midnight()
