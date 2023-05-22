import json
import time
from datetime import datetime

from celery import Celery
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import shutil
import requests
from app_modules import ExtractImages, Classes, async_data_process, master_data_obj, extract_images, Media, Event, MediaTagMap, MediaDuration, VideoStream, Rule_Type, Rule, Operators
from api_connectivity.utility import Utility, logging
from configuration import constants
from flask import Response
from converter import Converter
import subprocess

connect = Utility(configuration=constants.celery_configuration, rabbitmq_publisher=constants.celery_rabbitmq_publisher)
app = Celery('tasks', backend=connect.config_json.get('celery_backend'), broker=connect.config_json.get('celery_broker'))


# app.config_from_object('celery_config')


@app.task
def insert_rules_background(_data):
    start = time.time()
    start_datetime = datetime.now()
    """this takk will get started when user call the flask api insert rule which will call the fastapi insert rule and that will start this task to run and insert the rules in database """
    userid = _data.get('userid')
    try:

        feature_id = master_data_obj.feature_mapper.get(_data.get("feature"))
        rule_kind_id = connect.get_mapper(sql='''select id from m_rule_kind where name ="{}" and kind_type= "{}" '''.format(str(_data.get('rule')), str(_data.get('type'))), var='id')
        major = _data.get("major")
        minor = _data.get("minor")
        custom = _data.get("custom")
        insert_params = {}
        if major is not None:
            for d1 in major:
                tag_id = connect.get_mapper(sql='''select id from m_tags where name = "{}"'''.format(d1['className']), var="id")
                for par in d1['parameters']:
                    # async_data_process.insert_update(table=Rule_Type, insert_update_params={'type': par['keyword']}, filter_params={'type': par['keyword']})
                    filter_params = {
                        'type': par['keyword']
                    }
                    sql = '''select * from m_rule_type where {}'''.format(
                        'and'.join(['{}={}'.format(key, filter_params[key] if not isinstance(filter_params[key], str) else "'" + filter_params[key] + "'") for key in filter_params]))

                    rows_selected = connect.update_database(sql=sql)
                    if rows_selected == 0:
                        sql = '''insert into m_rule_type ({}) values ({})'''.format(','.join([str(key) for key in filter_params.keys()]),
                                                                                    ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in filter_params.values()]))

                        connect.update_database(sql=sql)
                    insert_params = {
                        'feature_id': feature_id,
                        'rule_kind_id': rule_kind_id,
                        'tags_id': tag_id,
                        'rule_id': connect.get_mapper(sql='''select id from m_rule_type where type ="{}"'''.format(par['keyword']), var="id"),
                        'Value': par['value'],
                        'operator_id': connect.get_mapper(sql='''select id from m_operator where name ="{}"'''.format(par['operator']), var="id"),
                        'tag_type': "major"}
                    sql = '''insert into m_rule ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                           ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))

                    connect.update_database(sql=sql)

        if minor is not None:
            for d1 in minor:
                tag_id = connect.get_mapper(sql='''select id from m_tags where name ="{}"'''.format(d1['className']), var="id")
                insert_params['tags_id'] = tag_id
                for par in d1['parameters']:
                    # async_data_process.insert_update(table=Rule_Type, insert_update_params={'type': par['keyword']}, filter_params={'type': par['keyword']})
                    filter_params = {
                        'type': par['keyword']
                    }
                    sql = '''select * from m_rule_type where {}'''.format(
                        'and'.join(['{}={}'.format(key, filter_params[key] if not isinstance(filter_params[key], str) else "'" + filter_params[key] + "'") for key in filter_params]))

                    rows_selected = connect.update_database(sql=sql)
                    if rows_selected == 0:
                        sql = '''insert into m_rule ({}) values ({})'''.format(','.join([str(key) for key in filter_params.keys()]),
                                                                               ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in filter_params.values()]))

                        connect.update_database(sql=sql)
                    insert_params = {
                        'feature_id': feature_id,
                        'rule_kind_id': rule_kind_id,
                        'tags_id': tag_id,
                        'rule_id': connect.get_mapper(sql='''select id from m_rule_type where type ="{}"'''.format(par['keyword']), var="id"),
                        'Value': par['value'],
                        'operator_id': connect.get_mapper(sql='''select id from m_operator where name ="{}"'''.format(par['operator']), var="id"),
                        'tag_type': "minor"}
                    sql = '''insert into m_rule ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                           ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))

                    connect.update_database(sql=sql)

        if custom is not None:
            for d1 in custom:
                for par in d1['parameters']:
                    # async_data_process.insert_update(table=Rule_Type, insert_update_params={'type': par['keyword']}, filter_params={'type': par['keyword']})
                    filter_params = {
                        'type': par['keyword']
                    }
                    sql = '''select * from m_rule_type where {}'''.format(
                        'and'.join(['{}={}'.format(key, filter_params[key] if not isinstance(filter_params[key], str) else "'" + filter_params[key] + "'") for key in filter_params]))

                    rows_selected = connect.update_database(sql=sql)
                    if rows_selected == 0:
                        sql = '''insert into m_rule ({}) values ({})'''.format(','.join([str(key) for key in filter_params.keys()]),
                                                                               ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in filter_params.values()]))

                        connect.update_database(sql=sql)
                    insert_params = {
                        'feature_id': feature_id,
                        'rule_kind_id': rule_kind_id,
                        'rule_id': connect.get_mapper(sql='''select id from m_rule_type where type ="{}"'''.format(par['keyword']), var="id"),
                        'Value': par['value'],
                        'operator_id': connect.get_mapper(sql='''select id from m_operator where name ="{}"'''.format(par['operator']), var="id"),
                    }
                    sql = '''insert into m_rule ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                           ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))

                    connect.update_database(sql=sql)
        end_datetime = datetime.now()
        end = time.time()
        task_result = {"user_id": str(userid), "name": "{} Rule  inserted successfully for feature {}".format(_data.get('rule'), _data.get('feature')), "status": "Success", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in insert rule background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end_datetime = datetime.now()
        end = time.time()
        task_result = {"user_id": userid, "name": "Exception while inserting rule at {} and event is {}".format(str(exc_tb.tb_lineno), str(_data)), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def review_again_background(_data):
    connect.loginfo("Re-extraction process started")
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    try:
        data = list(filter(None, _data['data']))
        media_end_point = _data.get('video_path')
        image_end_point = _data.get('image_path')
        media_id = _data.get('media_id')
        media_data = async_data_process.select(table=Media, filter_params={'id': media_id}, get_first_row=True)
        video_filename = media_data.video_filename
        local_zip_location = os.path.join(connect.config_json.get('static_path'), image_end_point)  # forward slashes
        connect.loginfo(" zip file  - {} location exists - {}".format(str(local_zip_location), os.path.exists(local_zip_location)))
        local_unzip_location = os.path.join(connect.config_json.get('static_path'), os.path.splitext(image_end_point)[0])  # forward slashes
        connect.loginfo("folder  - {} location exists - {}".format(str(local_unzip_location), os.path.exists(local_unzip_location)))
        for duration in data:
            connect.loginfo("update in media id- {}".format(str(media_id)))
            connect.loginfo("{}".format(str(duration)))
            id = duration.get('id')
            if id is not None and id != '':
                media_duration = async_data_process.select(table=MediaDuration, filter_params={"id": id}, get_first_row=True)
                connect.loginfo("{}".format(str(media_duration)))
                if os.path.exists(local_unzip_location):
                    connect.loginfo("going to first if condition- finding the folder")
                    connect.loginfo(" folder  - {} location exists - {}".format(str(local_unzip_location), os.path.exists(local_unzip_location)))
                    local_image_end_point = os.path.join(local_unzip_location, str(id))  # forward slashes
                    if os.path.exists(local_image_end_point):
                        connect.loginfo(" folder with id - {} - {} location exists - {}".format(str(id), str(local_image_end_point), os.path.exists(local_image_end_point)))
                        shutil.rmtree(local_image_end_point)
                        connect.loginfo(" folder with id - {}  - {} location exists - {}-- directory removed successfully".format(str(id), str(local_image_end_point), os.path.exists(local_image_end_point)))
                        connect.loginfo("checking if after deleting folder ,if the same name zip file exists or not ")
                        connect.loginfo("zip file  location exists - {}".format(str(local_zip_location), os.path.exists(local_zip_location)))
                        if os.path.exists(local_zip_location):
                            os.remove(local_zip_location)
                            connect.loginfo("local_zip_location - {} location exists - {} -- successfully removed ".format(str(local_zip_location), os.path.exists(local_zip_location)))

                elif os.path.exists(local_zip_location):
                    connect.loginfo("going to second elif  condition -finding the zip file")
                    connect.loginfo("local_zip_location - {} location exists - {}".format(str(local_zip_location), os.path.exists(local_zip_location)))
                    connect.loginfo("local_zip_location - {} -- unzipping the file ".format(str(local_zip_location)))
                    extract_images.unzip(local_zip_location)
                    connect.loginfo("local_zip_location - {} -- unziped  the file ".format(str(local_zip_location)))
                    local_image_end_point = os.path.join(local_unzip_location, str(id))  # forward slashes
                    connect.loginfo(" folder with id - {}  - {} location exists - {}".format(str(id), str(local_image_end_point), os.path.exists(local_image_end_point)))
                    shutil.rmtree(local_image_end_point)
                    connect.loginfo(" folder with id - {}  - {} location exists - {}-- directory removed successfully".format(str(id), str(local_image_end_point), os.path.exists(local_image_end_point)))
                    connect.loginfo("local_zip_location - {} location exists - {}".format(str(local_zip_location), os.path.exists(local_zip_location)))
                    os.remove(local_zip_location)
                    connect.loginfo("local_zip_location - {} location exists - {} -- successfully removed ".format(str(local_zip_location), os.path.exists(local_zip_location)))

                else:
                    connect.loginfo("going to third else   condition - finding in blob storage ")
                    local_zip_location_back = os.path.dirname(str(local_zip_location))
                    connect.loginfo("the base directory is - {} - status exists - {}".format(local_zip_location_back, os.path.exists(local_zip_location_back)))
                    if os.path.exists(local_zip_location_back):
                        connect.loginfo("Downloading the zip file  to - {} from blob-{} ".format(local_zip_location, media_duration.media_end_point))
                        async_data_process.download(media_duration.media_end_point, local_zip_location)
                        while True:
                            if os.path.exists(local_zip_location):
                                break

                        connect.loginfo("Downloaded")
                        connect.loginfo("local_zip_location - {} location exists - {}  ".format(str(local_zip_location), os.path.exists(local_zip_location)))
                        if os.path.exists(local_zip_location):
                            connect.loginfo("unzipping he file")
                            extract_images.unzip(local_zip_location)
                            connect.loginfo("file unzipped")
                            connect.loginfo(" folder  - {} location exists - {}".format(str(local_unzip_location), os.path.exists(local_unzip_location)))
                            local_image_end_point = os.path.join(local_unzip_location, str(id))  # forward slashes
                            connect.loginfo(" folder with id - {}  - {} location exists - {}".format(str(id), str(local_image_end_point), os.path.exists(local_image_end_point)))
                            shutil.rmtree(local_image_end_point)
                            connect.loginfo(" folder with id - {}  - {} location exists - {}".format(str(id), str(local_image_end_point), os.path.exists(local_image_end_point)))
                            os.remove(local_zip_location)
                            connect.loginfo("local_zip_location - {} location exists - {}  ".format(str(local_zip_location), os.path.exists(local_zip_location)))

                connect.loginfo("removing the zip file from blob storage - {}".format(image_end_point))
                async_data_process.remove_blob(image_end_point)
                connect.loginfo("removed success")
                filter_params_tag = {
                    'media_duration_id': id
                }
                sql = '''delete from media_tags_mapping where {}'''.format(' and '.join(['{}={}'.format(key, filter_params_tag[key] if not isinstance(filter_params_tag[key], str) else "'" + filter_params_tag[key] + "'") for key in filter_params_tag]))

                connect.update_database(sql=sql)
                filter_params = {
                    'id': id
                }

                sql = '''delete from t_media_durations where {}'''.format(' and '.join(['{}={}'.format(key, filter_params[key] if not isinstance(filter_params[key], str) else "'" + filter_params[key] + "'") for key in filter_params]))

                connect.update_database(sql=sql)
        _data['data'] = data
        connect.loginfo("calling the api extract with data- {}".format(str(_data)))
        response = requests.post(connect.config_json.get('app_server_host') + "/extract", json=_data)
        connect.loginfo("call success")

        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": str(userid), "name": "Re-extraction completed of video {}".format(video_filename), "status": "Success",
                       "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        connect.loginfo("re extraction end success")
        return task_result

    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in review_again_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception while reviewing video again at {} and event is {}".format(str(exc_tb.tb_lineno), str(_data)), "status": "Failed", "time_taken": str(end - start),
                       "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result

@app.task
def storage_update_background(_data):
    connect.loginfo('storage update background process start')
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    try:
        event = _data.get("event")
        if event == 'upload_start_event':
            connect.loginfo("upload start event started")
            _cam_id = _data["cam_id"]
            cam_id = _data["camera_id"]
            # _capture_start_datetime = _data['capture_start_datetime']
            # _capture_end_datetime = _data['capture_end_datetime']
            _video_upload_start_datetime = _data['video_upload_start_datetime']
            _video_end_point = _data['video_end_point']
            _video_upload_source = _data["video_upload_source"]
            _video_upload_source_id = _data['video_upload_source_id']
            _state = _data['state']
            insert_params = {'cam_id': cam_id,
                             # 'capture_start_datetime': _capture_start_datetime,
                             # 'capture_end_datetime': _capture_end_datetime,
                             'video_upload_start_datetime': _video_upload_start_datetime,
                             'video_end_point': _video_end_point,
                             'video_upload_source': _video_upload_source,
                             'video_upload_source_id': _video_upload_source_id,
                             'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(
                                 _state).isdigit() else None}

            sql = '''insert into t_media ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                    ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))
            connect.loginfo('upload start  datetime and other details inserting in t_media')
            connect.update_database(sql=sql)
            connect.loginfo('inserted')
            # async_data_process.insert(table=Media, insert_params=insert_params)
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "Video upload to BLOB completed for event {}".format(event), "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)

            print(task_result)
            connect.loginfo('storage update background process end for upload start ended')

            return task_result
        elif event == 'upload_end_event':
            connect.loginfo("upload end event started")
            _cam_id = _data["cam_id"]
            cam_id = _data["camera_id"]
            _video_upload_end_datetime = _data.get('video_upload_end_datetime')
            _video_end_point = _data.get('video_end_point')
            _annotation_end_point = _data.get('annotation_end_point')
            _state = _data['state']
            if _video_end_point:
                filter_params = {'cam_id': cam_id,
                                 'video_end_point': _video_end_point}
            else:
                filter_params = {'cam_id': cam_id,
                                 'annotation_end_point': _annotation_end_point}
            if _data.get("new_video_end_point"):
                update_params = {'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(_state).isdigit() else None,
                                 'video_upload_end_datetime': _video_upload_end_datetime,
                                 'video_end_point': _data.get("new_video_end_point")}

            else:
                update_params = {'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(
                    _state).isdigit() else None,
                                 'video_upload_end_datetime': _video_upload_end_datetime}

            sql = '''update t_media set {} where {}'''.format(
                ','.join(['{}={}'.format(key, update_params[key] if not isinstance(update_params[key], str) else "'" + update_params[key] + "'") for key in update_params]),
                ' and '.join(['{}={}'.format(key, filter_params[key] if not isinstance(filter_params[key], str) else "'" + filter_params[key] + "'") for key in filter_params]))

            connect.loginfo('updating the upload endtime in table t_media')
            connect.update_database(sql=sql)
            connect.loginfo('updated')
            # async_data_process.update(table=Media, update_params=update_params, filter_params=filter_params)
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "Video upload to BLOB completed for event {}".format(event), "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            print(task_result)
            connect.loginfo('storage update background process endedfor upload end event  ended')
            return task_result
        elif event == 'automatic':
            connect.loginfo("automatic  event started ")
            _cam_id = _data["cam_id"]
            cam_id = _data["camera_id"]
            _video_upload_start_datetime = _data['video_upload_end_datetime']
            _video_upload_end_datetime = _data['video_upload_end_datetime']
            _video_end_point = _data['video_end_point']
            _video_upload_source = _data["video_upload_source"]
            _video_upload_source_id = _data['video_upload_source_id']
            _state = _data['state']
            insert_params = {'cam_id': cam_id,
                             'video_upload_start_datetime': _video_upload_start_datetime,
                             'video_upload_end_datetime': _video_upload_start_datetime,
                             'video_end_point': _video_end_point,
                             'video_upload_source': _video_upload_source,
                             'video_upload_source_id': _video_upload_source_id,
                             'state_id': int(master_data_obj.state_mapper.get(_state)) if master_data_obj.state_mapper.get(
                                 _state).isdigit() else None}
            sql = '''insert into t_media ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                    ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))
            connect.loginfo('inserting into t_media table the uploading details')
            connect.update_database(sql=sql)
            connect.loginfo('inserted')

            # async_data_process.insert(table=Media, insert_params=insert_params)
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "Video upload to BLOB completed for event {}".format(event), "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            print(task_result)
            connect.loginfo('storage update background process automatic event end')
            return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in storage_update_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception while updating video upload status at {} and event is {}".format(str(exc_tb.tb_lineno), str(_data)), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def event_update_background(_event_data):
    connect.loginfo('event update background started')
    start = time.time()
    start_datetime = datetime.now()
    userid = _event_data.get('userid')
    try:
        _event = _event_data['event']
        insert_update_params = {}
        filter_params = {}
        if 'iot_event_id' in _event_data:
            connect.loginfo('event started for having iot event id  ')
            _iot_event_id = _event_data.get('iot_event_id')
            filter_params['iot_event_id'] = _iot_event_id
            if _event == "json_event":
                connect.loginfo("iot event id is there , it is   a json event started ")
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
                    connect.loginfo("iot event id is there , it is   a json event ended")
            elif _event == "image_event":
                connect.loginfo("iot  event id is there , it is a image event started ")
                _image_end_point = _event_data.get('image_end_point')
                if _image_end_point is not None:
                    insert_update_params['image_end_point'] = _image_end_point
                connect.loginfo("iot event id is there , it is   a image event ended")

            sql = '''update t_event set {} where {}'''.format(
                ','.join(['{}={}'.format(key, insert_update_params[key] if not isinstance(insert_update_params[key], str) else "'" + insert_update_params[key] + "'") for key in insert_update_params]),
                ' and '.join(['{}={}'.format(key, filter_params[key] if not isinstance(filter_params[key], str) else "'" + filter_params[key] + "'") for key in filter_params]))

            connect.loginfo("in image  event having iot event id also,  updating the t_event table ")
            rows_updated = connect.update_database(sql=sql)
            connect.loginfo("updated")

            if rows_updated == 0:
                sql = '''insert into t_event ({}) values ({})'''.format(','.join([str(key) for key in insert_update_params.keys()]),
                                                                        ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_update_params.values()]))
                connect.loginfo("in image  event having iot event id also,  inserting in  the t_event table ")
                connect.update_database(sql=sql)
                connect.loginfo("inserted ")
                end = time.time()
                end_datetime = datetime.now()
                task_result = {"user_id": str(userid), "name": " Image event added", "status": "Success", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
                task_result = json.dumps(task_result)
                print(task_result)
                connect.loginfo("iot event id is there , that event , task ended ")
                return task_result
            # async_data_process.insert_update(table=Event, insert_update_params=insert_update_params, filter_params=filter_params)
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": " Image event updated", "status": "Success", "time_taken": str(end - start), "start_datetime": str(start_datetime),
                           "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            print(task_result)
            connect.loginfo(" iot event id is there , that event , task ended ")

            return task_result

        else:
            if _event == "image_event":
                connect.loginfo("iot event id is not there , it is a image event started")
                _cam_name = _event_data.get('cam_name')
                _event_start_datetime = _event_data.get('event_start_datetime')
                _event_name = _event_data.get('event_name')
                _image_end_point = _event_data.get('image_end_point')
                insert_params = {"camera_id": int(master_data_obj.camera_mapper.get(str(_cam_name))),
                                 "image_end_point": _image_end_point,
                                 "start_datetime": _event_start_datetime,
                                 "type_id": int(master_data_obj.event_mapper.get(str(_event_name)))}
                sql = '''insert into t_event ({}) values ({})'''.format(','.join(insert_params.keys()),
                                                                        ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))
                connect.loginfo("iot event id is not there , it is a image event , inserting details in t_event")
                connect.update_database(sql=sql)
                connect.loginfo("inserted ")
                # async_data_process.insert(table=Event, insert_params=insert_params)
                end = time.time()
                end_datetime = datetime.now()
                task_result = {"user_id": str(userid), "name": " Image event updated at {}".format(_image_end_point), "status": "Success",
                               "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
                task_result = json.dumps(task_result)
                print(task_result)
                connect.loginfo("iot event id is not there , it is a image event , ended")
                return task_result

    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in event_update_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception while updating event at {} and event is {}".format(str(exc_tb.tb_lineno), str(_event_data)), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def extract_background(filter_params, update_params, _durations, media_status_id, video_end_point, _data):
    connect.loginfo("Extraction process started")
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    try:
        _durations_ids = []
        media_data = async_data_process.select(table=Media, filter_params={'id': filter_params['id']}, get_first_row=True)
        video_filename = media_data.video_filename
        connect.loginfo("updating the t_media table started")
        async_data_process.update(Media, update_params=update_params, filter_params=filter_params)
        connect.loginfo("updating the t_media table ended")
        for duration in _durations:

            insert_params = {'media_status_id': int(media_status_id),
                             'start_time': duration['start'],
                             'end_time': duration['end'],
                             'image_count': duration['images_count'],
                             'remark': duration['remarks'],
                             'extraction_status': 'extraction_pending'}
            connect.loginfo("insertion in t_media_duration table started for duration:{}-{}".format(duration['start'], duration['end']))
            sql = '''insert into t_media_durations ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                              ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))

            id = connect.update_database_and_return_id(sql=sql)
            # id = async_data_process.insert(MediaDuration, insert_params=insert_params)
            connect.loginfo("insertion in t_media_duration table ended for duration:{}-{}".format(duration['start'], duration['end']))

            _durations_ids.append(id)
            connect.loginfo("classes-{}".format(str(duration['classes'])))
            for class_ in duration['classes']:
                if class_ is None:
                    connect.loginfo("class_ is none")
                else:
                    connect.loginfo("class-{} type is {}, id is {}".format(class_, type(class_), master_data_obj.class_mapper.get(str(class_))))

                insert_params = {'media_duration_id': int(id),
                                 'tag_id': int(master_data_obj.class_mapper.get(class_)) if master_data_obj.class_mapper.get(
                                     class_).isdigit() else master_data_obj.class_mapper.get(class_)}
                sql = '''insert into media_tags_mapping ({}) values ({})'''.format(','.join([str(key) for key in insert_params.keys()]),
                                                                                   ','.join([str(value) if not isinstance(value, str) else "'" + value + "'" for value in insert_params.values()]))
                connect.loginfo("insertion in media_tags_mapping table  started for class {}".format(class_))

                connect.update_database(sql=sql)
                connect.loginfo("insertion in media_tags_mapping table  ended for class {}".format(class_))

                # async_data_process.insert(MediaTagMap, insert_params=insert_params)

        connect.loginfo("extracting images for video is started")

        extract_images.extract_images(video_end_point, _durations, _durations_ids, int(media_status_id))
        connect.loginfo("extracting images for video is ended")
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": str(userid), "name": "Image extraction completed for video - {}".format(video_filename), "status": "Success",
                       "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        print(task_result)
        connect.loginfo("Extraction process ended successfully")
        return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in extract_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception while extracting images at {}".format(str(exc_tb.tb_lineno)), "status": "Failed",
                       "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def upload_file_end_event_background(upload_end_event_data):
    userid = upload_end_event_data.get('userid')
    start = time.time()
    start_datetime = datetime.now()
    try:
        connect.loginfo("Celery accessed")
        connect.loginfo("upload file end event background started ")

        start = time.time()
        start_datetime = datetime.now()
        video_filename = upload_end_event_data.get('video_filename')
        userid = upload_end_event_data.get('userid')
        input_file = upload_end_event_data['local_video_location']
        if input_file is not None:
            if os.path.splitext(input_file)[1] not in (".ogg", ".ogv", ".webm", ".wmv", ".mkv"):
                connect.loginfo("video conversion started to .mkv")
                output_file = upload_end_event_data['local_video_location'].replace(os.path.splitext(input_file)[1], ".mkv")
                # subprocess.run(['ffmpeg', '-i', input_file, output_file])
                converter_ = Converter()
                info = converter_.probe(input_file)
                if info.streams[0].codec.lower() == 'mpeg4':
                    connect.loginfo("codec is mpeg4, converting to h264")
                    conv = converter_.convert(input_file, output_file, {'format': 'mkv',
                                                                        'video': {'codec': 'h264',
                                                                                  'width': info.streams[0].video_width,
                                                                                  'height': info.streams[0].video_height,
                                                                                  'fps': info.streams[0].video_fps}})

                else:
                    connect.loginfo("codec is other than mpeg4")
                    conv = converter_.convert(input_file, output_file, {'format': 'mkv',
                                                                        'video': {'codec': info.streams[0].codec,
                                                                                  'width': info.streams[0].video_width,
                                                                                  'height': info.streams[0].video_height,
                                                                                  'fps': info.streams[0].video_fps}})
                percent_completed = 0
                for time_code in conv:
                    percent_completed_new = int(time_code * 100)
                    if percent_completed != percent_completed_new:
                        percent_completed = percent_completed_new
                        status = json.dumps({"result": json.dumps({"name": upload_end_event_data['media_end_point'], "progress": percent_completed}), "publisher": "alert"})
                        connect.loginfo("publishing the conversion details", 'debug')
                        connect.publish(status, routing_key=constants.celery_rabbitmq_publisher["routing_key"].format(userid, upload_end_event_data['media_end_point']))
                if percent_completed != 100:
                    status = json.dumps({"result": json.dumps({"name": upload_end_event_data['media_end_point'], "progress": 100}), "publisher": "alert"})
                    connect.loginfo("publishing the conversion details", 'debug')
                    connect.publish(status)
                connect.loginfo("conversion ended")
                os.remove(input_file)
                connect.loginfo("removing the file before conversion, ie  other than ogg, ogv, webm, .wmv, mkv")

            else:
                connect.loginfo("no need to convert to mkv")
                output_file = input_file

            connect.loginfo("uploading the video to blob ")
            async_data_process.upload(file_to_upload=output_file, _upload_location=upload_end_event_data['media_end_point'].replace(os.path.splitext(upload_end_event_data['media_end_point'])[1], ".mkv"))
            connect.loginfo("uploaded")

            upload_end_event = {"cam_id": upload_end_event_data['_cam_id'],
                                "camera_id": upload_end_event_data['cam_id'],
                                "video_upload_end_datetime": upload_end_event_data['date_of_upload'],
                                "video_end_point": upload_end_event_data['media_end_point'] ,
                                "new_video_end_point": upload_end_event_data['media_end_point'].replace(os.path.splitext(upload_end_event_data['media_end_point'])[1], ".mkv") if os.path.splitext(input_file)[1] not in (".ogg", ".ogv", ".webm", ".wmv", ".mkv") else upload_end_event_data['media_end_point'],
                                "event": "upload_end_event",
                                "state": upload_end_event_data.get('state')}
        else:
            upload_end_event = {"cam_id": upload_end_event_data['_cam_id'],
                                "camera_id": upload_end_event_data['cam_id'],
                                "video_upload_end_datetime": upload_end_event_data['date_of_upload'],
                                "video_end_point": None,
                                "new_video_end_point": None,
                                "annotation_end_point": upload_end_event_data.get('annotation_end_point'),
                                "event": "upload_end_event",
                                "state": upload_end_event_data.get('state'),
                                "userid":userid}

        connect.loginfo("calling storage update background task")
        storage_update_background(upload_end_event)
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": str(userid), "name": "{} video file uploaded ".format(video_filename), "status": "Success",
                       "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        print(task_result)
        connect.loginfo("upload end event ended")
        return task_result

    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in upload_file_end_event_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception while updating upload event at {} and event is {}".format(str(exc_tb.tb_lineno), str(upload_end_event_data)), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result



