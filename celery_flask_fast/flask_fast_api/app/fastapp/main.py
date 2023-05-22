import json
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from celery_app.main import insert_rules_background, review_again_background, event_update_background, storage_update_background, extract_background, upload_file_end_event_background, video_feed_background, save_annotation_background, submit_annotation_background, test1_background, re_annotate_background, submit_remarks_background
from app_modules import Media, MediaDuration, MediaTagMap, extract_images, Event, master_data_obj, \
    async_data_process, VideoStream
from fastapi import BackgroundTasks, FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from api_connectivity.utility import Utility
from configuration import constants
from threading import Thread
from time import sleep
import logging

connect = Utility(configuration=constants.fast_api_utility_configuration, rabbitmq_publisher=constants.fast_api_publisher)
fast_app = FastAPI()
origins = ["*"]
fast_app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                        allow_headers=["*"])


@fast_app.get('/fastapi/ett')
def extract():
    print('get call')




@fast_app.post('/fastapi/resumable_upload_start_event')
async def upload_file_start_event(background_tasks: BackgroundTasks, request: Request, upload_start_event: dict = Body(...)):
    connect.loginfo('fastapp resumable upload start event is called')
    if upload_start_event.get('userid') is None:
        upload_start_event['userid'] = request.headers.get('user-id')
    background_tasks.add_task(storage_update_background_publisher, upload_start_event)
    response = {'message': 'added successfully!', 'status_code': 200}
    return response


@fast_app.post('/fastapi/resumable_upload_end_event')
async def upload_file_end_event(background_tasks: BackgroundTasks, request: Request, upload_end_event_data: dict = Body(...)):
    connect.loginfo('fastapp resumable upload end event is called')
    try:
        if upload_end_event_data.get('userid') is None:
            upload_end_event_data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling celery task upload_file_end_event_background_publisher', level='debug')
        background_tasks.add_task(upload_file_end_event_background_publisher, upload_end_event_data)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in upload_file_end_event " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def upload_file_end_event_background_publisher(event):
    try:
        sleep(1)
        connect.loginfo("starting accessing the celery task upload file end event  background")
        upload_file_end_event_background.delay(event)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in upload_file_end_event_background_publisher " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')




