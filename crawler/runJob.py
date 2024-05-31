from apscheduler.schedulers.blocking import BlockingScheduler


def job_function():
    # Đây là nơi bạn đặt mã để thực hiện công việc của bạn
    print("Hello World")


# Khởi tạo một lịch trình
scheduler = BlockingScheduler()

# Thêm công việc vào lịch trình để chạy mỗi tuần vào thứ 2 lúc 10:00
scheduler.add_job(job_function, 'cron', day_of_week='mon', hour=10)

# Bắt đầu lịch trình
scheduler.start()
