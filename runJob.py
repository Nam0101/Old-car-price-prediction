from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
import crawler_bonbanh as crawler_bonbanh
import crawler_oto as crawler_oto
from flask import Flask, request, jsonify
import pickle
import pandas as pd
from category_encoders import TargetEncoder, JamesSteinEncoder
from sklearn.preprocessing import OneHotEncoder
import os
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import clean_data as clean
import preprocess as preprocess
import train_model as train


def crawl_bonbanh():
    crawler_bonbanh.main()


def crawl_oto():
    crawler_oto.craw()


def clean_data():
    clean.main()


def preprocessing():
    preprocess.main()


def train_model():
    train.main()


def my_listener(event):
    if event.exception:
        print('The job ' + event.job_id + ' crashed :(')
    else:
        print('The job ' + event.job_id + ' worked :)')

    # Use a dictionary to track job dependencies
    job_dependencies = {
        'bonbanh': 'crawl_oto',  # Use the correct function names
        'crawl_oto': 'clean_data',
        'clean_data': 'preprocessing',
        'preprocessing': 'train_model',
    }

    if event.job_id in job_dependencies:
        next_job_id = job_dependencies[event.job_id]
        # Schedule the next job only if it's not already scheduled
        if not scheduler.get_job(next_job_id):
            scheduler.add_job(globals()[next_job_id], 'date', run_date=datetime.now(),
                              id=next_job_id)  # Use datetime.now()


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Only mỗi 2h sáng thứ 2
    scheduler.add_job(crawl_bonbanh, 'cron', day_of_week='mon', hour=2, id='bonbanh')

    scheduler.start()
