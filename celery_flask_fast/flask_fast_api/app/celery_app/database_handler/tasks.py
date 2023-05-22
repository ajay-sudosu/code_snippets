import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
import os
import shutil
import requests
from app_modules import async_data_process, master_data_obj, extract_images, Media, Event, MediaTagMap, MediaDuration, VideoStream
from api_connectivity.utility import Utility, logging
from celery_app.main import app
from flask import Response, jsonify


configuration = {"debug": 0,
                 "log_file": 'celery.log',
                 "mode": 1,
                 "enable_db": True,
                 "enable_redis": False,
                 "enable_rabbitmq_consumer": False,
                 "enable_rabbitmq_publisher": False,
                 "redis_db": 8,
                 "log_level": logging.DEBUG,
                 "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                 "database": "ZestIot_AppliedAI"}
# rabbitmq_consumer = {"exchange": "Task", "queue": "task_queue", "routing_keys": ["task.#"]}
connect = Utility(configuration=configuration)



@app.task
def review_again_background(_data):
    data = _data['data']
    for duration in data:
        id = duration["id"]
        if id is not None:
            filter_params = {'id': id}
            zip_location = os.path.join(app.config.get('static_path'), duration.get('media_end_point'))  # forward slashes
            local_zip_location = os.path.join(app.config.get('static_path'), os.path.splitext(duration.get('media_end_point'))[0])  # forward slashes

            if os.path.exists(local_zip_location):
                local_image_end_point = os.path.join(local_zip_location, str(id))  # forward slashes
                if os.path.exists(local_image_end_point):
                    shutil.rmtree(local_image_end_point)
                    if os.path.exists(zip_location):
                        os.remove(zip_location)

            elif os.path.exists(zip_location):
                extract_images.unzip(zip_location)
                local_image_end_point = os.path.join(local_zip_location, str(id))  # forward slashes
                shutil.rmtree(local_image_end_point)
                os.remove(zip_location)

            else:
                print("not found")

            async_data_process.remove_blob(duration['media_end_point'])
            filter_params_tag = {
                'media_duration_id': id
            }
            async_data_process.delete(MediaTagMap, filter_params_tag)
            async_data_process.delete(MediaDuration, filter_params)
    response = requests.post("http://cvd2s.eastus.cloudapp.azure.com/fastapi/extract", json=_data)


@app.task
def storage_update_background(_data):
    event = _data.get("event")
    if event == 'upload_start_event':
        _cam_id = _data["cam_id"]
        # _capture_start_datetime = _data['capture_start_datetime']
        # _capture_end_datetime = _data['capture_end_datetime']
        _video_upload_start_datetime = _data['video_upload_start_datetime']
        _video_end_point = _data['video_end_point']
        _video_upload_source = _data["video_upload_source"]
        _video_upload_source_id = _data['video_upload_source_id']
        _state = _data['state']
        insert_params = {'cam_id': int(master_data_obj.camera_mapper.get(_cam_id)) if master_data_obj.camera_mapper.get(
            _cam_id).isdigit() else master_data_obj.camera_mapper.get(_cam_id),
                         # 'capture_start_datetime': _capture_start_datetime,
                         # 'capture_end_datetime': _capture_end_datetime,
                         'video_upload_start_datetime': _video_upload_start_datetime,
                         'video_end_point': _video_end_point,
                         'video_upload_source': _video_upload_source,
                         'video_upload_source_id': _video_upload_source_id,
                         'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(
                             _state).isdigit() else None}
        async_data_process.insert(table=Media, insert_params=insert_params)
        response = jsonify('added successfully!')
        response.status_code = 200
        return response
    elif event == 'upload_end_event':
        _cam_id = _data["cam_id"]
        _video_upload_end_datetime = _data['video_upload_end_datetime']
        _video_end_point = _data['video_end_point']
        _state = _data['state']
        filter_params = {'cam_id': int(master_data_obj.camera_mapper.get(_cam_id)) if master_data_obj.camera_mapper.get(
            _cam_id).isdigit() else master_data_obj.camera_mapper.get(_cam_id),
                         'video_end_point': _video_end_point}
        update_params = {'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(
            _state).isdigit() else None,
                         'video_upload_end_datetime': _video_upload_end_datetime}
        async_data_process.update(table=Media, update_params=update_params, filter_params=filter_params)
        resp = jsonify('updated successfully!')
        resp.status_code = 200
        return resp
    elif event == 'automatic':
        _cam_id = _data["cam_id"]
        _video_upload_start_datetime = _data['video_upload_end_datetime']
        _video_upload_end_datetime = _data['video_upload_end_datetime']
        _video_end_point = _data['video_end_point']
        _video_upload_source = _data["video_upload_source"]
        _video_upload_source_id = _data['video_upload_source_id']
        _state = _data['state']
        insert_params = {'cam_id': int(master_data_obj.camera_mapper.get(_cam_id)) if master_data_obj.camera_mapper.get(
            _cam_id).isdigit() else master_data_obj.camera_mapper.get(_cam_id),
                         'video_upload_start_datetime': _video_upload_start_datetime,
                         'video_upload_end_datetime': _video_upload_start_datetime,
                         'video_end_point': _video_end_point,
                         'video_upload_source': _video_upload_source,
                         'video_upload_source_id': _video_upload_source_id,
                         'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(
                             _state).isdigit() else None}
        async_data_process.insert(table=Media, insert_params=insert_params)
        response = jsonify('added successfully!')
        response.status_code = 200
        return response
    else:
        resp = jsonify('No event detected!')
        resp.status_code = 200
        return resp