@app.task
def submit_annotation_background(data):
    connect.loginfo("submit annotation  background started")
    start = time.time()
    start_datetime = datetime.now()
    userid = data.get('userid')
    try:
        _data = data.get("_via_img_metadata").copy()
        negative_images = data.get('negative_images')
        for image_link in negative_images:
            image_name = image_link.split('/')[-1].split('.')[0]
            for key in _data:
                if image_name == key.split('.')[0]:
                    del data.get('_via_img_metadata')[key]
                    data.get('_via_image_id_list').remove(key)
        del data['negative_images']
        connect.loginfo('data = {}'.format(data))
        data = data.get("_via_img_metadata")
        if len(data) > 0:
            classes = {}
            class_length = 0
            local_zip_location = os.path.join(connect.config_json.get('static_path'), '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2]))
            connect.loginfo("local zip location = {}".format(local_zip_location))

            local_zip_end_point = os.path.join(connect.config_json.get('static_path'),
                                               '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2]) + ".zip")
            connect.loginfo("local zip end point= {}".format(local_zip_end_point))

            blob_zip_location = '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2])
            connect.loginfo("blob zip location= {}".format(blob_zip_location))

            blob_zip_end_point = '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2]) + ".zip"
            connect.loginfo("blob zip endpoint = {}".format(blob_zip_end_point))
            blob_image_end_point = '/'.join(list(data.values())[0]["image_link"].split("static/")[1].split('/')[:-2]) + '.zip'
            connect.loginfo("blob image endpoint = {}".format(blob_image_end_point))

            for key, value in data.items():
                txt_file_name = data[key]["filename"]
                connect.loginfo("text file name= {}".format(txt_file_name), 'debug')
                media_duration_id = data[key]["image_link"].split("/")[-2]
                connect.loginfo("media duration id= {}".format(media_duration_id), 'debug')
                annotation_file = os.path.join(connect.config_json.get('static_path'), data[key]["image_link"].split("static/")[1].replace("image", "annotation").replace(".jpg", ".txt"))
                connect.loginfo("annotation file= {}".format(annotation_file), 'debug')

                try:
                    x_res = float(txt_file_name.split("_")[-2])
                    y_res = float((txt_file_name.split("_")[-1]).split(".")[0])
                except Exception as e:
                    connect.loginfo("%s", str(e))
                    continue
                info = data[key]["regions"]
                for info_id in info:
                    connect.loginfo("the directory where annotation file is there is exists= {}".format(os.path.exists(os.path.split(annotation_file)[0])))
                    if not os.path.exists(os.path.split(annotation_file)[0]):
                        connect.loginfo("creating the directory= {}".format(os.path.split(annotation_file)[0]))
                        os.makedirs(os.path.split(annotation_file)[0])
                    connect.loginfo("started creating and appending the file")
                    with open(annotation_file, "a+") as txt_file:
                        coords = info_id["shape_attributes"]
                        if coords["name"] != 'rect':
                            continue
                        # print(coords,data[key]["regions"])
                        x_txt = float(coords["x"])
                        y_txt = float(coords["y"])
                        h_txt = float(coords["height"])
                        w_txt = float(coords["width"])
                        # print (x_res,y_res, x_txt,y_txt,w_txt,h_txt)
                        y_txt = float(y_txt / y_res) + float(float(h_txt / y_res) / 2)
                        h_txt = float(h_txt / y_res)
                        x_txt = float(x_txt / x_res) + float(float(w_txt / x_res) / 2)
                        w_txt = float(w_txt / x_res)
                        label = info_id["region_attributes"]
                        class_txt = label["Class"]
                        if media_duration_id in classes:
                            if class_txt not in classes[media_duration_id].keys():
                                class_directory = '/'.join(annotation_file.split('/')[:-1])
                                classes[media_duration_id][class_txt] = str(len(classes[media_duration_id]) - 1)
                                classes[media_duration_id]['class_directory'] = class_directory
                        else:
                            class_directory = '/'.join(annotation_file.split('/')[:-1])
                            classes[media_duration_id] = {class_txt: str(class_length), 'class_directory': class_directory}
                        txt_sting = classes[media_duration_id][class_txt] + " " + str(x_txt) + " " + str(y_txt) + " " + str(w_txt) + " " + str(h_txt) + "\n"
                        txt_file.write(txt_sting)
                        txt_file.close()
                    # print(label,x_res,y_res,x_txt,y_txt,w_txt,h_txt)
            for media_duration_id in classes:
                connect.loginfo("started creating and writing on classes.txt for media duration id ={}".format(media_duration_id), 'debug')
                with open(classes[media_duration_id]['class_directory'] + "/classes.txt", 'w') as cls_file:
                    for cl in classes[media_duration_id].keys():
                        if cl != 'class_directory':
                            cls_file.write(str(cl) + "\n")
                    cls_file.close()
            connect.loginfo("zipping the directory = {}".format(local_zip_location))
            zip_file = extract_images.zip(local_zip_location)
            connect.loginfo("zipped")
            connect.loginfo("started uploading the file from  = {} to ={}".format(zip_file, blob_zip_end_point))
            async_data_process.upload(file_to_upload=zip_file, _upload_location=blob_zip_end_point)
            connect.loginfo("updating the table t_media setting annotation end point")
            sql = "update t_media set annotation_end_point = '{}', state_id = 6 where image_end_point = '{}'".format(blob_zip_end_point, blob_image_end_point)
            connect.loginfo("updating the table t_media setting annotation end point")
            connect.update_database(sql=sql)
            connect.loginfo("updated")
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "Annotation submitted at {}".format(blob_zip_end_point), "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            connect.loginfo("submit annotation task ended")
            return task_result

        else:
            connect.loginfo("nothing to submit in annotation")
            end_datetime = datetime.now()
            end = time.time()
            task_result = {"user_id": str(userid), "name": "Nothing to submit", "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            connect.loginfo("submit annotation task ended, nothiing submitted")

            return task_result

    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in submit annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception while submitting annotation at {} and event is {}".format(str(exc_tb.tb_lineno), data), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def save_annotation_background(_data):
    connect.loginfo("save annotation background started")
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    try:
        data = _data.get("_via_img_metadata").copy()
        negative_images = _data.get('negative_images')
        for image_link in negative_images:
            image_name = image_link.split('/')[-1].split('.')[0]
            for key in data:
                if image_name == key.split('.')[0]:
                    del _data.get('_via_img_metadata')[key]
                    _data.get('_via_image_id_list').remove(key)
        del _data['negative_images']
        connect.loginfo('data = {}'.format(_data))
        data = _data.get("_via_img_metadata")
        if len(data) > 0:
            classes = {}
            class_length = 0
            local_zip_location = os.path.join(connect.config_json.get('static_path'), '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2]))
            connect.loginfo("local zip location = {}".format(local_zip_location))
            local_zip_end_point = os.path.join(connect.config_json.get('static_path'),
                                               '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2]) + ".json")
            connect.loginfo("local zip endpoint = {}".format(local_zip_end_point))
            blob_zip_location = '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2])
            connect.loginfo("blob zip location = {}".format(blob_zip_location))

            blob_zip_end_point = '/'.join(list(data.values())[0]["image_link"].split("static/")[1].replace("image", "annotation").split("/")[:-2]) + ".json"
            connect.loginfo("blob zip endpoint = {}".format(blob_zip_end_point))
            blob_image_end_point = '/'.join(list(data.values())[0]["image_link"].split("static/")[1].split('/')[:-2]) + '.zip'
            connect.loginfo("blob image endpoint= {}".format(blob_image_end_point))
            connect.loginfo("the location where blob zip file exists  = {}".format(os.path.exists(os.path.split(local_zip_location)[0])))
            if not os.path.exists(os.path.split(local_zip_location)[0]):
                connect.loginfo('creating the directory = {}'.format(os.path.split(local_zip_location)[0]))
                os.makedirs(os.path.split(local_zip_location)[0])
            connect.loginfo("creating and writing on file blob zip end point = {}".format(blob_zip_end_point))
            with open(local_zip_end_point, "w+") as json_file:
                json.dump(_data, json_file)

            connect.loginfo('removing the blob zip end point from blob ={}'.format(blob_zip_end_point))
            async_data_process.remove_blob(_remove_location=blob_zip_end_point)
            connect.loginfo("removed")
            connect.loginfo('uploading the file from = {} to  ={}'.format(local_zip_end_point, blob_zip_end_point))

            async_data_process.upload(file_to_upload=local_zip_end_point, _upload_location=blob_zip_end_point)
            connect.loginfo('uploaded')

            sql = "update t_media set partial_save_end_point = '{}', state_id = 5 where image_end_point = '{}'".format(blob_zip_end_point, blob_image_end_point)
            connect.loginfo('updating the t_media table')
            connect.update_database(sql=sql)
            connect.loginfo('updated')
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "Annotation saved at {}".format(blob_zip_end_point), "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            connect.loginfo('save annotation task ended')
            return task_result
        else:
            connect.loginfo('save annotation task started, nothing to save ')
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "Nothing to save", "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            connect.loginfo('save annotation task ended nothing to save ')
            return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception while saving annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()

        task_result = {"user_id": userid, "name": "Exception while saving annotation at {} and event is {}".format(str(exc_tb.tb_lineno), str(_data)), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def video_feed_background(_data):
    connect.loginfo("Data in video_feed_background " + str(_data))
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    # ip = _data.get('ip')
    camera_name = _data.get('camera_name')
    try:
        connect.loginfo('calling the Videostream class')
        video_stream = VideoStream(connect.config_json, camera_name, connect)
        connect.loginfo('checking if client is there')
        if video_stream.hpcl_client:
            connect.loginfo('client is there')
            try:
                connect.loginfo('close the connection')
                video_stream.hpcl_client.close()
                connect.loginfo('closed')
            except Exception as e_:
                pass
            connect.loginfo('setting hpclclient to none')
            video_stream.hpcl_client = None
        connect.loginfo('creating a new hpcl client connection')
        video_stream.hpcl_client = video_stream.initiate_socket()
        connect.loginfo('connection created')
        connect.loginfo('sending the data')
        video_stream.hpcl_client.send(video_stream.camera_name.encode())
        connect.loginfo('sent')
        connect.loginfo('recieving the data')
        message = video_stream.hpcl_client.recv(5 * 1024 * 1024)
        connect.loginfo('recieved')
        connect.loginfo('checking if ok is there in message')
        if b'ok' in message:
            connect.loginfo('ok is theere, calling the gen frames function')
            frame = video_stream.gen_frames()
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": userid, "name": "Socket connection created ", "status": "success", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            connect.loginfo("{}".format(str(task_result)))
            connect.loginfo('sending response')
            return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            task_result = {"user_id": userid, "name": "ok is not there in message ", "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in video_feed_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception in video_feed_background at line no {}".format(str(exc_tb.tb_lineno)), "status": "Failed", "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def re_annotate_background(_data):
    connect.loginfo("Re annotation started")
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    _via_settings = {
        "ui": {
            "annotation_editor_height": "25",
            "leftsidebar_width": "18",
            "annotation_editor_fontsize": "0.8",
            "image_grid": {
                "img_height": "80",
                "rshape_fill": "none",
                "rshape_fill_opacity": "0.3",
                "show_image_policy": "all",
                "show_region_shape": "true",
                "rshape_stroke_width": "2",
                "rshape_stroke": "yellow"
            },
            "image": {
                "region_label": "__via_region_id__",
                "region_color": "__via_default_region_color__",
                "region_label_font": "10px Sans",
                "on_image_annotation_editor_placement": "NEAR_REGION"
            }
        },
        "core": {
            "buffer_size": "18",
            "filepath": {},
            "default_filepath": ""
        },
        "project": {
            "name": "18"
        }
    }

    _via_attributes = {
                          "file": {},
                          "region": {
                              "Class": {
                                  "default_value": "",
                                  "description": "",
                                  "type": "dropdown"
                              }
                          }
                      },
    try:
        media_id = _data.get('media_id')
        connect.loginfo("media_id - {}".format(str(media_id)))
        filter_params = {'id': media_id}
        media = async_data_process.select(Media, filter_params, get_first_row=True)
        connect.loginfo("media.annotation_end_point - {}".format(str(media.annotation_end_point)))
        connect.loginfo("media.partial_save_end_point - {}".format(str(media.partial_save_end_point)))
        connect.loginfo("media.image_end_point - {}".format(str(media.image_end_point)))
        if media.annotation_end_point is not None:
            local_annotation_zip_path = os.path.join(connect.config_json.get('static_path'), media.annotation_end_point)
            local_image_zip_path = os.path.join(connect.config_json.get('static_path'), media.image_end_point)
            connect.loginfo("local annotated zip path - {} exists - {}".format(str(local_annotation_zip_path), os.path.exists(local_annotation_zip_path)))
            connect.loginfo("local image zip path - {} exists - {}".format(str(local_image_zip_path), os.path.exists(local_image_zip_path)))
            local_annotation_unzip_path = os.path.join(connect.config_json.get('static_path'), media.annotation_end_point).split('.')[0]
            local_image_unzip_path = os.path.join(connect.config_json.get('static_path'), media.image_end_point).split('.')[0]
            connect.loginfo("local annotation unzip path - {} exists - {}".format(str(local_annotation_unzip_path), os.path.exists(local_annotation_unzip_path)))
            connect.loginfo("local image unzip path - {} exists - {}".format(str(local_image_unzip_path), os.path.exists(local_image_unzip_path)))
            if not os.path.exists(local_annotation_unzip_path):
                if not os.path.exists(local_annotation_zip_path):
                    connect.loginfo("downloading the zip file from {} to {}".format(media.annotation_end_point, local_annotation_zip_path))
                    async_data_process.download(media.annotation_end_point, local_annotation_zip_path)
                    connect.loginfo("downloaded")
                    connect.loginfo("extracting the zip file")
                    ExtractImages.unzip(local_annotation_zip_path)
                else:
                    connect.loginfo("zip file is there in server already extracting the zip file {}".format(local_annotation_zip_path))
                    ExtractImages.unzip(local_annotation_zip_path)
            connect.loginfo("local annotation unzip  path - {} exists - {}".format(str(local_annotation_unzip_path), os.path.exists(local_annotation_unzip_path)))

            if not os.path.exists(local_image_unzip_path):
                if not os.path.exists(local_image_zip_path):
                    connect.loginfo("downloading the zip file from {} to {}".format(media.image_end_point, local_image_zip_path))
                    async_data_process.download(media.image_end_point, local_image_zip_path)
                    connect.loginfo("downloaded")
                    connect.loginfo("extracting the zip file")
                    ExtractImages.unzip(local_image_zip_path)
                else:
                    connect.loginfo("zip file is there in server already extracting the zip file {}".format(local_image_zip_path))
                    ExtractImages.unzip(local_image_zip_path)
            connect.loginfo("local image unzip  path - {} exists - {}".format(str(local_image_unzip_path), os.path.exists(local_image_unzip_path)))

            sample_json = {"_via_settings": _via_settings, "_via_img_metadata": {}, "_via_attributes": _via_attributes, "_via_data_format_version": "2.0.10", "_via_image_id_list": [], 'userid': str(userid)}
            local_json_path = str(local_annotation_unzip_path) + ".json"
            connect.loginfo("the local json path - {}".format(local_json_path))
            l1 = sorted(os.listdir(local_annotation_unzip_path))
            connect.loginfo("sorting the directories in local annotation unzip  path - {}".format(local_annotation_unzip_path))
            connect.loginfo("directories in local_annotation_unzip_path - {} are {}".format(local_annotation_unzip_path, str(l1)))

            l2 = sorted(os.listdir(local_image_unzip_path))
            connect.loginfo("sorting the directories in local image unzip  path - {}".format(local_image_unzip_path))
            connect.loginfo("directories in local_image_unzip_path - {} are {}".format(local_image_unzip_path, str(l2)))

            for duration_id in l2:
                connect.loginfo("directory - {}".format(str(duration_id)))
                duration_id_image_path = os.path.join(str(local_image_unzip_path), str(duration_id))
                duration_id_annotation_path = os.path.join(str(local_annotation_unzip_path), str(duration_id))
                connect.loginfo("checking if the same duration id folder exists in both")
                connect.loginfo("duration_id_image_path -{} exists - {}".format(duration_id_image_path, os.path.exists(duration_id_image_path)))
                connect.loginfo("duration_id_annotation_path -{} exists - {}".format(duration_id_annotation_path, os.path.exists(duration_id_annotation_path)))
                if os.path.exists(duration_id_annotation_path) and os.path.exists(duration_id_image_path):
                    connect.loginfo("exists in both")
                    classes_text_file = "classes.txt"
                    class_text_file_path = os.path.join(duration_id_annotation_path, classes_text_file)
                    category = []
                    connect.loginfo("creating classes.txt file")
                    connect.loginfo("writing the classes from -{} , classes  are - {}".format(class_text_file_path, category))
                    with open(class_text_file_path, "r") as data:
                        category = (data.read().strip()).split("\n")
                    connect.loginfo("created")
                    connect.loginfo("files in the {} are {}".format(duration_id_annotation_path, os.listdir(duration_id_annotation_path)))
                    connect.loginfo("files in the {} are {}".format(duration_id_image_path, os.listdir(duration_id_image_path)))
                    for img_file in sorted(os.listdir(duration_id_image_path)):
                        connect.loginfo("checking if the text file for image = {} exists or not ".format(img_file))
                        if img_file.replace("jpg", "txt") in sorted(os.listdir(duration_id_annotation_path)):
                            text_file = img_file.replace("jpg", "txt")
                            connect.loginfo("txt file = {} exists for image = {}".format(text_file, img_file))
                            text_file_path = os.path.join(duration_id_annotation_path, text_file)  # joining the text file name and the directory
                            connect.loginfo("text file path is -{}".format(text_file_path))
                            text_to_image_file_path = ((str(text_file_path).replace("annotation", "image")).replace('_annotation', '_images')).split(".")[0] + ".jpg"
                            connect.loginfo("text to image file path - {}".format(text_to_image_file_path))
                            text_to_image_file = str(text_file_path).split("/")[-1].replace(".txt", ".jpg")  # name of image file
                            connect.loginfo("text to image file - {}".format(text_to_image_file))
                            x_res = float(text_to_image_file.split("_")[-2])
                            y_res = float((text_to_image_file.split("_")[-1]).split(".")[0])
                            size = str(int(x_res * y_res))
                            connect.loginfo("the sizes are x_res -{}, y_res-{}, size-{}".format(str(x_res), str(y_res), size))
                            with open(text_file_path, "r") as data:
                                data_lists = (data.read().strip()).split("\n")
                            sample_json["_via_img_metadata"][text_to_image_file + size] = {"file_attributes": {}, "filename": text_to_image_file,
                                                                                           "image_link": connect.config_json.get('static_url') + text_to_image_file_path.split("/static/")[1],
                                                                                           "regions": [],
                                                                                           "size": size}
                            sample_json["_via_image_id_list"].append(text_to_image_file + size)
                            connect.loginfo("text_to_image_file -{} size - {}".format(text_to_image_file, size))
                            connect.loginfo("data_lists - {}".format(data_lists))
                            connect.loginfo("classes - {}".format(str(category)))
                            cat_dict = {v: k for v, k in enumerate(category)}
                            connect.loginfo("classes dict - {}".format(str(cat_dict)))
                            for data_list in data_lists:
                                data_list_item = (data_list.strip()).split(' ')
                                connect.loginfo("data_list_items - {}".format(str(data_list_item)))
                                h_txt = int(float(data_list_item[4]) * y_res)
                                y_txt = int(float(float(data_list_item[2]) - float(float(h_txt / y_res) / 2)) * y_res)
                                w_txt = int(float(data_list_item[3]) * x_res)
                                x_txt = int(float(float(data_list_item[1]) - float(float(w_txt / x_res) / 2)) * x_res)
                                connect.loginfo(cat_dict, cat_dict[int(data_list_item[0])])
                                sample_json["_via_img_metadata"][text_to_image_file + size]["regions"].append(
                                    {"shape_attributes": {"name": "rect", "x": str(x_txt), "y": str(y_txt), "width": str(w_txt), "height": str(h_txt)},
                                     "region_attributes": {"Class": cat_dict[int(data_list_item[0])]}})

                        else:
                            connect.loginfo("txt file = {} not exists for image = {}".format(img_file.replace("jpg", "txt"), img_file))
                            text_to_image_file = img_file
                            connect.loginfo("text to image file - {}".format(text_to_image_file))
                            text_to_image_file_path = os.path.join(duration_id_image_path, img_file)
                            connect.loginfo("text to image file path - {}".format(text_to_image_file_path))
                            size = os.path.getsize(text_to_image_file_path)
                            connect.loginfo("the size is  size-{}".format(size))
                            sample_json["_via_img_metadata"][text_to_image_file + str(size)] = {"file_attributes": {}, "filename": text_to_image_file,
                                                                                                "image_link": connect.config_json.get('static_url') + text_to_image_file_path.split("/static/")[1],
                                                                                                "regions": [],
                                                                                                "size": size}
                            sample_json["_via_image_id_list"].append(text_to_image_file + str(size))

                elif not os.path.exists(duration_id_annotation_path) and os.path.exists(duration_id_image_path):
                    connect.loginfo("exists in image path ")
                    for img_file in sorted(os.listdir(duration_id_image_path)):
                        connect.loginfo("txt file = {} not exists for image = {}".format(img_file.replace("jpg", "txt"), img_file))
                        text_to_image_file = img_file
                        connect.loginfo("text to image file - {}".format(text_to_image_file))
                        text_to_image_file_path = os.path.join(duration_id_image_path, img_file)
                        connect.loginfo("text to image file path - {}".format(text_to_image_file_path))
                        size = os.path.getsize(text_to_image_file_path)
                        connect.loginfo("the size is  size-{}".format(size))
                        sample_json["_via_img_metadata"][text_to_image_file + str(size)] = {"file_attributes": {}, "filename": text_to_image_file,
                                                                                            "image_link": connect.config_json.get('static_url') + text_to_image_file_path.split("/static/")[1],
                                                                                            "regions": [],
                                                                                            "size": size}
                        sample_json["_via_image_id_list"].append(text_to_image_file + str(size))
                else:
                    connect.loginfo("not exists in both")

            connect.loginfo("creating the json file")
            with open(local_json_path, "w") as json_data:
                write_json = json.dumps(sample_json, indent=4)
                json_data.write(write_json)

            connect.loginfo("created the file")
            blob_upload_path = media.partial_save_end_point
            connect.loginfo("removing the partial save annotation  point  - {}".format(media.partial_save_end_point))

            async_data_process.remove_blob(media.partial_save_end_point)
            connect.loginfo("removed")
            connect.loginfo("removing the annotation end point - {} ".format(media.annotation_end_point))

            async_data_process.remove_blob(media.annotation_end_point)
            connect.loginfo("removed")

            connect.loginfo("local image path - {} exists - {}".format(str(local_annotation_unzip_path), os.path.exists(local_annotation_unzip_path)))
            shutil.rmtree(local_annotation_unzip_path)
            connect.loginfo("local image path - {} exists - {}".format(str(local_annotation_unzip_path), os.path.exists(local_annotation_unzip_path)))
            connect.loginfo("removed from server - {}".format(str(local_annotation_unzip_path)))

            connect.loginfo("local zip path - {} exists - {}".format(str(local_annotation_zip_path), os.path.exists(local_annotation_zip_path)))
            os.remove(local_annotation_zip_path)
            connect.loginfo("local zip path - {} exists - {}".format(str(local_annotation_zip_path), os.path.exists(local_annotation_zip_path)))
            connect.loginfo("removed from server - {}".format(str(local_annotation_zip_path)))

            connect.loginfo("uploading th json file -{}  to  -{}".format(local_json_path, blob_upload_path))
            async_data_process.upload(local_json_path, blob_upload_path)

            connect.loginfo("blob uploaded")

            partial_path = str(local_json_path).split("static")[1][1:]
            connect.loginfo("partial path - {} and partial save end point previously - {} ".format(str(partial_path), str(blob_upload_path)))
            update_filter_params = {'partial_save_end_point': partial_path, 'annotation_end_point': None}
            async_data_process.insert_update(table=Media, insert_update_params=update_filter_params,
                                             filter_params=filter_params)
            connect.loginfo("database updated")
            end = time.time()
            end_datetime = datetime.now()
            task_result = {"user_id": str(userid), "name": "re annotation done ", "status": "Success",
                           "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
            task_result = json.dumps(task_result)
            connect.loginfo("re annotation done ")
            return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in re annotate " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception in re annotate at line no {}".format(str(exc_tb.tb_lineno)), "status": "Failed", "time_taken": str(end - start),
                       "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


@app.task
def test1_background(_data):
    try:
        connect.loginfo("Accessing test 1")
        start = time.time()
        start_datetime = datetime.now()
        userid = _data.get('userid')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": str(userid), "name": "Task completed", "status": "Success",
                       "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in test1_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')



@app.task
def submit_remarks_background(_data):
    connect.loginfo("submit remarks  started")
    start = time.time()
    start_datetime = datetime.now()
    userid = _data.get('userid')
    try:
        remarks_json = _data.get('remarks')
        camera_id = _data.get("camera_id")
        connect.loginfo("remarks = {}".format(str(remarks_json)), 'debug')
        # for remark in remarks_json['remarks']:
        for remark in remarks_json:
            year, month, day, hour, minute_15 = remark.split('_')
            sql = "update t_image_remarks set remarks= '{remarks}' where year = {year} and month = {month} and day = {day} and hour = {hour} and minute_15 = {minute_15} and camera_id = {camera_id}".format(remarks=json.dumps(remarks_json[remark]),
                                                                                                                                                                                   year=str(year),
                                                                                                                                                                                   month=str(month),
                                                                                                                                                                                   day=str(day),
                                                                                                                                                                                   hour=str(hour),
                                                                                                                                                                                   minute_15=str(minute_15),
                                                                                                                                                                                   camera_id=str(camera_id))
            connect.update_database(sql=sql)
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": str(userid), "name": "images marked  done ", "status": "Success",
                       "time_taken": str(end - start), "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        connect.loginfo("images marked done ")
        return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in submit remarks " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        end = time.time()
        end_datetime = datetime.now()
        task_result = {"user_id": userid, "name": "Exception in submit remarks at line no {}".format(str(exc_tb.tb_lineno)), "status": "Failed", "time_taken": str(end - start),
                       "start_datetime": str(start_datetime), "end_datetime": str(end_datetime)}
        task_result = json.dumps(task_result)
        return task_result


app.conf.update(result_expires=3600, result_persistent=True, task_ignore_result=False)
if __name__ == '__main__':
    app.start()
