from celery import shared_task


@shared_task
def my_scheduled_function():
    print("Scheduled Function Starts")
    # Some activity
    print("Scheduled Function Ends")