@app.task
def event_update_background(_event_data):
    _event = _event_data['event']
    insert_update_params = {}
    filter_params = {}
    if 'iot_event_id' in _event_data:
        _iot_event_id = _event_data.get('iot_event_id')
        filter_params['iot_event_id'] = _iot_event_id
        if _event == "json_event":
            for key in _event_data:
                value = _event_data.get(key)
                if value is not None:
                    if key == 'event':
                        continue
                    elif key == 'event_name':
                        insert_update_params['type_id'] = int(
                            master_data_obj.event_mapper.get(value)) if master_data_obj.event_mapper.get(
                            value).isdigit() else None
                    elif key == 'camera_name':
                        insert_update_params['camera_id'] = int(
                            master_data_obj.camera_mapper.get(value)) if master_data_obj.camera_mapper.get(
                            value).isdigit() else master_data_obj.camera_mapper.get(value)
                    else:
                        insert_update_params[key] = value
        elif _event == "image_event":
            _image_end_point = _event_data.get('image_end_point')
            if _image_end_point is not None:
                insert_update_params['image_end_point'] = _image_end_point
        async_data_process.insert_update(table=Event, insert_update_params=insert_update_params, filter_params=filter_params)
        response = jsonify('added successfully!')
        response.status_code = 200
        return response

    else:
        if _event == "image_event":
            _cam_name = _event_data.get('cam_name')
            _event_start_datetime = _event_data.get('event_start_datetime')
            _event_name = _event_data.get('event_name')
            _image_end_point = _event_data.get('image_end_point')
            insert_params = {"camera_id": int(master_data_obj.camera_mapper.get(str(_cam_name))),
                             "image_end_point": _image_end_point,
                             "start_datetime": _event_start_datetime,
                             "type_id": int(master_data_obj.event_mapper.get(str(_event_name)))}
            async_data_process.insert(table=Event, insert_params=insert_params)
            response = jsonify('added successfully!')
            response.status_code = 200
            return response
        else:
            response = jsonify('Not successfully!')
            response.status_code = 201
            return response

@app.task
def extract_background(filter_params, update_params, _durations, media_status_id, video_end_point):
    _durations_ids = []
    async_data_process.update(Media, update_params=update_params, filter_params=filter_params)
    for duration in _durations:
        insert_params = {'media_status_id': int(media_status_id),
                         'start_time': duration['start'],
                         'end_time': duration['end'],
                         'image_count': duration['images_count'],
                         'remark': duration['remarks'],
                         'extraction_status': 'extraction_pending'}
        id = async_data_process.insert(MediaDuration, insert_params=insert_params)
        _durations_ids.append(id)
        for class_ in duration['classes']:
            insert_params = {'media_duration_id': int(id),
                             'tag_id': int(master_data_obj.class_mapper.get(class_)) if master_data_obj.class_mapper.get(
                                 class_).isdigit() else master_data_obj.class_mapper.get(class_)}
            async_data_process.insert(MediaTagMap, insert_params=insert_params)
    extract_images.extract_images(video_end_point, _durations, _durations_ids, int(media_status_id))

@app.task
def upload_file_end_event_background(upload_end_event_data):
    async_data_process.upload(file_to_upload=upload_end_event_data['local_video_location'], _upload_location=upload_end_event_data['media_end_point'])
    upload_end_event = {"cam_id": upload_end_event_data['_cam_id'],
                        "video_upload_end_datetime": upload_end_event_data['date_of_upload'].strftime('%Y-%m-%d %H:%M:%S'),
                        "video_end_point": upload_end_event_data['media_end_point'],
                        "event": "upload_end_event",
                        "state": "review_pending"}
    storage_update_background(upload_end_event)

@app.task
def video_feed_background():
    video_stream = VideoStream()
    if video_stream.hpcl_client:
        try:
            video_stream.hpcl_client.close()
        except Exception as e_:
            pass
        video_stream.hpcl_client = None
    frame = video_stream.gen_frames()
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')