@fast_app.post('/fastapi/extract')
async def extract(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    connect.loginfo('fastapp extract is called')
    try:
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
        media_status_id = _data['media_id']
        video_end_point = _data['video_path']
        _durations = _data['data']
        filter_params = {'id': int(media_status_id)}
        update_params = {'state_id': int(master_data_obj.state_mapper.get(connect.config_json['status']['extract_pending']))}
        connect.loginfo('calling celery task extract_background', level='debug')
        background_tasks.add_task(extract_background_publisher, filter_params, update_params, _durations, media_status_id,
                                  video_end_point, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in extarct " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def extract_background_publisher(filter_params, update_params, _durations, media_status_id, video_end_point, _data):
    sleep(1)
    connect.loginfo("starting accessing the celery task extract background")
    extract_background.delay(filter_params, update_params, _durations, media_status_id, video_end_point, _data)


@fast_app.post('/fastapi/event_update')
async def event_update(background_tasks: BackgroundTasks, request: Request, _event_data: dict = Body(...)):
    connect.loginfo('fastapp event update is called')
    try:
        if _event_data.get('userid') is None:
            _event_data['userid'] = request.headers.get('user-id')
        _event_data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling celery task event_update_background', level='debug')
        background_tasks.add_task(event_update_background_publisher, _event_data)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in event update " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def event_update_background_publisher(event):
    sleep(1)
    connect.loginfo("starting accessing the celery task event update background ")
    event_update_background.delay(event)


@fast_app.post('/fastapi/storage_update')
async def storage_update(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...), resumable_video_data=None):
    connect.loginfo('fastapp storage update is called')
    try:
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
        _data = _data if not resumable_video_data else resumable_video_data
        _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling celery task storage_update_background', level='debug')
        background_tasks.add_task(storage_update_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in storage update" + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def storage_update_background_publisher(event):
    sleep(1)
    connect.loginfo("starting accessing the celery task storage update background")
    storage_update_background.delay(event)


@fast_app.post('/fastapi/review_again')
async def review_again(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    connect.loginfo('fastap review again is called')
    try:
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling celery task review_again_background', level='debug')
        background_tasks.add_task(review_again_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in review again " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def review_again_background_publisher(event):
    sleep(1)
    connect.loginfo("starting accessing the celery task review again  background")
    review_again_background.delay(event)


@fast_app.post('/fastapi/save_annotation')
async def save_annotation(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    try:
        connect.loginfo('fastapp save annotation is called')
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling celery task save_annotation_background', level='debug')
        background_tasks.add_task(save_annotation_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in save annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def save_annotation_background_publisher(event):
    sleep(1)
    connect.loginfo("starting accessing the celery task save annotation background")
    save_annotation_background.delay(event)


@fast_app.post('/fastapi/submit_annotation')
async def submit_annotation(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    connect.loginfo('fastapp submit annotation is called')
    try:
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling celery task submit_annotation_background', level='debug')
        background_tasks.add_task(submit_annotation_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in submit annotation" + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def submit_annotation_background_publisher(event):
    sleep(1)
    connect.loginfo("starting accessing the celery task submit annotation background")
    submit_annotation_background.delay(event)


@fast_app.post('/fastapi/test1')
async def test1(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    if _data.get('userid') is None:
        _data['userid'] = request.headers.get('user-id')
    connect.loginfo('calling celery task test1_background', level='debug')
    background_tasks.add_task(test1_background_publisher, _data)
    response = {'message': 'added successfully!', 'status_code': 200}
    return response


@fast_app.post('/fastapi/insert_rules')
async def insert_rules(background_tasks: BackgroundTasks, _data: dict = Body(...)):
    connect.loginfo('fastapp insert rule api is called')
    try:
        """fastapi insert_rules will be called by the flaskapi insert rules """
        connect.loginfo('calling celery task insert_rules_background', level='debug')
        background_tasks.add_task(insert_rules_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in insert rules" + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def insert_rules_background_publisher(event):
    """thi function will call the by the fastapi inser_rules and this will start the task insert rules background in the celery task"""
    sleep(1)
    connect.loginfo("starting accessing the celery task insert rules background")
    insert_rules_background.delay(event)


@fast_app.post('/fastapi/re_annotate_images')
async def re_annotate_images(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    connect.loginfo('fastapp re annotate  is called')
    try:
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
            connect.loginfo('calling celery task re_annotate_background', level='debug')
        background_tasks.add_task(re_annotate_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in re annotate " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def re_annotate_background_publisher(event):
    """thi function will call the by the fastapi re_annotate and this will start the task re_annotate background in the celery task"""
    sleep(1)
    connect.loginfo("starting accessing the celery task reannotate background")
    re_annotate_background.delay(event)


@fast_app.post('/fastapi/submit_remarks')
async def submit_remarks(background_tasks: BackgroundTasks, request: Request, _data: dict = Body(...)):
    connect.loginfo('fastapp submit_remarks  is called')
    try:
        if _data.get('userid') is None:
            _data['userid'] = request.headers.get('user-id')
            connect.loginfo('calling celery task re_annotate_background', level='debug')
        background_tasks.add_task(submit_remarks_background_publisher, _data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in submit_remarks " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


def submit_remarks_background_publisher(event):
    """thi function will call the by the fastapi re_annotate and this will start the task re_annotate background in the celery task"""
    sleep(1)
    connect.loginfo("starting accessing the celery task submit_remarks_background")
    submit_remarks_background.delay(event)


def test1_background_publisher(event):
    sleep(1)
    connect.loginfo("Fast api accessed " + str(event))
    test1_background.delay(event)


def check_task_status():
    connect.loginfo('checking task status')
    while True:
        try:
            for key in connect.master_redis.r.scan_iter("celery-task-meta-*"):
                status = connect.master_redis.get_val(key=key)

                status = json.loads(status)
                status_task = json.loads(status['result'])
                user_id = status_task['user_id']
                if user_id is None:
                    user_id = "#"
                print("user-id", user_id)
                connect.loginfo("%s", status)
                status["publisher"] = "alert"
                status = json.dumps(status)
                if 'Success' in status:
                    connect.master_redis.r.delete(key)
                    connect.publish(event=status, routing_key="task.{}".format(user_id))
                    connect.loginfo("published")
                elif 'Failed' in status:
                    connect.master_redis.r.delete(key)
                    connect.publish(event=status, routing_key="task.{}".format(user_id))
            sleep(30)
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            connect.loginfo(
                "check_task_status thread : exception in check_task_status " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
            sleep(60)


thread = Thread(target=check_task_status, daemon=True)
thread.start()
