import shutil
import zipfile
from base64 import b64encode

from flask import Response, url_for, jsonify, request, session, render_template, redirect, Flask
from python_resumable import UploaderFlask
from kombu import Connection
from flask_cors import cross_origin
from collections import defaultdict
from datetime import datetime, timedelta
from functools import reduce
from flask_cors import CORS
from time import sleep
import requests
import hashlib
import time
import copy
import sys
import cv2
import os
import numpy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app_modules import VideoStreamConsumer,Entities, Rule, Model, event_data, VideoStream, Camera_Feature, Feature, Event, UserProfile, AccessViews, Department, Designation, RolePermissions, UserSession, db_connection, engine, master_rule, RedisData, master_data, master_data_obj, Session_db, Media, Classes, MediaDuration, MediaTagMap, async_data_process, ExtractImages, _build_auth_code_flow, InitializeApp, os, sys, msal, app_config, json, MasterData, UserProfile, EventLogs, extract_images, cv2, Camera, ModelType, FeatureRoi, Areas, Remarks, FeedRemarks, Locations, cards_data, latest_events_data
from api_authentication.user_auth import login_required, user_login_auth, user_logout_auth, secure_password,user_login_auth_new
from api_connectivity.utility import Utility
from configuration import constants

app, redis_, login_manager = InitializeApp.initialize_app()
CORS(app, support_credentials=True, resources={r"*": constants.api_v2_cors_config})
connect = Utility(configuration=constants.flask_utility_configuration, rabbitmq_publisher=constants.rabbitmq_publisher)
ip = connect.config_json.get("ip")
hq_ip = connect.config_json.get("hq_ip")
hq_connect = None
video_stream = {}
if ip != hq_ip:
    constants.hq_rabbitmq_publisher['routing_key'] = "edge_status.#"
    constants.hq_rabbitmq_publisher['rabbitmq_host'] = hq_ip
    hq_connect = Utility(configuration=constants.hq_flask_utility_configuration, rabbitmq_publisher=constants.hq_rabbitmq_publisher)
else:
    constants.hq_rabbitmq_publisher['routing_key'] = "hq_status.#"

connect.loginfo("ip = {}".format(connect.config_json.get("ip")), 'debug')
connect.loginfo("hq_ip = {}".format(connect.config_json.get("hq_ip")), 'debug')
connect.loginfo(" hostname fastapi = {}".format(connect.config_json.get('host_name_fastapi')), 'debug')
connect.loginfo("static path = {}".format(connect.config_json.get('static_path')), 'debug')
connect.loginfo("static url = {}".format(connect.config_json.get("static_url")), 'debug')
connect.loginfo("container name model = {}".format(connect.config_json.get("container_name_model")), 'debug')
connect.loginfo(" model location = {}".format(connect.config_json.get("model_location")), 'debug')
connect.loginfo("entity = {}".format(connect.config_json.get("entity")), 'debug')
connect.loginfo("location = {}".format(connect.config_json.get("location")), 'debug')
connect.loginfo("entity-location = {}".format(str(connect.config_json.get("entity-location"))), 'debug')
connect.loginfo("status = {}".format(str(connect.config_json.get('status'))), 'debug')

redis_data = RedisData(connect)


@app.route('/api/test')
@cross_origin(supports_credentials=True)
def test():
    return Response({'Working'})


@app.route('/api/test1')
@cross_origin(supports_credentials=True)
def test1():
    _data = {'userid': "1"}
    requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/test1", json=_data)
    return Response({'Working'})


@app.route("/api/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)


@app.route("/api/login")
@cross_origin(supports_credentials=True)
def login():
    session["flow"] = _build_auth_code_flow(authority=app_config.AUTHORITY, scopes=app_config.SCOPE)
    session["flow"]["auth_uri"] = session["flow"]["auth_uri"].replace('response_type=code', 'response_type=token')
    return jsonify(url=session["flow"]["auth_uri"], version=msal.__version__, session=session["flow"])


@app.route("/api/ad_login", methods=['POST'])
@cross_origin(supports_credentials=True)
def ad_login():
    connect.loginfo('1. AD login api is called', level='info')
    try:
        data = request.json
        connect.loginfo('2. Json data {} received'.format(data), level='info')
        user_email = data.get('mail')
        connect.loginfo("3. Fetch user data from user profile", level='info')
        user = async_data_process.select(table=UserProfile, filter_params={'email': user_email}, get_first_row=True, get_distinct_rows=False, retry_count=1)
        connect.loginfo('4. checking if user exists or not', level='info')
        if user is None:
            connect.loginfo('   4.1. Roles and permission  does not exists for this new user', level='info')
            insert_params = {"full_name": request.json.get('displayName'),
                             "email": request.json.get('mail'),
                             "login_name": request.json.get('givenName'),
                             'user_login_type': 'ad'}
            connect.loginfo('   4.2. Inserting the user data {} into m_user_profile table'.format(insert_params), level='info')
            async_data_process.insert(table=UserProfile, insert_params=insert_params)
            connect.loginfo('   4.3. The new user data is saved, but role is not assigned', level='info')
            response = {"message": "Contact the administrator for assigning roles to your Id"}
            return response
        else:
            connect.loginfo('   4.1. User verified ,checking if role is assigned to user or not ', level='info')
            if user.role_id is None:
                connect.loginfo('   4.2. Role id is None', level='info')
                response = {"message": "Contact the administrator for assigning roles to your Id"}
                return response
            else:
                connect.loginfo('   4.2. User has a role id {}'.format(user.role_id), level='info')
                connect.loginfo("   4.3. Fetching the role and permission for this user", level='info')
                permission = async_data_process.select(table=RolePermissions, filter_params={'id': user.role_id}, get_first_row=True)
                connect.loginfo("   4.4. Fetching the master data", level='info')
                master_entity_location = master_data.get("entity_product_cam")
                entity_location = {}
                for entity in master_entity_location:
                    if entity not in entity_location:
                        entity_location[entity] = {'locations': []}
                    entity_location[entity]['locations'] = list(master_entity_location[entity]['locations'].keys())
                if user.entity_id is None:
                    user_entities = entity_location
                else:
                    if user.location_id is None:
                        user_entities = {
                            str(master_data_obj.mapper.get('entity_mapper').get(str(user.entity_id))): {'locations': entity_location[str(master_data_obj.mapper.get('entity_mapper').get(str(user.entity_id)))]['locations']}}
                    else:
                        _entity = master_data_obj.mapper.get('entity_mapper').get(user.entity_id)
                        location = str(master_data_obj.mapper.get(_entity).get('location_mapper').get(str(user.location_id)))
                        user_entities = {str(_entity): {'locations': [location]}}
                response = {"user_id": str(user.id),
                            "full_name": str(user.full_name),
                            "employee_id": str(user.employee_id),
                            "gender": str(user.gender),
                            "mobile": str(user.mobile),
                            "email": str(user.email),
                            "login_name": str(user.login_name),
                            "user_entity_location": json.dumps(user_entities),
                            "status": str(user.status),
                            "role": permission.role_name,
                            "key": b64encode(os.urandom(16)).decode('utf-8'),
                            "permissions": permission.access_rules}
                connect.loginfo('   4.5. New user logged in successfully', level='info')
                return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. AD login exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/user_login", methods=['POST'])
@cross_origin(supports_credentials=True)
def user_login():
    """when user enter manually the username and password and tries to log in then this ap will be called """
    connect.loginfo('1. User login api is called', level='info')
    try:
        # data = request.values
        data = request.json
        response = user_login_auth(data, async_data_process, UserProfile, UserSession, master_data_obj, master_data, RolePermissions, connect)
        return jsonify(response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in user login  " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/user_login_new", methods=['POST'])
@cross_origin(supports_credentials=True)
def user_login_new():
    """when user enter manually the username and password and tries to log in then this ap will be called """
    connect.loginfo('1. user login api is called', 'info')
    try:
        data = request.json
        response = user_login_auth_new(data, async_data_process, UserProfile, UserSession, master_data_obj, master_data, RolePermissions, connect)
        if response == -1:
            return Response("Password is wrong", status=400, mimetype='application/json')
        elif response == -2:
            return Response("User Name not found", status=400, mimetype='application/json')
        else:
            return jsonify(response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in user login  " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/user_logout")
@cross_origin(supports_credentials=True)
@login_required
def user_logout():
    connect.loginfo("1. User logout api is called", level='info')
    """if user has entered manually the user name and password and tres to logout thn this api will be called"""
    try:
        user_id = request.headers.get('user-id')
        key = str(request.headers.get('key'))
        response = user_logout_auth(key, async_data_process, UserSession, user_id, connect)
        return jsonify(response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in user logout" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/token")
@cross_origin(supports_credentials=True)
def token():
    connect.loginfo('1. Token api is called', level='info')
    try:
        code = request.args.get('code')
        code_verifier = json.loads(request.args.get('code_verifier'))
        url = app_config.AUTHORITY + '/oauth2/v2.0/token'
        dictToSend = {'client_id': app_config.CLIENT_ID, 'scope': app_config.SCOPE, 'code': code,
                      'redirect_uri': connect.config_json.get('host_name_fastapi') + '/login',
                      'grant_type': 'authorization_code',
                      'code_verifier': hashlib.sha256(code_verifier.encode())}  # ,'client_secret':app_config.CLIENT_SECRET}
        res = requests.post(url, data=dictToSend)
        return res.json()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Token exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/logout")
@cross_origin(supports_credentials=True)
def logout():
    connect.loginfo('1. Logout api is called', level='info')
    session.clear()  # Wipe out user and its token cache from session
    connect.loginfo('2. user logged out and its token cache from session has been cleared', level='info')
    return redirect(app_config.AUTHORITY + "/oauth2/v2.0/logout" + "?post_logout_redirect_uri=" + url_for("index", _external=True))  # Also logout from your tenant's web session


@app.route("/api/graphcall")
@cross_origin(supports_credentials=True)
def graphcall():
    connect.loginfo('1. Graphcall api is called', level='info')
    try:
        token = request.args.get('access_token')
        connect.loginfo('2. Checking for token in headers', level='info')
        if not token:
            connect.loginfo('3. Token not received redirecting to login', level='info')
            return redirect(url_for("login"))
        connect.loginfo('3. Token received', level='info')
        graph_data = requests.get(app_config.ENDPOINT, headers={'Authorization': 'Bearer ' + token}, ).json()
        return jsonify(graph_data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Graphcall exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_videos', methods=['GET'])
@cross_origin(supports_credentials=True, **constants.api_v2_cors_config)
def fetch_videos():
    connect.loginfo('1. Fetch videos api is called', level='info')
    try:
        _data = request.values
        connect.loginfo('2. Json data received {}'.format(str(_data)), level='info')
        _cam_name = _data.get("cam_name")
        _state_name = _data.get("state_name")
        _area = _data.get("area")
        _location = _data.get("location")
        _entity = _data.get("entity")
        connect.loginfo("3. camera id = {}".format(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(_cam_name)), level='info')
        _cam_id = master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(_cam_name)
        _state_id = master_data_obj.state_mapper.get(_state_name) if _state_name else None
        _cam_id = int(_cam_id) if str(_cam_id).isdigit() else _cam_id
        _state_id = int(_state_id) if _state_id and str(_state_id).isdigit() else _state_id
        filter_params = {"cam_id": _cam_id, "state_id": _state_id}
        connect.loginfo('4. Quering database to get media having camera_name {} and state {}'.format(_cam_name, _state_name), level='info')
        entries = async_data_process.select(table=Media, filter_params=filter_params)
        response = defaultdict(list)
        for entry in entries:
            entry = dict(entry)
            entry['remarks'] = str(entry.get('remarks')) if entry.get('remarks') is not None else "No remarks"
            entry['filename'] = str(entry.get('video_filename')) if entry.get('video_filename') is not None else "No file name"
            connect.loginfo("camera name = {}".format(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(str(entry['cam_id']))), 'debug')
            entry['cam_id'] = master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(str(entry['cam_id']))
            entry['activity'] = master_data_obj.state_action_mapper.get(str(entry['state_id']))
            entry['state_id'] = master_data_obj.state_mapper.get(str(entry['state_id']))
            entry['capture_end_datetime'] = entry['capture_end_datetime'].strftime('%Y-%m-%d %H:%M:%S') if entry[
                'capture_end_datetime'] else None
            entry['capture_start_datetime'] = entry['capture_start_datetime'].strftime('%Y-%m-%d %H:%M:%S') if entry[
                'capture_start_datetime'] else None
            entry['video_upload_end_datetime'] = entry['video_upload_end_datetime'].strftime('%Y-%m-%d %H:%M:%S') if entry[
                'video_upload_end_datetime'] else None
            entry['video_upload_start_datetime'] = entry['video_upload_start_datetime'].strftime('%Y-%m-%d %H:%M:%S') if \
                entry['video_upload_start_datetime'] else None
            response['data'].append(entry)
        connect.loginfo('5. Videos fetched successfully having camera_name {} and state {}'.format(_cam_name, _state_name), level='info')
        return {"response": response, "re-extract": True if _state_id >= 4 else False}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in fetch_videos " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/mark_image_negative", methods=['POST'])
@cross_origin(supports_credentials=True)
def mark_image_negative():
    connect.loginfo(' 1. Mark image negative api is called', level='info')
    try:
        _data = request.json
        connect.loginfo(' 2. Json data recieved {}'.format(_data), level='info')
        if len(_data) > 0:
            for i in range(len(_data)):
                link = _data[i]
                path_from_link = "/".join(link.split('/')[4:-2])
                connect.loginfo(' 3. Path from the link {}'.format(path_from_link), level='info')
                zip_path_from_link = "/".join(link.split('/')[4:-2]) + '.zip'
                connect.loginfo(' 4. Zip path file from the link {}'.format(zip_path_from_link), level='info')
                local_zip_path = os.path.join(connect.config_json.get('static_path'), zip_path_from_link)
                connect.loginfo(' 5. Local zip path {}'.format(local_zip_path), level='info')
                local_unzip_location = os.path.join(connect.config_json.get('static_path'), path_from_link)
                connect.loginfo(' 6. The local unzipped location  {}'.format(local_unzip_location), level='info')
                local_zip_location_back = os.path.dirname(str(local_zip_path))
                connect.loginfo(' 7. The directory where zip file is there'.format(local_zip_location_back), level='info')
                connect.loginfo(' 8. Check path for data', level='info')

                if os.path.exists(local_unzip_location):
                    connect.loginfo('    8.1. path {} exists'.format(local_unzip_location), level='info')
                    image_path = os.path.join(connect.config_json.get('static_path'), link.split('static')[1][1:])
                    connect.loginfo('    8.2. Removing image {} '.format(image_path), level='info')
                    try:
                        os.remove(image_path)
                        connect.loginfo('    8.3. Image removed successfully', level='info')
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        connect.loginfo("#. Exception in removing image " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

                elif os.path.exists(local_zip_path):
                    connect.loginfo('    8.1. Path {} exists'.format(local_zip_path), level='info')
                    connect.loginfo('    8.2. Zip file is there {}'.format(local_zip_path), level='info')
                    extract_images.unzip(local_zip_path)
                    image_path = os.path.join(connect.config_json.get('static_path'), link.split('static')[1][1:])
                    connect.loginfo('    8.3. Removing image {} '.format(image_path), level='info')
                    try:
                        os.remove(image_path)
                        connect.loginfo('    8.3. Image removed successfully', level='info')
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        connect.loginfo("#. Exception in removing image " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

                else:
                    if not os.path.exists(local_zip_location_back):
                        connect.loginfo('    8.1. Path {} exists'.format(local_zip_location_back), level='info')
                        connect.loginfo('    8.2. Now making directories', level='info')
                        os.makedirs(local_zip_location_back)
                    connect.loginfo('    8.3. Downloading zip file', level='info')
                    async_data_process.download(zip_path_from_link, local_zip_path)
                    connect.loginfo('    8.4. Downloaded', level='info')
                    while True:
                        if zipfile.is_zipfile(local_zip_path):
                            break
                    connect.loginfo('    8.5. Zip file downloaded successfully', level='info')
                    try:
                        connect.loginfo('    8.6. Extracting zip file', level='info')
                        extract_images.unzip(local_zip_path)
                        connect.loginfo('    8.7. Zip file extracted successfully', level='info')
                    except Exception as e_:
                        connect.loginfo('#. Error while extracting zip file {}'.format(e_))
                    image_path = os.path.join(connect.config_json.get('static_path'), link.split('static')[1][1:])
                    connect.loginfo('    8.8. Removing image {} '.format(image_path), level='info')
                    try:
                        os.remove(image_path)
                        connect.loginfo('    8.9. Image removed successfully', level='info')
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        connect.loginfo("#. Exception in removing image " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')
            # removing zip folder from local
            connect.loginfo(' 9. Removing zip folder', level='info')
            if os.path.exists(local_zip_path):
                os.remove(local_zip_path)
            connect.loginfo('10. zip folder removed', level='info')
            # making new zip file from remaining images
            connect.loginfo('11. Making new zip file', level='info')
            extract_images.zip(local_unzip_location)
            # removing previous zip file form blob
            connect.loginfo('12. Removing old zip file from blob', level='info')
            async_data_process.remove_blob(zip_path_from_link)
            connect.loginfo("13. Removed successfully", level='info')
            # uploading new zip file to the blob
            connect.loginfo('14. Uploading new zip file to blob', level='info')
            async_data_process.upload(local_zip_path, zip_path_from_link)
            connect.loginfo("uploaded")
            connect.loginfo('15. New zip file uploaded successfully in blob', level='info')
            return jsonify({'message': 'images_deleted'})
        else:
            connect.loginfo('3. No images to delete ', level='info')
            return jsonify({'message': 'no images to delete'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Mark image negative exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_annotated_images', methods=['GET'])
@cross_origin(supports_credentials=True, **constants.api_v2_cors_config)
def fetch_annotated_images():
    connect.loginfo('1. Fetch annotated images  api is called', level='info')
    try:
        _data = request.values
        connect.loginfo('2. Json data {} received'.format(_data), level='info')
        _cam_name = _data.get("cam_name")
        _area = _data.get("area")
        _location = _data.get("location")
        _entity = _data.get("entity")
        _date_to_fetch = _data.get("date_to_fetch")
        _cam_id = int(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(_cam_name))
        filter_params = {"camera_id": _cam_id, "upload_date": _date_to_fetch}
        entries = async_data_process.select(table=EventLogs, filter_params=filter_params)
        response = []
        for entry in entries:
            entry = dict(entry)
            entry['camera_name'] = master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(str(entry['camera_id']))
            entry['feature_name'] = master_data_obj.mapper.get(_entity).get(_location).get('feature_mapper').get(str(entry['feature_id']))
            entry['upload_date'] = entry['upload_date'].strftime('%Y-%m-%d')
            del entry['camera_id']
            del entry['feature_id']
            response.append(entry)
        connect.loginfo()
        return {"response": response}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in fetch_annotated_images " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/classes', methods=['GET'])
@cross_origin(supports_credentials=True)
def classes():
    connect.loginfo('1. Classes  api is called', level='info')
    try:
        entity_data = json.loads(request.headers.get('entity-location'))
        for key in entity_data:
            entity = key
        entity_id = int(master_data_obj.mapper.get('entity_mapper').get(entity))
        filter_params = {'entity_id': entity_id}
        connect.loginfo('2. Fetching classes from database', level='info')
        entries = async_data_process.select(table=Classes, filter_params=filter_params, get_distinct_rows={"columns": ['name']})
        connect.loginfo('3. Classes fetched successful', level='info')
        return jsonify([x.name for x in entries])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in classes " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/video_preview', methods=['GET'])
def review():
    connect.loginfo('1. Review  api is called', level='info')
    try:
        _data = request.values
        connect.loginfo('2. Json data {} received'.format(_data), level='info')
        _media_id = _data.get('media_id')
        filter_params = {'id': int(_media_id)}
        connect.loginfo('3. Querying database using filter {}'.format(filter_params), level='info')
        media_obj = async_data_process.select(table=Media, filter_params=filter_params)
        connect.loginfo('4. Querying database using filter {} successful'.format(filter_params), level='info')
        _media = dict(media_obj[0])
        response = {'url': app.config.get('static_url') + _media.get('video_end_point', ''), 'upload_remarks': _media.get('remarks', '')}
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in review " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/video_feed')
@cross_origin(supports_credentials=True)
def video_feed():
    connect.loginfo('1. Video feed  api is called', level='info')
    camera_name = request.args.get('camera_name')
    connect.loginfo("2. Entry " + camera_name, level='info')
    filter_params = {'name': camera_name}
    connect.loginfo('3. Querying database using filter {}'.format(filter_params), level='info')
    obj = async_data_process.select(table=Camera, filter_params=filter_params, get_first_row=True)
    connect.loginfo('4. Querying database using filter {} successful'.format(filter_params), level='info')
    _data = {'userid': request.headers.get('user-id'),
             'ip': obj.ip,
             'camera_name': obj.name}
    userid = _data.get('userid')
    camera_name = _data.get('camera_name')
    try:
        connect.loginfo('5. Trying to make a socket connection', level='info')
        video_stream = VideoStream(connect.config_json, camera_name, connect)
        connect.loginfo('6. Checking if client connection exists already', level='info')
        if video_stream.hpcl_client:
            connect.loginfo('   6.1. Vlient connection exists', level='info')
            try:
                connect.loginfo('   6.2. Closing the client connection', level='info')
                video_stream.hpcl_client.close()
                connect.loginfo('   6.3. Client connection closed', level='info')
            except Exception as e_:
                connect.loginfo('#. Exception:{}'.format(e_), level='error')
                pass
            video_stream.hpcl_client = None
        connect.loginfo('7. Initiating new socket connection', level='info')
        video_stream.hpcl_client = video_stream.initiate_socket()
        connect.loginfo('8. New socket connection established', level='info')
        video_stream.hpcl_client.send(video_stream.camera_name.encode())
        message = video_stream.hpcl_client.recv(5 * 1024 * 1024)
        if b'ok' in message:
            # frame = video_stream.gen_frames()
            connect.loginfo('9. Getting frames from camera {}'.format(camera_name), level='info')
            return Response(video_stream.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            connect.loginfo('9. Failed to create socket connection', level='info')
            task_result = {"user_id": userid, "name": "Failed to create socket connection", "status": "Failed"}
            task_result = json.dumps(task_result)
            return task_result
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in video_feed_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/video_feed0', methods=['POST', 'GET', 'DELETE'])
@cross_origin(supports_credentials=True)
def video_feed0():
    try:
        global video_stream
        if request.method != 'DELETE':
            # for key in connect.master_redis.scan_iter("video_feed_*"):
            #     connect.loginfo(str(key) + ' : ' + str(connect.master_redis.get_val(key=key)))
            #     connect.master_redis.set_val(key=key, val='close')
            connect.loginfo('1. Video feed  api is called', level='info')
            camera_name = request.args.get('camera_name')
            feature = request.args.get('feature')
            unique_name = request.args.get('unique_name')
            _area = request.headers.get('area')
            _location = request.headers.get('location')
            _entity = request.headers.get('entity')
            if not _location:
                entity_location = json.loads(request.args.get('entity_location'))
                _entity = list(entity_location.keys())[0]
                _location = entity_location[_entity]['locations'][0]
            video_stream[camera_name] = VideoStreamConsumer(camera_name, Utility, connect, unique_name, _entity, _location, feature=feature)
            video_stream[camera_name].connect = video_stream[camera_name].initiate_socket()
            connect.loginfo('2. Getting frames from camera {}'.format(camera_name), level='info')
            return Response(video_stream[camera_name].gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            camera_name = request.args.get('camera_name')
            unique_name = request.args.get('unique_name')
            connect.master_redis.set_val(key='video_feed_{}_{}'.format(camera_name, unique_name), val='close')
            return Response('message connection closed')
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in video_feed_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/add_camera_roi", methods=['POST'])
@cross_origin(supports_credentials=True)
def add_camera_roi():
    connect.loginfo('1. Add amera roi  api is called', level='info')
    try:
        roi = []
        data = request.json
        cam_name = request.args.get('name')
        _via_img_metadata = data.get('_via_img_metadata')
        for key, val in _via_img_metadata.items():
            for i in _via_img_metadata[key].get('regions'):
                shape_attributes = i.get('shape_attributes')
                x = str(shape_attributes.get('x'))
                y = str(shape_attributes.get('y'))
                width = str(shape_attributes.get('width'))
                height = str(shape_attributes.get('height'))
                roi_list = x + ',' + y + ',' + width + ',' + height
                roi.append(roi_list)

        insert_update_params = {'roi1': roi[0], 'roi2': roi[1], 'roi3': roi[2], 'roi4': roi[3], 'roi5': roi[4]}
        filter_params = {'name': cam_name}
        connect.loginfo("2. Updating_inserting the details in camera table", level='info')
        async_data_process.insert_update(table=Camera, insert_update_params=insert_update_params, filter_params=filter_params)
        connect.loginfo("3. updated_inserted successfully", level='info')
        return jsonify({'message': 'roi added successfully'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Add camera roi exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/fetch_camera", methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_camera():
    connect.loginfo('1. Fetch camera   api is called', level='info')
    master_data = master_data_obj.master_data_(Session_db)
    # connect.loginfo('fetch camera   api is called ' + str(master_data))
    try:
        response = {}
        connect.loginfo('2. checking headers', level='info')
        entity_data = request.headers.get('entity_location')
        entity_data_dict = master_data_obj.get_entity_location(entity_data)
        connect.loginfo("3. calling the master data", level='info')
        # m_data = master_data_obj.master_data_(Session_db)
        entity_cam = master_data['entity_product_id']
        cam_name = request.args.get('name')
        if cam_name is not None:
            connect.loginfo('fetching camera details of camera {}'.format(cam_name), level='info')
            for k, v in entity_data_dict.items():
                for location in v['locations']:
                    for key, val in entity_cam[k]['locations'][location].items():
                        if cam_name in val:
                            filter_params = {'id': cam_name}
                            connect.loginfo("using join select unction of async data process", level='debug')
                            join_obj = async_data_process.join_select(
                                tables=[[Camera, Camera_Feature], [Camera_Feature, Feature]],
                                join_params=[{1: ['id', 'camera_id']}, {1: ['feature_id', 'id']},
                                             {1: ['tag_id', 'id']}],
                                add_column_params=[{1: ['status', 'alert']}, {1: ['name']}],
                                table_names=[['camera', 'camera_feature'], ['camera_feature', 'feature']],
                                filter_params=[{0: filter_params}], join='left')
                            for obj in join_obj:
                                if obj.Camera.is_deleted != 1:
                                    feature_dict = {
                                        "feature_name": obj.feature_name,
                                        "status": obj.camera_feature_status,
                                        "alert": obj.camera_feature_alert
                                    }
                                    camera_data = master_data_obj.camera_id_mapper[str(obj.Camera.id)]
                                    a_id = camera_data.get('area_id')
                                    connect.loginfo("area name = {}".format(camera_data.get('area_name'), 'debug'))
                                    area_name = camera_data.get('area_name')
                                    # filter_params = {'id': a_id}
                                    # area_obj = async_data_process.select(table=Areas, filter_params=filter_params, get_first_row=True)
                                    location_id = camera_data.get('location_id')
                                    location = camera_data.get('location_name')
                                    if obj.Camera.name in response:
                                        response[obj.Camera.name]['feature'].append(feature_dict)
                                    else:
                                        image_size = 0
                                        image_name = None
                                        if obj.Camera.base_image_end_point:
                                            local_base_image_location = os.path.join(connect.config_json.get("static_path"), obj.Camera.base_image_end_point)
                                            connect.loginfo("local base image location = {}".format(local_base_image_location), 'debug')
                                            if not os.path.isfile(local_base_image_location):
                                                if not os.path.exists(os.path.split(local_base_image_location)[0]):
                                                    os.makedirs(os.path.split(local_base_image_location)[0])
                                                connect.loginfo("downloading the file")
                                                async_data_process.download(file_to_download=obj.Camera.base_image_end_point, download_location=local_base_image_location, container_name=connect.config_json.get("container_name_model"))
                                                connect.loginfo("downloaded")

                                            image = cv2.imread(local_base_image_location)
                                            if not isinstance(image, type(None)):
                                                image_size = image.shape[1] * image.shape[0]
                                                image_name = os.path.split(obj.Camera.base_image_end_point)[1]
                                            else:
                                                obj.Camera.base_image_end_point = None
                                        else:
                                            image_size = 0
                                            image_name = None
                                        response[obj.Camera.name] = {
                                            "id": obj.Camera.id,
                                            "camera_name": obj.Camera.name,
                                            'user_name': obj.Camera.user_name,
                                            'password': obj.Camera.password,
                                            'ip': obj.Camera.ip,
                                            'area_name': area_name,
                                            'resolution': obj.Camera.resolution,
                                            'location': location,
                                            'rtsp_link': obj.Camera.rtsp_link,
                                            "status": obj.Camera.status,
                                            "owner": obj.Camera.owner,
                                            "specification": obj.Camera.specifications,
                                            "base_image_end_point": {"image_link": os.path.join(connect.config_json.get("base_image_header"), obj.Camera.base_image_end_point) if obj.Camera.base_image_end_point else obj.Camera.base_image_end_point,
                                                                     "name": image_name,
                                                                     "size": image_size},
                                            "frame_rate": obj.Camera.frame_rate,
                                            "max_height": obj.Camera.max_height,
                                            "max_width": obj.Camera.max_width,
                                            "health": obj.Camera.health,
                                            "last_active": obj.Camera.last_active,
                                            "feature": [feature_dict]}
                                    connect.loginfo("image link = {}".format(response[obj.Camera.name]['base_image_end_point']['image_link']), 'debug')
                                    connect.loginfo('camera details fetched successfully')
                            break
                    else:
                        connect.loginfo('no camera found')
                        response = {'message': 'no camera found'}

        else:
            connect.loginfo('   3.1. Fetching all camera details', level='info')
            camera_ids = []
            for k, v in entity_data_dict.items():
                for location in v['locations']:
                    for key, val in entity_cam[k]['locations'][location].items():
                        for cam_id in val:
                            camera_ids.append(cam_id)
            filter_params = {'id': camera_ids}
            connect.loginfo('   3.2. Querying database using filter , using join select  function of async data process{}'.format(filter_params), level='info')
            join_obj = async_data_process.join_select(
                tables=[[Camera, Camera_Feature], [Camera_Feature, Feature]],
                join_params=[{1: ['id', 'camera_id']}, {1: ['feature_id', 'id']},
                             {1: ['tag_id', 'id']}],
                add_column_params=[{1: ['status', 'alert']}, {1: ['name']}],
                table_names=[['camera', 'camera_feature'], ['camera_feature', 'feature']],
                filter_params=[{0: filter_params}], join='left')
            connect.loginfo('   3.3. Database query successful suing filter {}'.format(join_obj), level='info')
            for obj in join_obj:
                if obj.Camera.is_deleted != 1:
                    feature_dict = {"feature_name": obj.feature_name,
                                    "status": obj.camera_feature_status,
                                    "alert": obj.camera_feature_alert}
                    camera_data = master_data_obj.camera_id_mapper[str(obj.Camera.id)]
                    area_name = camera_data.get('area_name')
                    location = camera_data.get('location_name')
                    if obj.Camera.name in response:
                        response[obj.Camera.name]['feature'].append(feature_dict)
                    else:
                        image_size = 0
                        image_name = None
                        if obj.Camera.base_image_end_point:
                            local_base_image_location = os.path.join(connect.config_json.get("static_path"), obj.Camera.base_image_end_point)
                            connect.loginfo("        3.3.1. Local base image location = {}".format(local_base_image_location), level='info')
                            if not os.path.isfile(local_base_image_location):
                                if not os.path.exists(os.path.split(local_base_image_location)[0]):
                                    os.makedirs(os.path.split(local_base_image_location)[0])
                                connect.loginfo("        3.3.2. Downloading the file", level='info')
                                async_data_process.download(file_to_download=obj.Camera.base_image_end_point, download_location=local_base_image_location, container_name=connect.config_json.get("container_name_model"))
                                connect.loginfo("        3.3.3. Downloaded", level='info')
                            image = cv2.imread(local_base_image_location)
                            if not isinstance(image, type(None)):
                                image_size = image.shape[1] * image.shape[0]
                                image_name = os.path.split(obj.Camera.base_image_end_point)[1]
                            else:
                                obj.Camera.base_image_end_point = None
                        else:
                            image_size = 0
                            image_name = None
                        response[obj.Camera.name] = {"id": obj.Camera.id,
                                                     "camera_name": obj.Camera.name,
                                                     'user_name': obj.Camera.user_name,
                                                     'password': obj.Camera.password,
                                                     'ip': obj.Camera.ip,
                                                     'area_name': area_name,
                                                     'resolution': obj.Camera.resolution,
                                                     'location': location,
                                                     'rtsp_link': obj.Camera.rtsp_link,
                                                     "status": obj.Camera.status,
                                                     "owner": obj.Camera.owner,
                                                     "specification": obj.Camera.specifications,
                                                     "base_image_end_point": {"image_link": os.path.join(connect.config_json.get("base_image_header"),obj.Camera.base_image_end_point) if obj.Camera.base_image_end_point else obj.Camera.base_image_end_point,
                                                                              "name": image_name,
                                                                              "size": image_size},
                                                     "frame_rate": obj.Camera.frame_rate,
                                                     "max_height": obj.Camera.max_height,
                                                     "max_width": obj.Camera.max_width,
                                                     "health": obj.Camera.health,
                                                     "last_active": obj.Camera.last_active,
                                                     "feature": [feature_dict]}
                        connect.loginfo("image link = {}".format(response[obj.Camera.name]['base_image_end_point']['image_link']), 'debug')
            connect.loginfo('   3.4. camera details fetched successfully', level='info')
        return {"data": list(response.values())[::-1]}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Fetch camera exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/add_camera", methods=['POST'])
@cross_origin(supports_credentials=True)
def add_camera_details():
    connect.loginfo('1. Add camera_details  api is called', level='info')
    try:
        data = request.json
        connect.loginfo('2. Data received {}'.format(data), level='info')
        name = data.get('name')
        filter_params = {'name': name}
        obj = async_data_process.select(Camera, filter_params=filter_params)
        if not obj:
            connect.loginfo('3. Inserting camera details into Camera table', level='info')
            insert_params = {'name': data.get('name'),
                             'user_name': data.get('user_name'),
                             'password': data.get('password'),
                             'ip': data.get('ip'),
                             'rtsp_link': data.get('rtsp_link'),
                             'resolution': data.get('resolution'),
                             'specifications': data.get('specification')}
            entity_location = json.loads(request.headers.get('entity-location'))
            _entity = list(entity_location.keys())[0]
            _location = entity_location[_entity]['locations'][0]
            insert_params["area_id"] = int(
                master_data_obj.mapper.get(_entity).get(_location).get('area_mapper').get(data.get("area_name")))
            connect.loginfo("4. Inserting_updating the camera table", level='info')
            async_data_process.insert_update(table=Camera, insert_update_params=insert_params,
                                             filter_params=filter_params)
            connect.loginfo('5. Camera added successfully', level='info')
            connect.loginfo("6. Fetching from master data", level='info')
            master_data = master_data_obj.master_data_(Session_db)
            response = 'successful!!!'
            return jsonify(response)
        else:
            connect.loginfo('2. Camera name already present,use different camera name', level='info')
            return Response("Use different camera name", status=400, mimetype='application/json')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Add camera details exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/change_camera_configuration", methods=['POST', 'DELETE'])
@cross_origin(supports_credentials=True)
def get_camera_configuration():
    connect.loginfo('1. Change_camera_configuration  api is called', level='info')
    if request.method == 'POST':
        try:
            data = request.json
            filter_params = {'id': data.get('id')}
            area_name = data.get('area_name')
            entity_location = json.loads(request.headers.get('entity-location'))
            _entity = list(entity_location.keys())[0]
            _location = entity_location[_entity]['locations'][0]
            area_id = int(master_data_obj.mapper.get(_entity).get(_location).get('area_mapper').get(area_name))
            update_params = {'name': data.get('name'),
                             'user_name': data.get('user_name'),
                             'ip': data.get('ip'),
                             'rtsp_link': data.get('rtsp_link'),
                             'resolution': data.get('resolution'),
                             'area_id': area_id,
                             'specifications': data.get('specification')}
            async_data_process.update(table=Camera, update_params=update_params, filter_params=filter_params)
            master_data = master_data_obj.master_data_(Session_db)
            return jsonify({'message': 'successful updated'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            connect.loginfo("#. Change_camera_configuration exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

    elif request.method == 'DELETE':
        try:
            id = request.args.get('id')
            filter_params = {'id': id}
            update_params = {'is_deleted': 1}
            async_data_process.update(table=Camera, filter_params=filter_params, update_params=update_params)
            return jsonify({'message': 'successfully deleted'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            connect.loginfo("delete_camera_configuration exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/fetch_tags_and_models", methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_tags():
    connect.loginfo('1. Fetch tags  api is called', level='info')
    try:
        tag_name = []
        models_name = {}
        id = request.args.get('media_id')
        connect.loginfo('2. Querying Media,MediaDuration,MediaTagMap,Classes tables in database, using join select function', level='info')
        tags = async_data_process.join_select(tables=[[Media, MediaDuration], [MediaDuration, MediaTagMap], [MediaTagMap, Classes]],
                                              join_params=[{1: ['id', 'media_status_id']}, {1: ['id', 'media_duration_id']}, {1: ['tag_id', 'id']}],
                                              add_column_params=[{1: ['image_count']}, {}, {1: ['name']}],
                                              table_names=[['media', 'media_duration'], ['media_duration', 'media_tag_mapping'], ['media_tag_mapping', 'tags']],
                                              filter_params=[{0: {'id': id}}])
        connect.loginfo('3. Database querying successful', level='info')
        for tag in tags:
            tag_name.append(tag.tags_name)
        tag_list = list(dict.fromkeys(tag_name))
        connect.loginfo('4. Querying database table ModelType ', level='info')
        data_obj = async_data_process.select(table=ModelType)
        connect.loginfo('5. Database querying successful', level='info')
        for data in data_obj:
            models_name[data.name] = data.conv_end_point
        connect.loginfo('6. Tags and models fetched successfully', level='info')
        return jsonify({'tags': tag_list,
                        'models': models_name})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Fetch tags exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/update_camera', methods=['POST'])
@cross_origin(supports_credentials=True)
def update_camera():
    connect.loginfo('1. Update camera  api is called', level='info')
    try:
        connect.loginfo('checking json data')
        data = request.json
        connect.loginfo('2. Json data {} received'.format(data), level='info')
        connect.loginfo('3. Updating camera details started', level='info')
        async_data_process.update(table=Camera, update_params={"health": str(data.get("health")), "last_active": str(data.get("last_active")), "last_checked": str(data.get("last_checked"))},
                                  filter_params={"name": str(data.get("camera_name"))}, retry_count=0)
        connect.loginfo('4. Camera details successfully updated', level='info')
        response = data
        response['api_end_point'] = 'update_camera'
        if 'sync' not in data:
            if hq_connect:
                hq_connect.publish(event=json.dumps(response))
            else:
                sql = '''select area_id from m_camera where name = '{}' '''.format(data.get("camera_name"))
                rows, no_of_rows = connect.query_database(sql=sql)
                if no_of_rows > 0:
                    area_id = rows[0][0]
                    sql = '''select location_id from m_area where id = '{}' '''.format(area_id)
                    rows, no_of_rows = connect.query_database(sql=sql)
                    if no_of_rows > 0:
                        location_id = rows[0][0]
                        sql = '''select ip from m_edge where location_id = '{}' '''.format(location_id)
                        rows, no_of_rows = connect.query_database(sql=sql)
                        if no_of_rows > 0:
                            ip = rows[0][0]
                            constants.hq_rabbitmq_publisher["rabbitmq_host"] = ip
                            edge_connect = Utility(configuration=constants.hq_flask_utility_configuration, rabbitmq_publisher=constants.hq_rabbitmq_publisher)
                            edge_connect.publish(event=json.dumps(response))
        response = 'successfully updated'
        return jsonify(response)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in updating camera details" + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in updating camera details " + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route('/api/camera_base_image', methods=['POST'])
@cross_origin(supports_credentials=True)
def camera_base_image():
    connect.loginfo('1. Camera base image  api is called', level='info')
    try:
        _data = request.json
        connect.loginfo('2. Json data {} received'.format(_data), level='info')
        camera_name = _data.get('camera_name')
        if camera_name:
            connect.loginfo('3. Camera name: {} present'.format(camera_name), level='info')
            response = {"camera_name": camera_name,
                        "camera_base_image": ""}
        else:
            response = {"camera_base_image": ""}
        connect.loginfo('4. Publishing data to fetch base image', level='info')
        connect.publish(event=json.dumps(response), routing_key="camera.status.#")
        connect.loginfo('5. Data published successfully to fetch base image', level='info')
        return jsonify({"message": "Published data to fetch base image"})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route('/api/camera_status', methods=['POST'])
@cross_origin(supports_credentials=True)
def camera_status():
    connect.loginfo('1. camera status  api is called', level='info')
    try:
        _data = request.json
        connect.loginfo('2. Json data {} received'.format(_data), level='info')
        camera_name = _data.get('camera_name')
        camera_status = int(_data.get('status'))
        response = {"camera_name": camera_name,
                    "status": camera_status,
                    "api_end_point": 'camera_status'}
        filter_params = {"name": camera_name}
        update_params = {"status": camera_status}
        connect.loginfo('3. Updating Camera table started', level='info')
        async_data_process.update(table=Camera, filter_params=filter_params, update_params=update_params)
        connect.loginfo('4. Updating Camera table successful', level='info')
        connect.loginfo('5. Publishing data to RabbitMq', level='info')
        connect.publish(event=json.dumps(response), routing_key="status.camera.#")
        connect.loginfo('6. Publishing data to RabbitMq done', level='info')
        if 'sync' not in _data:
            if hq_connect:
                hq_connect.publish(event=json.dumps(response))
            else:
                sql = '''select area_id from m_camera where name = '{}' '''.format(camera_name)
                connect.loginfo('   6.1. Database querying with command {}'.format(sql), level='info')
                rows, no_of_rows = connect.query_database(sql=sql)
                if no_of_rows > 0:
                    area_id = rows[0][0]
                    sql = '''select location_id from m_area where id = '{}' '''.format(area_id)
                    rows, no_of_rows = connect.query_database(sql=sql)
                    if no_of_rows > 0:
                        location_id = rows[0][0]
                        sql = '''select ip from m_edge where location_id = '{}' '''.format(location_id)
                        rows, no_of_rows = connect.query_database(sql=sql)
                        if no_of_rows > 0:
                            ip = rows[0][0]
                            constants.hq_rabbitmq_publisher["rabbitmq_host"] = ip
                            edge_connect = Utility(configuration=constants.hq_flask_utility_configuration, rabbitmq_publisher=constants.hq_rabbitmq_publisher)
                            edge_connect.publish(event=json.dumps(response))
        connect.loginfo('7. Published data to change status successfully', level='info')
        return jsonify({"message": "Published data to change status"})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in camera_status " + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route('/api/usecase_status', methods=['POST'])
@cross_origin(supports_credentials=True)
def usecase_status():
    connect.loginfo('1. Use case status  api is called', level='info')
    try:
        _data = request.json
        connect.loginfo('2. Json data {} received'.format(_data), level='info')
        camera_name = _data.get('camera_name')
        feature_name = _data.get('feature_name')
        feature_status = int(_data.get('status'))
        response = {"camera_name": camera_name,
                    "status": feature_status,
                    "feature_name": feature_name,
                    "api_end_point": 'usecase_status'}
        camera_data = async_data_process.select(table=Camera, filter_params={"name": camera_name}, get_first_row=True)
        feature_data = async_data_process.select(table=Feature, filter_params={"name": feature_name}, get_first_row=True)
        connect.loginfo('3. Database query successful', level='info')
        filter_params = {"camera_id": camera_data.id,
                         "feature_id": feature_data.id}
        update_params = {"status": feature_status}
        connect.loginfo('4. Updating Camera_Feature table with data {}'.format(update_params), level='info')
        async_data_process.update(table=Camera_Feature, filter_params=filter_params, update_params=update_params)
        connect.loginfo('5. updating successful', level='info')
        connect.loginfo('6. publishing data', level='info')
        connect.publish(event=json.dumps(response), routing_key="status.usecase.#")
        connect.loginfo('7. data published to change status', level='info')
        if 'sync' not in _data:
            if hq_connect:
                hq_connect.publish(event=json.dumps(response))
            else:
                sql = '''select area_id from m_camera where name = '{}' '''.format(camera_name)
                rows, no_of_rows = connect.query_database(sql=sql)
                if no_of_rows > 0:
                    area_id = rows[0][0]
                    sql = '''select location_id from m_area where id = '{}' '''.format(area_id)
                    rows, no_of_rows = connect.query_database(sql=sql)
                    if no_of_rows > 0:
                        location_id = rows[0][0]
                        sql = '''select ip from m_edge where location_id = '{}' '''.format(location_id)
                        rows, no_of_rows = connect.query_database(sql=sql)
                        if no_of_rows > 0:
                            ip = rows[0][0]
                            constants.hq_rabbitmq_publisher["rabbitmq_host"] = ip
                            edge_connect = Utility(configuration=constants.hq_flask_utility_configuration, rabbitmq_publisher=constants.hq_rabbitmq_publisher)
                            edge_connect.publish(event=json.dumps(response))
        return jsonify({"message": "Published data to change status"})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in usecase_status " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in usecase_status " + str(e_) + ' ' + str(exc_tb.tb_lineno)}) \

@app.route('/api/alert_status', methods=['POST'])
@cross_origin(supports_credentials=True)
def alert_status():
    connect.loginfo('1. Alert status  api is called', level='info')
    try:
        _data = request.json
        connect.loginfo('2. Json data {} received'.format(_data), level='info')
        camera_name = _data.get('camera_name')
        feature_name = _data.get('feature_name')
        alert_status = int(_data.get('status'))
        connect.loginfo('3. Alert status is: {}'.format(alert_status), level='info')
        response = {"camera_name": camera_name,
                    "status": alert_status,
                    "feature_name": feature_name,
                    "api_end_point": 'alert_status'}
        camera_data = async_data_process.select(table=Camera, filter_params={"name": camera_name}, get_first_row=True)
        feature_data = async_data_process.select(table=Feature, filter_params={"name": feature_name}, get_first_row=True)
        filter_params = {"camera_id": camera_data.id,
                         "feature_id": feature_data.id}
        update_params = {"alert": alert_status}
        connect.loginfo('4. Updating alert_status id:{}'.format(alert_status), level='info')
        async_data_process.update(table=Camera_Feature, filter_params=filter_params, update_params=update_params)
        connect.loginfo('5. Update successful', level='info')
        connect.loginfo('6. Publishing data', level='info')
        connect.publish(event=json.dumps(response), routing_key="status.usecase.#")
        connect.loginfo('7. Data published to change status', level='info')
        if 'sync' not in _data:
            if hq_connect:
                hq_connect.publish(event=json.dumps(response))
            else:
                sql = '''select area_id from m_camera where name = '{}' '''.format(camera_name)
                rows, no_of_rows = connect.query_database(sql=sql)
                if no_of_rows > 0:
                    area_id = rows[0][0]
                    sql = '''select location_id from m_area where id = '{}' '''.format(area_id)
                    rows, no_of_rows = connect.query_database(sql=sql)
                    if no_of_rows > 0:
                        location_id = rows[0][0]
                        sql = '''select ip from m_edge where location_id = '{}' '''.format(location_id)
                        rows, no_of_rows = connect.query_database(sql=sql)
                        if no_of_rows > 0:
                            ip = rows[0][0]
                            constants.hq_rabbitmq_publisher["rabbitmq_host"] = ip
                            edge_connect = Utility(configuration=constants.hq_flask_utility_configuration, rabbitmq_publisher=constants.hq_rabbitmq_publisher)
                            edge_connect.publish(event=json.dumps(response))
        return jsonify({"message": "Published data to change status"})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in alert_status " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in alert_status " + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route('/api/fetch_cameras_details', methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_cameras_details():
    connect.loginfo(' 1. Fetch camera details  api is called', level='info')
    try:
        entity_location = request.headers.get('entity-location')
        entity_location = master_data_obj.get_entity_location(entity_location)
        connect.loginfo(' 2. Headers present:{}'.format(entity_location), level='info')
        cameras = []
        entity_save = " "
        location_save = " "
        connect.loginfo(' 3. Fetching camera details started', level='info')
        for entity, value in entity_location.items():
            entity_save = entity
            location_save = value['locations'][0]
            locations = master_data["entity_product_id"][entity]["locations"]
            for location in entity_location[entity]["locations"]:
                areas = locations[location]
                for camera_list in list(areas.values()):
                    cameras.extend(camera_list)
        connect.loginfo(' 4. Cameras list:{}'.format(cameras), level='info')
        filter_params = {"status": 1, "id": cameras}
        camera_details = async_data_process.select(table=Camera, filter_params=filter_params)
        connect.loginfo(' 5. Querying database table Camera done', level='info')
        filter_params = {"status": 1}
        connect.loginfo(' 6. Getting camera features', level='info')
        camera_feature_mapping = async_data_process.join_select(tables=[[Camera_Feature, Camera, Feature]],
                                                                join_params=[{1: ['camera_id', 'id'], 2: ['feature_id', 'id']}],
                                                                add_column_params=[{1: ['name', 'ip'], 2: ['name']}],
                                                                table_names=[['camera_feature', 'camera', 'feature']],
                                                                filter_params=[{0: {"camera_id": cameras, "status": 1}, 2: {"status": 1}}])
        camera_features = {}
        feature_group = {}
        model_id_list = []
        for entry in camera_feature_mapping:
            if entry[0].status == 1:
                if entry[0].model_id not in model_id_list:
                    model_id_list.append(entry[0].model_id)
                if entry['feature_name'] not in feature_group:
                    feature_group[entry['feature_name']] = [entry['camera_ip']]
                else:
                    feature_group[entry['feature_name']].append(entry['camera_ip'])
                if entry[0].camera_id in camera_features:
                    camera_features[entry[0].camera_id].append(entry['feature_name'])
                else:
                    camera_features[entry[0].camera_id] = [entry['feature_name']]
        connect.loginfo(' 7. Camera_features added', level='info')
        connect.loginfo(' 8. Getting model_data,subscriber_config,model_details', level='info')
        rules = async_data_process.join_select(tables=[[Rule, Camera, Feature, Model]],
                                               join_params=[{1: ['camera_id', 'id'], 2: ['feature_id', 'id'], 3: ['model_id', 'id']}],
                                               add_column_params=[{1: ['name'], 2: ['name'], 3: ['name', 'end_point', 'model_category', 'number_of_instance']}],
                                               table_names=[['rule', 'camera', 'feature', 'model']],
                                               filter_params=[{0: {"camera_id": cameras, "model_id": model_id_list}}])
        model_data, subscriber_config, model_details = {}, [], {}
        for rule in rules:
            if rule[0].camera_id in camera_features and rule.feature_name in camera_features[rule[0].camera_id]:
                if rule[0].camera_id in model_data:
                    if rule.model_model_category in model_data[rule[0].camera_id]:
                        if rule.model_name in model_data[rule[0].camera_id][rule.model_model_category]:
                            if not rule.feature_name in model_data[rule[0].camera_id][rule.model_model_category][rule.model_name]:
                                model_data[rule[0].camera_id][rule.model_model_category][rule.model_name].append(rule.feature_name)
                        else:
                            model_data[rule[0].camera_id][rule.model_model_category][rule.model_name] = [rule.feature_name]
                    else:
                        model_data[rule.camera_name][rule.model_model_category] = {rule.model_name: [rule.feature_name]}
                else:
                    model_data[rule[0].camera_id] = {rule.model_model_category: {rule.model_name: [rule.feature_name]}}
            if rule.model_name not in model_details:
                # if rule.camera_name in cameras:
                if rule.model_end_point:
                    end_points = eval(rule.model_end_point)
                else:
                    end_points = ['', '', '', '']
                model_details[rule.model_name] = {"data": os.path.join(connect.config_json.get("model_location"), end_points[0]),
                                                  "names": os.path.join(connect.config_json.get("model_location"), end_points[1]),
                                                  "cfg": os.path.join(connect.config_json.get("model_location"), end_points[3]),
                                                  "weights": os.path.join(connect.config_json.get("model_location"), end_points[2])}
                connect.loginfo("data = {}".format(model_details[rule.model_name]['data']), 'debug')
                connect.loginfo("names = {}".format(model_details[rule.model_name]['names']), 'debug')
                connect.loginfo("cfg  = {}".format(model_details[rule.model_name]['cfg']), 'debug')
                connect.loginfo("weights = {}".format(model_details[rule.model_name]['weights']), 'debug')
                subscriber_config.append((rule.model_name, rule.model_number_of_instance))
        model_data_new = {}
        for camera_ in model_data:
            if camera_ in model_data_new:
                pass
            else:
                model_data_new[camera_] = {}
            for model_category in model_data[camera_]:
                for model_ in model_data[camera_][model_category]:
                    model_data_new[camera_][model_] = model_data[camera_][model_category][model_]
        model_data = model_data_new
        connect.loginfo(' 9. Model_data,subscriber_config,model_details fetched successfully', level='info')
        response = {"camera_config": {}, "subscriber_config": subscriber_config, "model_details": model_details, "use_case_list": []}
        index = 1
        for camera_detail in camera_details:
            if camera_detail.id in camera_features:
                response["camera_config"]["camera_" + str(index)] = {}
                response["camera_config"]["camera_" + str(index)]["cam_id"] = camera_detail.name
                response["camera_config"]["camera_" + str(index)]["location"] = location_save
                response["camera_config"]["camera_" + str(index)]["area"] = master_data_obj.mapper.get(entity_save).get(location_save).get('area_mapper')[str(camera_detail.area_id)]
                # response["camera_config"]["camera_" + str(index)]["cam_ip"] = str(camera_detail.ip).replace("ext512", "home/harshit")
                response["camera_config"]["camera_" + str(index)]["cam_ip"] = str(camera_detail.ip)
                response["camera_config"]["camera_" + str(index)]["frame_rate"] = camera_detail.frame_rate
                response["camera_config"]["camera_" + str(index)]["max_height"] = camera_detail.max_height
                response["camera_config"]["camera_" + str(index)]["max_width"] = camera_detail.max_width
                response["camera_config"]["camera_" + str(index)]["base_image_end_point"] = camera_detail.base_image_end_point
                response["camera_config"]["camera_" + str(index)]["roi1"] = camera_detail.roi1
                response["camera_config"]["camera_" + str(index)]["roi2"] = camera_detail.roi2
                response["camera_config"]["camera_" + str(index)]["roi3"] = camera_detail.roi3
                response["camera_config"]["camera_" + str(index)]["roi4"] = camera_detail.roi4
                response["camera_config"]["camera_" + str(index)]["roi5"] = camera_detail.roi5
                response["camera_config"]["camera_" + str(index)]["user_name"] = camera_detail.user_name
                response["camera_config"]["camera_" + str(index)]["password"] = camera_detail.password
                response["camera_config"]["camera_" + str(index)]["rtsp_link"] = camera_detail.rtsp_link
                response["camera_config"]["camera_" + str(index)]["usecase"] = list(set(camera_features[camera_detail.id]))
                response["use_case_list"].extend(camera_features[camera_detail.id])
            if camera_detail.id in model_data:
                response["camera_config"]["camera_" + str(index)]["model"] = model_data[camera_detail.id]
            index = index + 1
        response["camera_config"]["max"] = len(response["camera_config"])
        response["use_case_list"] = list(set(response["use_case_list"]))
        response["feature_group"] = feature_group
        connect.loginfo('10. camera_details fetched successfully', level='info')
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("# Eexception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in fetch camera details " + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route("/api/get_usecase_roi", methods=['POST'])
@cross_origin(supports_credentials=True)
def get_roi_details():
    connect.loginfo('1. Get roi details  api is called', level='info')
    try:
        roi_json = {}
        data = request.json
        camera_name = request.args.get('name')
        connect.loginfo("2. Master_data_obj.camera_mapper.get(camera_name)  = {}".format(master_data_obj.camera_mapper.get(camera_name)), level='info')
        id = int(master_data_obj.camera_mapper.get(camera_name))
        _via_img_meta_data = data.get('_via_img_metadata')
        for key, val in _via_img_meta_data.items():
            start = 1
            regions = _via_img_meta_data[key].get('regions')
            for i in range(len(regions)):
                shape_attributes = regions[i].get('shape_attributes')
                x = str(shape_attributes.get('x'))
                y = str(shape_attributes.get('y'))
                width = str(shape_attributes.get('width'))
                height = str(shape_attributes.get('height'))
                roi = x + ',' + y + ',' + width + ',' + height
                roi_json['roi' + str(start)] = roi
                start += 1
        insert_update_params = {'camera_id': id, 'roi_json': roi_json}
        filter_params = {'camera_id': id}
        connect.loginfo("3. Calling the insert update function from async data process for table featureroi", level='info')
        async_data_process.insert_update(table=FeatureRoi, insert_update_params=insert_update_params, filter_params=filter_params)
        return jsonify({"messge": "successfull"})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Get roi details exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/get_annotations", methods=['GET'])
@cross_origin(supports_credentials=True)
def get_annotation_images():
    connect.loginfo('1. Get annotated images   api is called', level='info')
    try:
        if request.method == 'GET':
            response = {}
            result = []
            connect.loginfo('checking media id')
            media_id = request.args.get('media_id')
            connect.loginfo('2. Media id is {}'.format(media_id), level='info')
            filter_params = {'media_status_id': media_id}
            connect.loginfo('3. Querying database table MediaDuration table with data {}'.format(filter_params), level='info')
            duration_obj = async_data_process.select(MediaDuration, filter_params)
            connect.loginfo('4. Query successful', level='info')
            filter_params = {'id': media_id}
            connect.loginfo('5. Querying database Media table with data {}'.format(filter_params), level='info')
            media = async_data_process.select(Media, filter_params, True)
            connect.loginfo('6. Query successful', level='info')
            product_entity = MasterData.product_entity_mapper.get(str(media.cam_id))

            for duration in duration_obj:
                test_dict = defaultdict(list)
                if duration.media_end_point is not None:
                    zip_file_path = os.path.join(app.config.get('static_path'), duration.media_end_point)
                    connect.loginfo('checking image path')
                    image_path = os.path.join(app.config.get('static_path'), duration.media_end_point.split('.')[0])
                    if not os.path.exists(image_path):
                        connect.loginfo('image path does not exist')
                        connect.loginfo('making directories to image path')
                        os.makedirs(image_path)
                        os.chdir(image_path)
                        connect.loginfo('downloading zip file')
                        async_data_process.download(duration.media_end_point, os.path.split(zip_file_path)[0])
                        connect.loginfo('zip file downloaded successfully')
                        connect.loginfo('unzipping zip file')
                        ExtractImages.unzip(zip_file_path)
                        connect.loginfo('zip file unzipped successfully')
                    each_image_path, _, filenames = next(os.walk(os.path.join(image_path, str(duration.id))), (None, None, []))
                    with Session_db() as db_session:
                        class_obj = db_session.query(MediaTagMap, Classes).filter_by(media_duration_id=duration.id).join(Classes).all()
                    for x in filenames:
                        x_path = os.path.join(each_image_path, x)
                        test_dict['images'].append({'size': os.path.getsize(x_path), 'name': x, 'image_link': app.config['static_url'] + duration.media_end_point.split('.')[0] + '/' + str(duration.id) + '/' + x})
                    test_dict['classes'] = [x.Classes.name for x in class_obj]
                    test_dict['remarks'] = duration.remark
                    test_dict['id'] = duration.id
                    result.append(test_dict)
            response['result'] = result
            response['header'] = product_entity
            if media.partial_save_end_point:
                local_json_path = os.path.join(connect.config_json.get('static_path'), media.partial_save_end_point)
                connect.loginfo("local json path = {}".format(local_json_path), 'debug')
                if not os.path.isfile(local_json_path):
                    connect.loginfo('downloading json file')
                    async_data_process.download(media.partial_save_end_point, local_json_path)
                    connect.loginfo('json file downloaded successful')
                connect.loginfo('')
                with open(local_json_path) as json_file:
                    response['json'] = json.load(json_file)
            return jsonify(response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("get annotation exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/check_file', methods=['GET'])
def check_file():
    connect.loginfo('check file  api is called')
    try:
        video_directory = app.config.get('video_location_to_resume')
        filename = request.headers['file_to_upload']
        file = os.path.join(video_directory, filename)
        if os.path.exists(file):
            connect.loginfo('file path exists')
            response = jsonify({"file_upload_status": True, "size": os.path.getsize(file)})
            connect.loginfo('file is uploaded successfully')
            response.status_code = 200
            return response
        connect.loginfo('file path does not exists')
        response = jsonify({"file_upload_status": False})
        connect.loginfo('file is not uploaded ')
        response.status_code = 204
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("check file exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/file_upload_status', methods=['GET'])
def file_upload_status():
    connect.loginfo('file upload status  api is called')
    try:
        sleep(5)
        for file_to_upload in redis_data.upload_status:
            if (datetime.now() - datetime.strptime(redis_data.upload_status[file_to_upload]['last_modified_date'], '%Y-%m-%d %H:%M:%S')).total_seconds() > 60:
                redis_data.upload_status[file_to_upload]['uploading'] = 'false'
        connect.master_redis.set_val(key='upload_status', val=redis_data.upload_status)
        yield redis_data.upload_status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("file upload status exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/annotation_summary', methods=['GET'])
async def annotation_summary():
    connect.loginfo('1. annotation summary  api is called', level='info')
    try:
        camera_id = request.args.get('camera_id')
        summary = {"total_images": 0, "total_annotation" : 0, "annotation_division": {}}
        entity_location = request.headers.get('entity-location').replace("'", '"')
        if entity_location:
            entity_location = json.loads(entity_location)
            if len(entity_location) == 0:
                entity_location = master_data.get('entity_location')
        else:
            entity_location = master_data.get('entity_location')
        entity = None
        location = None
        for key, value in entity_location.items():
            entity = key
            location = value['locations'][0]
        if not camera_id:
            camera_ids = [camera_id for camera_list in list(master_data['entity_product_cam'][entity]['locations'][location].values()) for camera_id in camera_list]
            filter_params = {"camera_id": camera_ids, "state_id": 6}
        else:
            filter_params = {"camera_id": camera_id, "state_id": 6}
        connect.loginfo('2. entity = {entity} and location = {location} and camera(s) = {camera}'.format(entity=entity, location=location, camera=camera_id if camera_id else camera_ids), level='info')
        medias = async_data_process.select(Media, filter_params, True)
        for media in medias:
            media_summary = media.remarks
            if media_summary:
                try:
                    media_summary = json.loads(media_summary)
                except Exception as e_:
                    connect.loginfo("#. media summary is not json ", level='info')
                media_summary = media_summary.get('summary')
                if media_summary:
                    summary["total_images"] += media_summary["total_images"]
                    summary["total_annotation"] += media_summary["total_annotation"]
                    for tag in media_summary["annotation_division"]:
                        if tag in summary["annotation_division"]:
                            summary["annotation_division"][tag] += media_summary["annotation_division"][tag]
                        else:
                            summary["annotation_division"][tag] = media_summary["annotation_division"][tag]
        connect.loginfo('3. summary is {summary}'.format(summary=json.dumps(summary)), level='info')
        return summary
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. exception in annotation summary " + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/resumable_upload', methods=['GET'])
async def check_status():
    connect.loginfo('check status  api is called')
    try:
        connect.loginfo('checking if resumableTotalChunks are present in query params', level='debug')
        if request.args.get('resumableTotalChunks'):
            connect.loginfo('resumableTotalChunks are present in query params')
            resumable_dict = {
                'resumableIdentifier': request.args.get('resumableIdentifier'),
                'resumableFilename': request.args.get('resumableFilename'),
                'resumableTotalSize': request.args.get('resumableTotalSize'),
                'resumableTotalChunks': request.args.get('resumableTotalChunks'),
                'resumableChunkNumber': request.args.get('resumableChunkNumber')}
        else:
            connect.loginfo('resumableTotalChunks are not present in query params')
            connect.loginfo('Now getting file details from the request object')
            resumable_dict = {
                'resumableIdentifier': request.form.get('resumableIdentifier'),
                'resumableFilename': request.form.get('resumableFilename'),
                'resumableTotalSize': request.form.get('resumableTotalSize'),
                'resumableTotalChunks': request.form.get('resumableTotalChunks'),
                'resumableChunkNumber': request.form.get('resumableChunkNumber')}
        connect.loginfo("print data " + str(resumable_dict))
        resumable = UploaderFlask(resumable_dict,
                                  app.config.get('video_location_to_resume'),
                                  app.config.get('chunk_location_to_resume'),
                                  '')

        if resumable.chunk.exists() is True:
            response = jsonify({"chunkUploadStatus": True})
            response.status_code = 200
            return response

        response = jsonify({"chunkUploadStatus": False})
        response.status_code = 204
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("resumable upload get request exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/resumable_upload', methods=['POST'])
async def upload_file():
    connect.loginfo('upload file  api is called')
    try:
        entity_location = request.headers.get('entity-location').replace("'", '"')
        if entity_location:
            entity_location = json.loads(entity_location)
            if len(entity_location) == 0:
                entity_location = master_data.get('entity_location')
        else:
            entity_location = master_data.get('entity_location')
        entity = None
        location = None
        for key, value in entity_location.items():
            entity = key
            location = value['locations'][0]

        connect.loginfo("*********************************: ")
        resumable_dict = {
            'resumableIdentifier': request.form.get('resumableIdentifier'),
            'resumableFilename': request.form.get('resumableFilename'),
            'resumableTotalSize': request.form.get('resumableTotalSize'),
            'resumableTotalChunks': request.form.get('resumableTotalChunks'),
            'resumableChunkNumber': request.form.get('resumableChunkNumber')}
        try:
            cam_name = request.form.get('cam_id') if request.form.get('cam_id') else request.headers.get('cam-id')
            _area = request.form.get('area') if request.form.get('area') else request.headers.get('area')
            _location = request.form.get('location') if request.form.get('location') else request.headers.get('location')
            _entity = request.form.get('entity') if request.form.get('entity') else request.headers.get('entity')
            # redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
            connect.loginfo('checking resumable filename in redis')
            if resumable_dict['resumableFilename'] + '!' + cam_name not in redis_data.upload_status:
                if resumable_dict['resumableChunkNumber'] == '1':
                    date_of_upload = datetime.now()
                    connect.loginfo("camera id = {}".format(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name) if master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name).isdigit() else master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name)), 'debug')
                    # connect.loginfo("int(master_data_obj.camera_mapper.get(_cam_id)) if master_data_obj.camera_mapper.get(_cam_id).isdigit() else master_data_obj.camera_mapper.get(_cam_id) = {}".format(master_data_obj.camera_mapper.get(cam_name) if master_data_obj.camera_mapper.get(cam_name).isdigit() else master_data_obj.camera_mapper.get(cam_name)), 'debug')
                    connect.loginfo("master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending']) if master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending']).isdigit() else None = {}".format(master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending']) if master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending']).isdigit() else None), 'debug')
                    insert_params = {'cam_id': int(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name)) if master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name).isdigit() else master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name),
                                     'video_upload_start_datetime': date_of_upload.strftime('%Y-%m-%d %H:%M:%S'),
                                     'video_end_point': os.path.join(entity, location, 'video', '{}/{}/{}/{}/{}{}'.format(cam_name, date_of_upload.year, date_of_upload.month, date_of_upload.day, str(int(date_of_upload.timestamp() * 1000)), os.path.splitext(resumable_dict['resumableFilename'])[1])),
                                     'video_upload_source': "Manual",
                                     'video_upload_source_id': request.form.get('user_id'),
                                     'remarks': json.dumps({"Remarks": request.form.get('remarks'), "Summary": request.headers.get('summary') if request.headers.get('summary') else ''}),
                                     'video_filename': request.form.get('resumableFilename'),
                                     'state_id': int(master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending'])) if master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending']).isdigit() else None}
                    # insert_params = {'cam_id': int(master_data_obj.camera_mapper.get(cam_name)) if master_data_obj.camera_mapper.get(cam_name).isdigit() else master_data_obj.camera_mapper.get(cam_name),
                    #                  'video_upload_start_datetime': date_of_upload.strftime('%Y-%m-%d %H:%M:%S'),
                    #                  'video_end_point': os.path.join(entity, location, 'video', '{}/{}/{}/{}/{}{}'.format(cam_name, date_of_upload.year, date_of_upload.month, date_of_upload.day, str(int(date_of_upload.timestamp() * 1000)), os.path.splitext(resumable_dict['resumableFilename'])[1])),
                    #                  'video_upload_source': "Manual",
                    #                  'video_upload_source_id': request.form.get('user_id'),
                    #                  'remarks': request.form.get('remarks'),
                    #                  'video_filename': request.form.get('resumableFilename'),
                    #                  'state_id': int(master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending'])) if master_data_obj.state_mapper.get(connect.config_json['status']['upload_pending']).isdigit() else None}

                    connect.loginfo("inserting the upload starting time and other details {}".format(str(insert_params)), 'debug')
                    media_id = async_data_process.insert(table=Media, insert_params=insert_params, connect=connect)
                    connect.loginfo("added upload starting details and other details successfully")
                    redis_data.upload_status[resumable_dict['resumableFilename'] + '!' + cam_name] = {'file_name': resumable_dict['resumableFilename'],
                                                                                                      'media_id': str(media_id),
                                                                                                      'last_modified_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                                                      'resumable_total_chunks': resumable_dict['resumableTotalChunks'],
                                                                                                      'resumable_chunk_number': resumable_dict['resumableChunkNumber'],
                                                                                                      '%': round((int(resumable_dict['resumableChunkNumber']) / int(resumable_dict['resumableTotalChunks'])) * 100, 2),
                                                                                                      'uploading': 'true',

                                                                                                      'upload_start_date': date_of_upload.strftime('%Y-%m-%d %H:%M:%S.%f')}
                    connect.master_redis.set_val(key='upload_status', val=json.dumps(redis_data.upload_status))
            else:
                redis_data.upload_status[resumable_dict['resumableFilename'] + '!' + cam_name]['%'] = round((int(resumable_dict['resumableChunkNumber']) / int(resumable_dict['resumableTotalChunks'])) * 100, 2)
                redis_data.upload_status[resumable_dict['resumableFilename'] + '!' + cam_name]['last_modified_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                connect.master_redis.set_val(key='upload_status', val=json.dumps(redis_data.upload_status))
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            connect.loginfo("Exception in storing redis chunk data : " + str(e_) + str(exc_tb.tb_lineno), level='error')

        resumable = UploaderFlask(resumable_dict,
                                  app.config.get('video_location_to_resume'),
                                  app.config.get('chunk_location_to_resume'),
                                  request.files['file'])

        resumable.upload_chunk()

        if resumable.check_status() is True:
            resumable.assemble_chunks()
            resumable.cleanup()
            try:
                # entity_location = json.loads(request.headers.get('entity-location').replace("'", '"'))
                # entity = None
                # location = None
                # for key, value in entity_location.items():
                #     entity = key
                #     location = value['locations'][0]
                cam_name = request.form.get('cam_id') if request.form.get('cam_id') else request.headers.get('cam-id')
                _area = request.form.get('area') if request.form.get('area') else request.headers.get('area')
                _location = request.form.get('location') if request.form.get('location') else request.headers.get('location')
                _entity = request.form.get('entity') if request.form.get('entity') else request.headers.get('entity')
                current_file = json.loads(connect.master_redis.get_val(key='upload_status'))
                media_id = current_file[resumable_dict['resumableFilename'] + '!' + cam_name]['media_id']

                date_of_upload = datetime.strptime(redis_data.upload_status.get(resumable_dict['resumableFilename'] + '!' + cam_name).get('upload_start_date'), '%Y-%m-%d %H:%M:%S.%f')

                # cam_name = request.form.get('cam_id') if request.form.get('cam_id') else request.headers.get('cam-id')
                cam_id = master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(cam_name)
                connect.loginfo('checking if a file uploaded is in zip format or not')
                if ".zip" in resumable_dict['resumableFilename']:
                    zip_path = os.path.join(app.config.get('video_location_to_resume'), resumable_dict['resumableFilename'])
                    if zipfile.is_zipfile(zip_path):
                        connect.loginfo('checking if zip path exists or not')
                        if os.path.exists(zip_path):
                            connect.loginfo('file uploaded is a zip file')
                            ExtractImages.unzip(zip_path)
                            file_path = os.path.split(str(zip_path))[0]
                            connect.loginfo('zip file path is {}'.format(zip_path))
                            os.remove(zip_path)
                            if os.path.exists(os.path.join(file_path, resumable_dict['resumableFilename'].split('.')[0])):
                                file_path_extracted = os.path.join(file_path, resumable_dict['resumableFilename'].split('.')[0])
                                connect.loginfo('file_path_extracted :' + str(file_path_extracted))
                                if 'classes.txt' in os.listdir(file_path_extracted):
                                    connect.loginfo('classes.txt file is present')
                                    year, month, day = str(date_of_upload.year), str(date_of_upload.month), str(date_of_upload.day)
                                    images_path = os.path.join(connect.config_json.get('static_path'), entity, location, 'image', cam_name, year, month, day, str(date_of_upload.timestamp() * 1000).split('.')[0] + str('_images'))
                                    annotations_path = os.path.join(connect.config_json.get('static_path'), entity, location, 'annotation', cam_name, year, month, day, str(date_of_upload.timestamp() * 1000).split('.')[0] + str('_annotations'))
                                    connect.loginfo('checking for image path-{} and annotation path-{}'.format(images_path, annotations_path))
                                    if not os.path.exists(images_path) and not os.path.exists(annotations_path):
                                        connect.loginfo('making directories of image path and annotations path')
                                        os.makedirs(images_path)
                                        os.makedirs(annotations_path)
                                    for name in os.listdir(file_path_extracted):
                                        if os.path.isdir(os.path.join(file_path_extracted, name)):
                                            all_files = os.listdir(os.path.join(file_path_extracted, name))
                                            connect.loginfo('checking for image and txt files inside the directory-{} and moving images to image path-{} and txt files to annotations path-{}'.format(os.path.join(file_path_extracted, name), images_path, annotations_path))
                                            for file in all_files:
                                                if '.jpg' in file:
                                                    shutil.move(os.path.join(file_path_extracted, name, file),
                                                                images_path)
                                                elif '.txt' in file:
                                                    shutil.move(os.path.join(file_path_extracted, name, file),
                                                                annotations_path)
                                            connect.loginfo('images and txt files moved successfully')

                                    connect.loginfo('moving classes.txt file to annotations path-{}'.format(annotations_path))
                                    shutil.move(os.path.join(file_path_extracted, 'classes.txt'), annotations_path)
                                    connect.loginfo('classes.txt moved successfully')
                                    connect.loginfo('zipping images path-{}'.format(images_path))
                                    extract_images.zip(images_path)
                                    connect.loginfo('image path zipped successfully')
                                    blob_image_end_point = str(images_path.split('static')[1][1:]) + ".zip"
                                    connect.loginfo('blob image end point -{}'.format(blob_image_end_point))
                                    connect.loginfo('zipping annotations path-{}'.format(annotations_path))
                                    extract_images.zip(annotations_path)
                                    connect.loginfo('annotations path zipped successfully')
                                    blob_annotation_end_point = str(annotations_path.split('static')[1][1:]) + ".zip"
                                    connect.loginfo('blob annotations end point -{}'.format(blob_annotation_end_point))
                                    if os.path.exists(images_path + '.zip'):
                                        connect.loginfo('uploading images zip file to blob')
                                        async_data_process.upload(file_to_upload=images_path + '.zip',
                                                                  _upload_location=blob_image_end_point)
                                        connect.loginfo('images zip file uploaded succesfully to blob')

                                    if os.path.exists(annotations_path + '.zip'):
                                        connect.loginfo('uploading annotations zip file to blob')
                                        async_data_process.upload(file_to_upload=annotations_path + '.zip',
                                                                  _upload_location=blob_annotation_end_point)
                                        connect.loginfo('annotations zip file uploaded succesfully to blob')

                                    update_params = {'video_end_point': None, 'cam_id': cam_id,
                                                     'image_end_point': blob_image_end_point,
                                                     'annotation_end_point': blob_annotation_end_point}
                                    filter_params = {'id': media_id}
                                    connect.loginfo('updating Media table in database with update params-{} and filter params-{}'.format(update_params, filter_params))
                                    async_data_process.update(Media, filter_params=filter_params,
                                                              update_params=update_params)
                                    connect.loginfo('database updated')
                                    insert_params = {'media_status_id': media_id, 'image_count': len(os.listdir(images_path)), 'media_end_point': blob_image_end_point, 'extraction_status': 'process_complete', 'remark': request.form.get('remarks')}
                                    connect.loginfo('updating MediaDuration table in database with insert params-{}'.format(insert_params))
                                    media_duration_id = async_data_process.insert(MediaDuration, insert_params=insert_params)
                                    connect.loginfo('database updated')
                                    connect.loginfo('reading classes.txt file')
                                    with open(os.path.join(annotations_path, 'classes.txt'), 'r') as tag:
                                        tags = tag.read()
                                    insert_list = []
                                    for t in tags.split('\n'):
                                        if t != '':
                                            insert_list.append({'media_duration_id': media_duration_id, 'tag_id': int(master_data_obj.class_mapper.get(t))})
                                    connect.loginfo('tags list {}'.format(insert_list))
                                    connect.loginfo('inserting tags in tags table in database')
                                    async_data_process.insert(MediaTagMap, multiple_param_insert=insert_list)
                                    connect.loginfo('database updated')

                                    shutil.rmtree(images_path)
                                    shutil.rmtree(annotations_path)
                                    shutil.rmtree(file_path_extracted)
                                    connect.loginfo('removed directory from server- {}'.format(file_path_extracted))
                                    upload_end_event_data = {'_cam_id': cam_name,
                                                             'cam_id': cam_id,
                                                             'date_of_upload': date_of_upload.isoformat(),
                                                             'local_video_location': None,
                                                             'annotation_end_point': blob_annotation_end_point,
                                                             'userid': request.headers.get('user-id'),
                                                             'video_filename': request.form.get('resumableFilename'),
                                                             'state': connect.config_json.get('status').get('annotate_pending')}
                                    connect.loginfo('calling fastsapi- resumable_upload_end_event')
                                    requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/resumable_upload_end_event", json=upload_end_event_data)
                                    connect.loginfo('removing key -{} from redis'.format(resumable_dict['resumableFilename'] + '!' + cam_name))
                                    redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
                                    connect.loginfo('setting key upload_status in redis')
                                    connect.master_redis.set_val(key='upload_status', val=json.dumps(redis_data.upload_status))
                                    return jsonify({"fileUploadStatus": True, "resumableIdentifier": resumable.repo.file_id})
                                elif 'vi$' in resumable_dict['resumableFilename'] or 'via$' in resumable_dict['resumableFilename']:
                                    via = True
                                    if 'vi$' in resumable_dict['resumableFilename']:
                                        via = False
                                    connect.loginfo('Uploading video and extracted images')
                                    year, month, day = str(date_of_upload.year), str(date_of_upload.month), str(date_of_upload.day)
                                    video_path = os.path.join(connect.config_json.get('static_path'), entity, location, 'video', cam_name, year, month, day)
                                    video_file = None
                                    images_path = os.path.join(connect.config_json.get('static_path'), entity, location, 'image', cam_name, year, month, day, str(date_of_upload.timestamp() * 1000).split('.')[0] + str('_images'))
                                    annotations_path = os.path.join(connect.config_json.get('static_path'), entity, location, 'annotation', cam_name, year, month, day, str(date_of_upload.timestamp() * 1000).split('.')[0] + str('_annotations'))
                                    connect.loginfo('checking for video path-{} and image path-{}'.format(video_path, images_path))
                                    connect.loginfo('making directories of video path, image path and annotation path')
                                    for path in [video_path, images_path] + [annotations_path] if via else [video_path, images_path]:
                                        if not os.path.exists(path):
                                            connect.loginfo("path = {}".format(path))
                                            os.makedirs(path)
                                    connect.loginfo('Moving files to video path, image path and annotation path')
                                    for name in os.listdir(file_path_extracted):
                                        if os.path.isdir(os.path.join(file_path_extracted, name)):
                                            if 'images' in name:
                                                all_files = os.listdir(os.path.join(file_path_extracted, name))
                                                connect.loginfo("images_path = {} allfiles  = {}".format(images_path, all_files))
                                                for file in all_files:
                                                    shutil.move(os.path.join(file_path_extracted, name, file), images_path)
                                            if 'annotations' in name:
                                                all_files = os.listdir(os.path.join(file_path_extracted, name))
                                                for file in all_files:
                                                    shutil.move(os.path.join(file_path_extracted, name, file), annotations_path)
                                        elif 'video' in name:
                                            video_file = os.path.join(video_path, str(date_of_upload.timestamp() * 1000).split('.')[0]) + os.path.splitext(name)[1]
                                            shutil.move(os.path.join(file_path_extracted, name), video_file)

                                    connect.loginfo("video_path = {}, exists = {}".format(video_path, os.path.exists(video_path)))
                                    connect.loginfo("image_path = {}, exists = {}, isdir = {}, isfile={}".format(images_path, os.path.exists(images_path), os.path.isdir(images_path), os.path.isfile(images_path)))
                                    connect.loginfo('zipping images path-{}'.format(images_path))
                                    extract_images.zip(images_path)
                                    connect.loginfo('image path zipped successfully')
                                    blob_image_end_point = str(images_path.split('static')[1][1:]) + ".zip"
                                    connect.loginfo('blob image end point -{}'.format(blob_image_end_point))
                                    connect.loginfo('zipping annotations path-{}'.format(annotations_path))
                                    extract_images.zip(annotations_path) if via else None
                                    connect.loginfo('annotations path zipped successfully')
                                    blob_annotation_end_point = str(annotations_path.split('static')[1][1:]) + ".zip"
                                    connect.loginfo('blob annotations end point -{}'.format(blob_annotation_end_point))
                                    blob_video_end_point = str(video_file.split('static')[1][1:])
                                    connect.loginfo('blob video end point -{}'.format(blob_video_end_point))
                                    if os.path.exists(images_path + '.zip'):
                                        connect.loginfo('uploading images zip file to blob')
                                        async_data_process.upload(file_to_upload=images_path + '.zip',
                                                                  _upload_location=blob_image_end_point)
                                        connect.loginfo('images zip file uploaded succesfully to blob')
                                    if os.path.exists(annotations_path + '.zip'):
                                        connect.loginfo('uploading annotations zip file to blob')
                                        async_data_process.upload(file_to_upload=annotations_path + '.zip',
                                                                  _upload_location=blob_annotation_end_point)
                                        connect.loginfo('annotations zip file uploaded succesfully to blob')
                                    # if os.path.exists(video_file):
                                    #     connect.loginfo('uploading video file to blob')
                                    #     async_data_process.upload(file_to_upload=video_file,
                                    #                               _upload_location=blob_video_end_point)
                                    #     connect.loginfo('video file uploaded succesfully to blob')
                                    update_params = {'video_end_point': blob_video_end_point, 'cam_id': cam_id,
                                                     'image_end_point': blob_image_end_point,
                                                     'annotation_end_point': blob_annotation_end_point if via else None}
                                    filter_params = {'id': media_id}
                                    connect.loginfo('updating Media table in database with update params-{} and filter params-{}'.format(update_params, filter_params))
                                    async_data_process.update(Media, filter_params=filter_params, update_params=update_params)
                                    connect.loginfo('database updated')
                                    insert_params = {'media_status_id': media_id, 'image_count': len(os.listdir(images_path)), 'media_end_point': blob_image_end_point, 'extraction_status': 'process_complete', 'remark': request.form.get('remarks')}
                                    connect.loginfo('updating MediaDuration table in database with insert params-{}'.format(insert_params))
                                    media_duration_id = async_data_process.insert(MediaDuration, insert_params=insert_params)
                                    connect.loginfo('database updated')
                                    connect.loginfo('reading classes.txt file')
                                    if via:
                                        with open(os.path.join(annotations_path, 'classes.txt'), 'r') as tag:
                                            tags = tag.read()
                                        insert_list = []
                                        for t in tags.split('\n'):
                                            if t != '':
                                                insert_list.append({'media_duration_id': media_duration_id, 'tag_id': int(master_data_obj.class_mapper.get(t))})
                                        connect.loginfo('tags list {}'.format(insert_list))
                                        connect.loginfo('inserting tags in tags table in database')
                                        async_data_process.insert(MediaTagMap, multiple_param_insert=insert_list)
                                        connect.loginfo('database updated')

                                    # shutil.rmtree(images_path)
                                    # shutil.rmtree(annotations_path) if via else None
                                    shutil.rmtree(file_path_extracted)
                                    connect.loginfo('removed directory from server- {}'.format(file_path_extracted))
                                    upload_end_event_data = {'_cam_id': cam_name,
                                                             'cam_id': cam_id,
                                                             'date_of_upload': date_of_upload.isoformat(),
                                                             'local_video_location': video_file,
                                                             'media_end_point': blob_video_end_point,
                                                             'userid': request.headers.get('user-id'),
                                                             'video_filename': request.form.get('resumableFilename'),
                                                             'state': connect.config_json.get('status').get('annotate_pending') if via else connect.config_json.get('status').get('extract_completed')}
                                    connect.loginfo('calling fastsapi- resumable_upload_end_event')
                                    requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/resumable_upload_end_event", json=upload_end_event_data)
                                    connect.loginfo('removing key -{} from redis'.format(resumable_dict['resumableFilename'] + '!' + cam_name))
                                    redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
                                    connect.loginfo('setting key upload_status in redis')
                                    connect.master_redis.set_val(key='upload_status', val=json.dumps(redis_data.upload_status))
                                    return jsonify({"fileUploadStatus": True, "resumableIdentifier": resumable.repo.file_id})
                                else:
                                    extract_video_file = os.listdir(file_path_extracted)[0]
                                    shutil.copy(os.path.join(file_path_extracted, extract_video_file), file_path)
                                    shutil.rmtree(file_path_extracted)
                                    redis_data.upload_status[extract_video_file + '!' + cam_name] = redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
                                    resumable_dict['resumableFilename'] = extract_video_file
                                    update_params = {
                                        'video_end_point': os.path.join(_entity, _location, 'video', '{}/{}/{}/{}/{}{}'.format(cam_name, date_of_upload.year, date_of_upload.month, date_of_upload.day, str(int(date_of_upload.timestamp() * 1000)), os.path.splitext(resumable_dict['resumableFilename'])[1])),
                                        'video_filename': resumable_dict['resumableFilename']}
                                    filter_params = {'id': media_id}
                                    async_data_process.update(table=Media, update_params=update_params, filter_params=filter_params)

                            else:
                                extract_video_file = os.listdir(file_path)[0]
                                local_path = os.path.join(connect.config_json.get('static_path'), _entity,
                                                          _location, 'video',
                                                          '{}/{}/{}/{}'.format(cam_name, date_of_upload.year,
                                                                               date_of_upload.month, date_of_upload.day))

                                if not os.path.exists(local_path):
                                    os.makedirs(local_path)
                                # else:
                                shutil.copy(os.path.join(file_path, extract_video_file), local_path)
                                redis_data.upload_status[extract_video_file + '!' + cam_name] = redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
                                resumable_dict['resumableFilename'] = extract_video_file
                                update_params = {
                                    'video_end_point': os.path.join(_entity, _location, 'video', '{}/{}/{}/{}/{}{}'.format(cam_name, date_of_upload.year, date_of_upload.month, date_of_upload.day, str(int(date_of_upload.timestamp() * 1000)), os.path.splitext(resumable_dict['resumableFilename'])[1])),
                                    'video_filename': resumable_dict['resumableFilename'],
                                }
                                filter_params = {'id': media_id
                                                 }
                                async_data_process.update(table=Media, update_params=update_params, filter_params=filter_params)
                    else:
                        redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
                        connect.master_redis.set_val(key='upload_status', val=json.dumps(redis_data.upload_status))
                        return jsonify({"message": "not a proper zip file", "resumableIdentifier": resumable.repo.file_id})

                print(resumable_dict['resumableFilename'] + '!' + cam_name)
                print(redis_data.upload_status.get(resumable_dict['resumableFilename'] + '!' + cam_name))
                date_of_upload = datetime.strptime(redis_data.upload_status.get(resumable_dict['resumableFilename'] + '!' + cam_name).get('upload_start_date'), '%Y-%m-%d %H:%M:%S.%f')
                media_end_point = os.path.join(_entity, _location, 'video', '{}/{}/{}/{}/{}{}'.format(cam_name, date_of_upload.year, date_of_upload.month, date_of_upload.day, str(int(date_of_upload.timestamp() * 1000)), os.path.splitext(resumable_dict['resumableFilename'])[1]))
                local_video_location = os.path.join(app.config.get('static_path'), media_end_point)
                if not os.path.exists(os.path.split(local_video_location)[0]):
                    os.makedirs(os.path.split(local_video_location)[0])
                os.rename(os.path.join(app.config.get('video_location_to_resume'), resumable_dict.get('resumableFilename')), local_video_location)
                upload_end_event_data = {'_cam_id': cam_name, 'cam_id': cam_id, 'date_of_upload': date_of_upload.isoformat(), 'media_end_point': media_end_point, 'local_video_location': local_video_location, 'userid': request.headers.get('user-id'), 'video_filename': request.form.get('resumableFilename'), 'state': connect.config_json.get('status').get('review_pending')}
                requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/resumable_upload_end_event", json=upload_end_event_data)
                redis_data.upload_status.pop(resumable_dict['resumableFilename'] + '!' + cam_name)
                connect.master_redis.set_val(key='upload_status', val=json.dumps(redis_data.upload_status))
            except Exception as e_:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                connect.loginfo("Exception in storing redis chunk data : " + str(e_) + str(exc_tb.tb_lineno), level='error')
            return jsonify({"fileUploadStatus": True,
                            "resumableIdentifier": resumable.repo.file_id})

        return jsonify({"chunkUploadStatus": True,
                        "resumableIdentifier": resumable.repo.file_id})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in upload post : " + str(e_) + str(exc_tb.tb_lineno), level='error')
        return jsonify({"end" + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@login_required
@app.route('/api/extract', methods=['POST'])
@cross_origin(supports_credentials=True)
def extract(data=None):
    connect.loginfo('extract  api is called')
    try:
        if data is not None:
            _data = data
        else:
            _data = request.json
        _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling fastapi/extract fastapp')
        response = requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/extract", json=_data)
        return jsonify("successfully added")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("extract  exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/review_again', methods=['POST'])
@cross_origin(supports_credentials=True)
def review_again():
    connect.loginfo('review again  api is called')
    try:
        _data = request.json
        _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling fastapi/review_again fastapp')
        response = requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/review_again", json=_data)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("review again exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/save_annotation', methods=['POST'])
@cross_origin(supports_credentials=True)
def save_annotation():
    connect.loginfo('save annotation  api is called')
    try:
        _data = request.json
        _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling fastapi/save_annotation in fastapp')
        response = requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/save_annotation", json=_data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("save annotation exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/submit_annotation', methods=['POST'])
@cross_origin(supports_credentials=True)
def submit_annotation():
    connect.loginfo('submit annotation  api is called')
    try:
        _data = request.json
        _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling fastapi/submit_annotation in fastapp')
        response = requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/submit_annotation", json=_data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("submit annotation exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_annotation', methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_annotation():
    connect.loginfo('fetch annotation api is called')
    try:
        connect.loginfo('fetch annotation api is called')
        annotation_end_point = request.args.get('annotation_end_point')
        connect.loginfo('json data received', level='debug')
        filter_params = {"annotation_end_point": annotation_end_point}
        connect.loginfo('querying EventLogs table in database using data {}'.format(filter_params))
        event_logs = async_data_process.select(EventLogs, filter_params, True)
        product_entity = MasterData.product_entity_mapper.get(str(event_logs.camera_id))
        local_zip_location = os.path.join(connect.config_json.get('static_path'), annotation_end_point)
        connect.loginfo('local zip location - {}'.format(str(local_zip_location)), level='debug')
        local_directory_location = os.path.splitext(local_zip_location)[0]
        connect.loginfo('local directory location - {}'.format(str(local_directory_location)), level='debug')
        response = {}
        images_list = []
        classes_list = []
        if not os.path.isdir(local_directory_location):
            connect.loginfo('local_directory_location :{} does not exists'.format(local_directory_location))
            if not os.path.isfile(local_zip_location):
                connect.loginfo('File does not exists at :{}'.format(local_directory_location))
                if not os.path.exists(os.path.split(local_zip_location)[0]):
                    connect.loginfo('Path:{} does not exists'.format(os.path.split(local_zip_location)[0]))
                    connect.loginfo('making directories')
                    os.makedirs(os.path.split(local_zip_location)[0])
                connect.loginfo('File is being downloaded')
                async_data_process.download(annotation_end_point, local_zip_location)
                connect.loginfo('File downloaded successfully')
            connect.loginfo('File is being extracted')
            extract_images.unzip(local_zip_location)
            connect.loginfo('File extracted successfully')
        else:
            connect.loginfo('local_directory_location :{} exists'.format(local_directory_location))
            pass
        for root, dirs, files in os.walk(local_directory_location):
            connect.loginfo('checking text files in local_directory_location :{}'.format(local_directory_location))
            files = [file for file in files if file.endswith(".txt") and not file.startswith("class")]
            class_list = []
            if os.path.isfile(os.path.join(local_directory_location, 'classes.txt')):
                class_list = open(os.path.join(local_directory_location, 'classes.txt')).readlines()
                class_list = {str(v): k[:-1] for v, k in enumerate(class_list)}
            for file in files:
                data = ''
                with open(os.path.join(local_directory_location, file)) as fp:
                    data = fp.read()

                class_id, x_txt, y_txt, w_txt, h_txt = data.split()[:5]
                x_txt, y_txt, w_txt, h_txt = float(x_txt), float(y_txt), float(w_txt), float(h_txt)
                image_name = file.replace('.txt', '.jpg')
                image = cv2.imread(os.path.join(local_directory_location, file).replace('.txt', '.jpg'))
                x_res, y_res = image.shape[1], image.shape[0]

                w_txt = int(w_txt * x_res)
                h_txt = int(h_txt * y_res)
                x_txt = int((x_txt * x_res) - (w_txt / 2))
                y_txt = int((y_txt * y_res) - (h_txt / 2))

                response[file] = {"filename": file,
                                  "size": reduce(lambda x, y: x * y, image.shape),
                                  "image_link": os.path.join(connect.config_json.get('static_url'), "{}/{}".format(os.path.splitext(annotation_end_point)[0], image_name)),
                                  "regions": [{"shape_attributes": {"name": "rect",
                                                                    "x": x_txt,
                                                                    "y": y_txt,
                                                                    "width": w_txt,
                                                                    "height": h_txt},
                                               "region_attributes": {"Categories": class_list.get(class_id)}
                                               }],

                                  "file_attributes": {}}

                connect.loginfo("image link = {}".format(response[file]['image_link']), 'debug')

                images_list.append({"name": file,
                                    "size": reduce(lambda x, y: x * y, image.shape),
                                    "image_link": os.path.join(connect.config_json.get('static_url'), "{}/{}".format(os.path.splitext(annotation_end_point)[0], image_name))})

                if class_list.get(class_id) not in classes_list:
                    classes_list.append(class_list.get(class_id))
        response = {"_via_attributes": {"file": {}, "region": {"Categories": {"default_value": "", "description": "", "type": "dropdown"}}},
                    "_via_data_format_version": "2.0.10",
                    "_via_image_id_list": list(response.keys()),
                    "_via_img_metadata": response,
                    "_via_settings": {"core": {"buffer_size": 18, "default_filepath": "", "filepath": {}},
                                      "project": {"name": 18},
                                      "ui": {"annotation_editor_fontsize": 0.8, "annotation_editor_height": 25,
                                             "image": {"on_image_annotation_editor_placement": "NEAR_REGION",
                                                       "region_color": "__via_default_region_color__",
                                                       "region_label": "__via_region_id__",
                                                       "region_label_font": "10px Sans"},
                                             "image_grid": {"img_height": 80, "rshape_fill": "none",
                                                            "rshape_fill_opacity": 0.3,
                                                            "rshape_stroke": "yellow",
                                                            "rshape_stroke_width": 2,
                                                            "show_image_policy": "all",
                                                            "show_region_shape": True},
                                             "leftsidebar_width": 18}}}
        final_response = {"header": product_entity,
                          "json": response,
                          "result": [{"images": images_list, "classes": classes_list}]}
        return final_response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in fetch_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/mark_annotation', methods=['POST'])
@cross_origin(supports_credentials=True)
def mark_annotation():
    connect.loginfo("mark annotation api is called")
    try:
        connect.loginfo('checking json data for mark annotation')
        _data = request.json
        connect.loginfo('json data {} received'.format(str(_data)), level='debug')
        blob_zip_end_point = _data.get('annotation_end_point')
        # _cam_name = request.args.get("cam_name")
        # _cam_id = int(master_data_obj.camera_mapper.get(_cam_name))
        local_zip_end_point = os.path.join(connect.config_json.get('static_path'), blob_zip_end_point)
        connect.loginfo("local zip end point is {}".format(str(local_zip_end_point)), level='debug')
        filename = _data.get('filename')
        status = _data.get('status')
        connect.loginfo('getting redis_status')
        redis_status = connect.master_redis.get_val(key=blob_zip_end_point)
        if redis_status:
            connect.loginfo('redis_status recieved')
            redis_status = json.loads(redis_status)
            if status in redis_status:
                connect.loginfo('checking status key in redis_status')
                connect.loginfo('adding filename to status key in redis')
                redis_status[status].append(filename)
            else:
                connect.loginfo('status key already present adding filename to it')
                redis_status[status] = [filename]
            connect.loginfo('setting key value pair in redis with key {} and val {}'.format(blob_zip_end_point, json.dumps(redis_status)))
            connect.master_redis.set_val(key=blob_zip_end_point, val=json.dumps(redis_status))
        else:
            connect.loginfo('redis_status is not received')
            connect.loginfo('adding filenmame to redis')
            redis_status = {status: [filename], 'blob_zip_end_point': blob_zip_end_point}
            connect.master_redis.set_val(key=blob_zip_end_point, val=json.dumps(redis_status))
        update_params = {'image_status': json.dumps(redis_status)}
        filter_params = {'annotation_end_point': blob_zip_end_point}
        connect.loginfo('updating database EventLogs table with filter_params {} and update_params {}'.format(filter_params, update_params))
        async_data_process.update(table=EventLogs, update_params=update_params, filter_params=filter_params)
        connect.loginfo('database updated successfully')
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/train', methods=['POST'])
@cross_origin(supports_credentials=True)
def train():
    try:
        _data = request.json
        tags_names = _data.get('classes')
        model_name = _data.get('model_name')
        model_type = _data.get('model_type')
        userid = request.headers.get('user-id')
        class_mediaduration = {}
        mediaduration_mediaid = {}
        with Session_db() as db_session:
            table_data = db_session.execute('SELECT tag_id, media_duration_id FROM media_tags_mapping')
            for row in table_data.fetchall():
                if str(row[0]) not in class_mediaduration:
                    class_mediaduration[str(row[0])] = []
                class_mediaduration[str(row[0])].append(str(row[1]))

        with Session_db() as db_session:
            table_data = db_session.execute('SELECT id, media_status_id FROM t_media_durations')
        for row in table_data.fetchall():
            mediaduration_mediaid[str(row[0])] = str(row[1])

        tags_ids = [str(master_data_obj.class_mapper.get(str(tag_name))) for tag_name in tags_names]
        media_duration_lists = [class_mediaduration.get(str(tag_id)) for tag_id in tags_ids]

        media_duration_ids = []
        for media_duration_id_list in media_duration_lists:
            media_duration_ids.extend(media_duration_id_list)
        media_ids = []
        for media_duration_id in media_duration_ids:
            if str(mediaduration_mediaid.get(str(media_duration_id))) not in media_ids:
                media_ids.append(str(mediaduration_mediaid.get(str(media_duration_id))))

        blob_end_points = []
        for media_id in async_data_process.select(table=Media, filter_params={'id': media_ids, 'state_id': [6, 7]}):
            media_id = dict(media_id)
            blob_end_points.append({'blob_image_end_point': media_id['image_end_point'], 'blob_annotation_end_point': media_id['annotation_end_point']})
        # camera_name = _data.get('camera_name')
        # camera_id = int(master_data_obj.camera_mapper.get(camera_name))
        # tags = async_data_process.join_select(tables=[[Media, MediaDuration], [MediaDuration, MediaTagMap], [MediaTagMap, Classes]],
        #                                       join_params=[{1: ['id', 'media_status_id']}, {1: ['id', 'media_duration_id']}, {1: ['tag_id', 'id']}],
        #                                       add_column_params=[{1: ['image_count']}, {}, {1: ['name']}],
        #                                       table_names=[['media', 'media_duration'], ['media_duration', 'media_tag_mapping'], ['media_tag_mapping', 'tags']])
        entity = list(connect.config_json.get('entity-location').keys())[0]
        location = connect.config_json['entity-location'][entity]['locations'][0]

        response = {"end_points": blob_end_points,
                    "total_classes": len(tags_ids),
                    "model_name": model_name,
                    "user_id": str(userid),
                    "model_type": model_type,
                    "location_id": master_data_obj.mapper.get(entity).get('location_mapper').get(location),
                    "model_type_id": master_data_obj.model_type_mapper.get(model_type),
                    "config": _data.get('config'),
                    # "config_end_point": _data.get('config_end_point'),
                    "conv_end_point": _data.get('conv_end_point')}
        connect.loginfo('publishing data')
        connect.publish(event=json.dumps(response))
        connect.loginfo('data published successfully')
        return jsonify({"message": "Published data for training"})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in train api " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in train" + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route('/api/download_model', methods=['POST'])
@cross_origin(supports_credentials=True)
def download_model():
    connect.loginfo("download model api is called")
    try:
        connect.loginfo('checking json data', level='debug')
        _data = request.json
        connect.loginfo('json data {} received'.format(str(_data)), level='debug')
        model_name = _data.get('model_name')
        response = {"model_name": model_name, "message": "GET MODEL"}
        connect.loginfo('publishing data')
        connect.publish(event=json.dumps(response), routing_key="model.download.#")
        connect.loginfo('data published successfully')
        return jsonify({"message": "Published data for training"})
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
        return jsonify({"message": "exception in mark_annotation " + str(e_) + ' ' + str(exc_tb.tb_lineno)})


@app.route('/api/fetch_extracted_videos', methods=['GET'])
@cross_origin(supports_credentials=True, **constants.api_v2_cors_config)
def fetch_extracted_videos():
    try:
        connect.loginfo("fetch extracted videos api  is called")
        """api for fetching the videos which has been already extracted """
        connect.loginfo('checking json data', level='debug')
        _data = request.values
        connect.loginfo('json data {} received'.format(str(_data)), level='debug')
        _cam_name = _data.get("cam_name")
        _state_name = _data.get("state_name")
        _area = _data.get("area")
        _location = _data.get("location")
        _entity = _data.get("entity")
        # connect.loginfo(" master_data_obj.camera_mapper.get(_cam_name)= {}".format(master_data_obj.camera_mapper.get(_cam_name)), 'debug')
        # _cam_id = master_data_obj.camera_mapper.get(_cam_name)
        connect.loginfo(" camera id = {}".format(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(_cam_name)), 'debug')
        _cam_id = master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(_cam_name)
        connect.loginfo("master_data_obj.state_mapper.get(_state_name) if _state_name else None = {}".format(master_data_obj.state_mapper.get(_state_name) if _state_name else None), 'debug')
        _state_id = master_data_obj.state_mapper.get(_state_name) if _state_name else None

        _cam_id = int(_cam_id) if str(_cam_id).isdigit() else _cam_id
        _state_id = int(_state_id) if _state_id and str(_state_id).isdigit() else _state_id
        filter_params = {'cam_id': _cam_id,
                         'state_id': _state_id}
        connect.loginfo('querying database table Media with data {}'.format(filter_params))
        entries = async_data_process.select(table=Media, filter_params=filter_params, get_first_row=False)
        connect.loginfo('query successful')
        response = defaultdict(list)
        connect.loginfo('fetching of videos started')
        for entry in entries:
            l2 = []
            entry = dict(entry)
            filter_params = {'media_status_id': entry['id']}
            connect.loginfo('querying database table MediaDuration with data {}'.format(filter_params))
            durations = async_data_process.select(table=MediaDuration, filter_params=filter_params, get_first_row=False)
            connect.loginfo('query successful')
            for duration in durations:
                l1 = []
                duration = dict(duration)
                filter_params = {'media_duration_id': duration["id"]}
                connect.loginfo('querying database table MediaTagMAp with data {}'.format(filter_params))
                tags = async_data_process.select(table=MediaTagMap, filter_params=filter_params, get_first_row=False)
                connect.loginfo('query successful')
                for tag in tags:
                    tag = dict(tag)
                    filter_params = {'id': tag['tag_id']}
                    connect.loginfo('querying database table CLasses with data {}'.format(filter_params))
                    class_s = async_data_process.select(table=Classes, filter_params=filter_params, get_first_row=True)
                    connect.loginfo('query successful')
                    class_s = dict(class_s)
                    if class_s["name"] not in l1:
                        l1.append(class_s["name"])
                duration['id'] = {'id': duration['id'],
                                  'start_time': duration["start_time"],
                                  'end_time': duration["end_time"],
                                  'image_count': duration["image_count"],
                                  'remark': duration["remark"],
                                  'classes': l1}
                l2.append(duration['id'])
            entry['Duration'] = l2
            entry['remarks'] = str(entry.get('remarks')) if entry.get('remarks') is not None else "No remarks"
            entry['filename'] = str(entry.get('video_filename')) if entry.get('video_filename') is not None else "No file name"
            # connect.loginfo("master_data_obj.camera_mapper.get(str(entry['cam_id'])) = {}".format(master_data_obj.camera_mapper.get(str(entry['cam_id']))), 'debug')
            # entry['cam_id'] = master_data_obj.camera_mapper.get(str(entry['cam_id']))
            connect.loginfo("camera name = {}".format(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(str(entry['cam_id']))), 'debug')
            entry['cam_id'] = master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(str(entry['cam_id']))
            connect.loginfo("master_data_obj.state_action_mapper.get(str(entry['state_id'])) = {}".format(master_data_obj.state_action_mapper.get(str(entry['state_id']))), 'debug')
            entry['activity'] = master_data_obj.state_action_mapper.get(str(entry['state_id']))
            connect.loginfo("master_data_obj.state_mapper.get(str(entry['state_id'])) = {}".format(master_data_obj.state_mapper.get(str(entry['state_id']))), 'debug')
            entry['state_id'] = master_data_obj.state_mapper.get(str(entry['state_id']))
            entry['capture_end_datetime'] = entry['capture_end_datetime'].strftime('%Y-%m-%d %H:%M:%S') if entry[
                'capture_end_datetime'] else None
            entry['capture_start_datetime'] = entry['capture_start_datetime'].strftime('%Y-%m-%d %H:%M:%S') if entry[
                'capture_start_datetime'] else None
            entry['video_upload_end_datetime'] = entry['video_upload_end_datetime'].strftime('%Y-%m-%d %H:%M:%S') if entry[
                'video_upload_end_datetime'] else None
            entry['video_upload_start_datetime'] = entry['video_upload_start_datetime'].strftime('%Y-%m-%d %H:%M:%S') if \
                entry['video_upload_start_datetime'] else None
            response['data'].append(entry)
            connect.loginfo('response is {}'.format(response))
        connect.loginfo('videos fecthed seccessfully')
        return {"response": response, "re-extract": True if _state_id >= 4 else False}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("fetch extracted video  exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_master_rule_data', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def fetch_master_rule_data():
    connect.loginfo("fetch master rule data api  is called")
    """api for fetching all the details needed for inserting the  rules like location , camera, feature , tags, list of rule kinds, rule,types , operators  """
    try:
        connect.loginfo('checking json data', level='debug')
        response = master_rule
        entity_location = request.headers.get('entity-location')
        if entity_location:
            entity_location = json.loads(entity_location)
            if len(entity_location) == 0:
                entity_location = master_data.get('entity_location')
        else:
            entity_location = master_data.get('entity_location')
        connect.loginfo('json data {} received'.format(str(entity_location)), level='debug')
        entities = list(entity_location.keys())
        if len(entities) == 1:
            connect.loginfo('only one entity present {}'.format(entities))
            locations = entity_location[entities[0]]['locations']
            if len(locations) == 1:
                connect.loginfo('only one location present')
                response_1 = {'dropdown': {'location': {locations[0]: response['dropdown'][entities[0]]['location'][locations[0]]}, 'separate': response['dropdown'][entities[0]]['separate']}}
            else:
                connect.loginfo('more than one location present')
                response_1 = {'dropdown': response['dropdown'][entities[0]]}
        else:
            connect.loginfo('more than one entity present {}'.format(entities))
            response_1 = {'dropdown': response['dropdown']}
        return jsonify(response_1)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in fetch master rule " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/insert_rules', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def insert_rules():
    try:
        """api for  inserting the rules  """
        connect.loginfo("inset rule api  is called")
        connect.loginfo('checking json data', level='debug')
        _data = request.json
        connect.loginfo('json data {} received'.format(str(_data)), level='debug')
        _data['userid'] = request.headers.get('user-id')
        connect.loginfo('calling fastapi/insert_rules in  fastapp')
        response = requests.post(connect.config_json.get('host_name_fastapi') + "/insert_rules", json=_data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("insert rules exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_rules', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def fetch_rules():
    try:
        """api for fetching the rules according to the user selected feature name """
        connect.loginfo('fetching rules')
        feature = request.values['feature']
        response = master_rule
        user_id = request.headers.get('user-id')
        connect.loginfo('feature {} and user_id {} received'.format(feature, user_id), level='debug')
        connect.loginfo("master_data_obj.user_entity_mapper.get(user_id) = {}".format(master_data_obj.user_entity_mapper.get(user_id)), 'debug')
        entity_name = master_data_obj.user_entity_mapper.get(user_id)
        response_1 = {'feature_rule': response['feature_rule'][entity_name][feature]}
        connect.loginfo('fetch_rules successfully')
        return jsonify(response_1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("fetch rules exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_roles', methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_roles():
    connect.loginfo("fetch roles api is called")
    try:
        response = {"role_data": [], "department": [], "designation": [], "role_name": [], "role_policies": {}}
        entity_location = json.loads(request.headers.get('entity-location'))
        connect.loginfo('entity_location = {}'.format(str(entity_location)), level='debug')
        _entity = list(entity_location.keys())[0]
        _entity_id = int(master_data_obj.mapper.get('entity_mapper').get(_entity))
        connect.loginfo('entity_id = {}'.format(str(_entity_id)), level='debug')
        connect.loginfo('querying for roles in database RolePermissions table, using join_select', level='debug')
        role_permissions = async_data_process.join_select(tables=[[RolePermissions, Department, Designation]],
                                                          join_params=[{1: ['department_id', 'id'], 2: ['designation_id', 'id']}],
                                                          add_column_params=[{1: ['name'], 2: ['name']}],
                                                          table_names=[['role_permissions', 'department', 'designation']])
        connect.loginfo('fetched  details successfully', level='debug')
        connect.loginfo('querying for roles in database accessviews table, using select', level='debug')
        access_views = async_data_process.select(table=AccessViews, get_distinct_rows={"columns": ['name']})
        connect.loginfo('fetched  details successfully', level='debug')
        for role_permission in role_permissions:
            response["role_data"].append({"pk": role_permission[0].id,
                                          "fields": {
                                              "role_name": role_permission[0].role_name,
                                              "department": role_permission[1],
                                              "designation": role_permission[2]}})
            if role_permission[0].access_rules:
                policies = json.loads(role_permission[0].access_rules)["views"]
                response["role_policies"][role_permission[0].role_name] = {view.name: True if view.name in policies else False for view in access_views}
            else:
                response["role_policies"][role_permission[0].role_name] = {view.name: False for view in access_views}
            if role_permission[1] not in response["department"]:
                response["department"].append(role_permission[1])
            if role_permission[2] not in response["designation"]:
                response["designation"].append(role_permission[2])
            if role_permission[0].role_name not in response["role_name"]:
                if role_permission[0].entity_id == _entity_id:
                    response["role_name"].append(role_permission[0].role_name)
        response["role_data"] = response["role_data"][::-1]
        return jsonify(response)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in fetch roles " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_users', methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_users():
    connect.loginfo("fetch users api is called")
    try:
        response = {"user_data": {'ad': [], 'normal': []}, "department": [], "designation": [], "role_name": []}
        current_user_id = int(request.headers['user-id'])
        connect.loginfo('checking for user_id = {}'.format(str(current_user_id)))
        connect.loginfo('user_id {} received'.format(current_user_id), level='debug')
        connect.loginfo('querying for roles in database RolePermissions table', level='debug')
        roles = async_data_process.select(table=RolePermissions)
        connect.loginfo('query successful')
        roles = {role.id: role.role_name for role in roles}
        connect.loginfo('fetched  details from role permission table using join select function ', level='debug')
        role_permissions = async_data_process.join_select(tables=[[RolePermissions, Department, Designation]],
                                                          join_params=[{1: ['department_id', 'id'], 2: ['designation_id', 'id']}],
                                                          add_column_params=[{1: ['name'], 2: ['name']}],
                                                          table_names=[['role_permissions', 'department', 'designation']])
        connect.loginfo('fetched  details successfully', level='debug')
        connect.loginfo('querying for user_profiles in database table UserProfile')
        user_profiles = async_data_process.select(table=UserProfile)
        connect.loginfo('query successful')
        role_permissions = {role_permission[0].id: {"role_name": role_permission[0].role_name, "department": role_permission[1], "designation": role_permission[2]} for role_permission in role_permissions}
        connect.loginfo('role_permissions'.format(role_permissions))
        role_count = {}
        for user_profile in user_profiles:
            connect.loginfo('checking user login type')
            if user_profile.user_login_type == "ad":
                connect.loginfo(" entity name = {}".format(master_data_obj.mapper.get('entity_mapper').get(str(user_profile.entity_id)) if user_profile.entity_id != None else None, ), 'debug')
                _entity = master_data_obj.mapper.get('entity_mapper').get(str(user_profile.entity_id)) if user_profile.entity_id != None else None
                connect.loginfo("location name = {}".format(master_data_obj.mapper.get(str(_entity)).get('location_mapper').get(str(user_profile.location_id)) if user_profile.location_id != None else None), 'debug')
                _location = master_data_obj.mapper.get(str(_entity)).get('location_mapper').get(str(user_profile.location_id)) if user_profile.location_id != None else None
                response["user_data"]['ad'].append({"id": user_profile.id,
                                                    "full_name": user_profile.full_name,
                                                    "employee_id": user_profile.employee_id,
                                                    "email": user_profile.email,
                                                    "mobile": user_profile.mobile,
                                                    "gender": user_profile.gender,
                                                    "designation": role_permissions[user_profile.role_id]["designation"] if user_profile.role_id != None else None,
                                                    "department": role_permissions[user_profile.role_id]["department"] if user_profile.role_id != None else None,
                                                    "role": roles[user_profile.role_id] if user_profile.role_id != None else None,
                                                    "username": user_profile.login_name,
                                                    "entity": _entity,
                                                    "location": _location,
                                                    "password": secure_password.decrypt_password(user_profile.password)
                                                    })
                if user_profile.role_id:
                    if roles[user_profile.role_id] in role_count:
                        role_count[roles[user_profile.role_id]] += 1
                    else:
                        role_count[roles[user_profile.role_id]] = 1
            else:
                connect.loginfo(" entity name = {}".format(master_data_obj.mapper.get('entity_mapper').get(str(user_profile.entity_id)) if user_profile.entity_id != None else None, ), 'debug')
                _entity = master_data_obj.mapper.get('entity_mapper').get(str(user_profile.entity_id)) if user_profile.entity_id != None else None
                connect.loginfo("location name = {}".format(master_data_obj.mapper.get(str(_entity)).get('location_mapper').get(str(user_profile.location_id)) if user_profile.location_id != None else None), 'debug')
                _location = master_data_obj.mapper.get(str(_entity)).get('location_mapper').get(str(user_profile.location_id)) if user_profile.location_id != None else None
                response["user_data"]['normal'].append({"id": user_profile.id,
                                                        "full_name": user_profile.full_name,
                                                        "employee_id": user_profile.employee_id,
                                                        "email": user_profile.email,
                                                        "mobile": user_profile.mobile,
                                                        "gender": user_profile.gender,
                                                        "designation": role_permissions[user_profile.role_id]["designation"],
                                                        "department": role_permissions[user_profile.role_id]["department"],
                                                        "role": roles[user_profile.role_id] if user_profile.role_id != None else None,
                                                        "username": user_profile.login_name,
                                                        "entity": _entity,
                                                        "location": _location,
                                                        "password":secure_password.decrypt_password(user_profile.password)})
                if user_profile.role_id:
                    if roles[user_profile.role_id] in role_count:
                        role_count[roles[user_profile.role_id]] += 1
                    else:
                        role_count[roles[user_profile.role_id]] = 1
            if int(user_profile.id) == current_user_id:
                response['current_user_role'] = roles[user_profile.role_id]
        for role_id in role_permissions:
            if role_permissions[role_id]["department"] not in response["department"]:
                response["department"].append(role_permissions[role_id]["department"])
            if role_permissions[role_id]["designation"] not in response["designation"]:
                response["designation"].append(role_permissions[role_id]["designation"])
            if role_permissions[role_id]["role_name"] not in response["role_name"]:
                response["role_name"].append(role_permissions[role_id]["role_name"])
        response['role_count'] = role_count
        response['user_data']['normal'] = response['user_data']['normal'][::-1]
        return jsonify(response)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in fetch users " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/add_roles', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_roles():
    try:
        connect.loginfo("add roles api is called")
        entry = request.json
        connect.loginfo('data received = {}'.format(str(entry)), level='debug')
        entity_location = json.loads(request.headers.get('entity-location'))
        connect.loginfo('entity_location = {}'.format(str(entity_location)), level='debug')
        _entity = list(entity_location.keys())[0]
        _entity_id = int(master_data_obj.mapper.get('entity_mapper').get(_entity))
        connect.loginfo('entity_id = {}'.format(str(_entity_id)), level='debug')
        cards_obj = async_data_process.select(Entities,filter_params = {"id":_entity_id},get_first_row =True)
        # cards = json.loads(cards_obj.cards_permissions)
        cards = json.loads(cards_obj.cards_permissions)
        connect.loginfo('cards = {}'.format(str(cards)), level='debug')
        connect.loginfo('fetched  details from department table', level='debug')
        departments = async_data_process.select(table=Department)
        connect.loginfo('fetched  details successfully', level='debug')
        departments = {department.name: department.id for department in departments}
        connect.loginfo('fetched  details from desgnation table ', level='debug')
        designations = async_data_process.select(table=Designation)
        connect.loginfo('fetched  details successfully', level='debug')
        designations = {designation.name: designation.id for designation in designations}
        connect.loginfo('inserting data in role permission table', level='debug')
        access_rules = json.dumps({"views": [], "cards": cards})
        insert_params = {"role_name": entry["role_name"],
                         "department_id": departments[entry["department"]],
                         "designation_id": designations[entry["designation"]],
                         "access_rules":access_rules,
                         "entity_id":_entity_id}
        filter_params = {"role_name": entry["role_name"]}
        role_obj = async_data_process.select(table=RolePermissions, filter_params=filter_params,get_first_row=True)
        if not role_obj:
            async_data_process.insert(table=RolePermissions, insert_params=insert_params)
            return jsonify(({"status": "New role added"}))

        else:
            return Response("Role Name already exists", status=400, mimetype='application/json')


        # async_data_process.insert(table=RolePermissions, insert_params=insert_params)
        # connect.loginfo('inserted')
        # return jsonify(({"status": "New role added"}))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("add roles exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/edit_roles', methods=['POST'])
@cross_origin(supports_credentials=True)
def edit_roles():
    try:
        connect.loginfo("edit roles api is called")
        entry = request.json
        connect.loginfo('data received = {}'.format(str(entry)), level='debug')
        connect.loginfo('fetched  details from department table', level='debug')
        departments = async_data_process.select(table=Department)
        connect.loginfo('fetched  details successfully', level='debug')
        departments = {department.name: department.id for department in departments}
        connect.loginfo('fetched  details from designation table ', level='debug')
        designations = async_data_process.select(table=Designation)
        connect.loginfo('fetched  details successfully', level='debug')
        designations = {designation.name: designation.id for designation in designations}
        update_params = {"role_name": entry["role_name"],
                         "department_id": departments[entry["department"]],
                         "designation_id": designations[entry["designation"]]}

        role_obj = async_data_process.select(table=RolePermissions, filter_params={'id': entry["role_id"]},get_first_row=True)
        if entry["role_name"] == role_obj.role_name:
            async_data_process.update(table=RolePermissions, update_params=update_params, filter_params={'id': entry["role_id"]})
            return jsonify({"status": "Role edited"})
        else:
            filter_params = {'role_name': entry["role_name"]}
            obj = async_data_process.select(table=RolePermissions, filter_params=filter_params)
            if not obj:
                filter_params = {"id": int(entry["role_id"])}
                async_data_process.update(table=RolePermissions, update_params=update_params, filter_params=filter_params)
                return jsonify({"status": "Role edited"})

            else:
                return Response("Role Name already exists", status=400, mimetype='application/json')
        # filter_params = {"id": int(entry["role_id"])}
        # connect.loginfo('updating the roles  table', level='debug')
        # async_data_process.update(table=RolePermissions, update_params=update_params, filter_params=filter_params)
        # connect.loginfo('updated')
        # return jsonify({"status": "Role edited"})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("edit roles exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/edit_access', methods=['POST'])
@cross_origin(supports_credentials=True)
def edit_access():
    try:
        connect.loginfo("edit access api is called")
        entry = request.json
        connect.loginfo('data received = {}'.format(str(entry)), level='debug')
        entity_location = json.loads(request.headers.get('entity-location'))
        connect.loginfo('entity_location = {}'.format(str(entity_location)), level='debug')
        _entity = list(entity_location.keys())[0]
        _entity_id = int(master_data_obj.mapper.get('entity_mapper').get(_entity))
        cards_obj = async_data_process.select(Entities, filter_params={"id": _entity_id}, get_first_row=True)
        connect.loginfo('entity_id = {}'.format(str(_entity_id)), level='debug')
        cards = json.loads(cards_obj.cards_permissions)
        connect.loginfo('cards = {}'.format(str(cards)), level='debug')
        connect.loginfo('fetching role permission table', level='debug')
        roles = async_data_process.select(table=RolePermissions)
        connect.loginfo('fetched  details successfully', level='debug')
        roles = {role.role_name: role.id for role in roles}
        views = []
        if entry["screens"]:
            for view in entry["screens"]:
                if str(view).lower() != 'dashboard' and entry["screens"][view]:
                    views.append(view)
                elif str(view).lower() == 'dashboard' and entry["screens"][view]:
                    views.insert(0, view)

        access_rules = json.dumps({"views": views,"cards":cards})
        update_params = {"access_rules": access_rules}
        filter_params = {"id": int(roles[entry["role_name"]])}
        connect.loginfo('updating the permission table', level='debug')
        async_data_process.update(table=RolePermissions, update_params=update_params, filter_params=filter_params)
        connect.loginfo('updated')
        return jsonify({"status": "Role access edited"})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("edit access exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

@app.route('/api/delete_roles', methods=['POST'])
@cross_origin(supports_credentials=True)
def delete_roles():
    try:
        connect.loginfo("delete roles api is called")
        entry = request.json
        connect.loginfo('data received - {}'.format(str(entry)), level='debug')
        filter_params = {"id": int(entry["role_id"])}
        connect.loginfo('deletion in role and permission table', level='debug')
        async_data_process.delete(table=RolePermissions, filter_params=filter_params)
        connect.loginfo('deleted')
        return jsonify({"status": "Role deleted"})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("delete roles" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/add_user', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_user():
    try:
        connect.loginfo('add user api is called', level='debug')
        connect.loginfo('fetched  details from role permission table ', level='debug')
        roles = async_data_process.select(table=RolePermissions)
        connect.loginfo('fetched', level='debug')
        roles = {role.role_name: role.id for role in roles}
        entry = request.json
        connect.loginfo('data received - {}'.format(str(entry)), level='debug')
        insert_params = {"full_name": entry["name"],
                         "login_name": entry["username"],
                         "password": secure_password.encrypt_password(entry["password"]),
                         "role_id": int(roles[entry["role"]]),
                         "employee_id": entry["employee_id"],
                         "gender": entry["gender"],
                         "mobile": entry["mobile"],
                         "email": entry["email"]}
        if entry.get("entity"):
            connect.loginfo("entity id ={}".format(master_data_obj.mapper.get('entity_mapper').get(entry.get("entity"))), 'debug')
            connect.loginfo("location id ={}".format(master_data_obj.mapper.get(entry.get("entity")).get('location_mapper').get(entry.get("location"))), 'debug')
            _location = master_data_obj.mapper.get(entry.get("entity")).get('location_mapper').get(entry.get("location"))
            insert_params["entity_id"] = int(master_data_obj.mapper.get('entity_mapper').get(entry.get("entity")))
            if entry.get("location"):
                insert_params["location_id"] = int(_location)
        connect.loginfo('inserting data in user profile table', level='debug')
        filter_params = {"login_name": entry["username"]}
        obj = async_data_process.select(UserProfile, filter_params=filter_params)
        if not obj:
            if entry["role"].lower() != "administrator":
                async_data_process.insert(table=UserProfile, insert_params=insert_params)
                connect.loginfo('inserted')
                return jsonify({"status": "New user added"})
            else:
                insert_params["user_login_type"] = 'ad'
                async_data_process.insert(table=UserProfile, insert_params=insert_params)
                connect.loginfo('inserted')
                return jsonify({"status": "New user added"})
        else:
            return Response("User Name already exists", status=400, mimetype='application/json')

    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            connect.loginfo("add user exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/edit_user', methods=['POST'])
@cross_origin(supports_credentials=True)
def edit_user():
    try:
        connect.loginfo("edit user api  is called")
        connect.loginfo('fetching the role permission table ', level='debug')
        roles = async_data_process.select(table=RolePermissions)
        connect.loginfo('fetched', level='debug')
        roles = {role.role_name: role.id for role in roles}
        entry = request.json
        connect.loginfo('data received - {}'.format(str(entry)), level='debug')
        update_params = {"full_name": entry["name"],
                         "login_name": entry["username"],
                         "role_id": int(roles[entry["role"]]),
                         "employee_id": entry["employee_id"],
                         "password": secure_password.encrypt_password(entry["password"]),
                         "gender": entry["gender"],
                         "mobile": entry["mobile"],
                         "email": entry["email"]}
        if entry.get("entity"):
            connect.loginfo("entity id ={}".format(master_data_obj.mapper.get('entity_mapper').get(entry.get("entity"))), 'debug')
            connect.loginfo("location id ={}".format(master_data_obj.mapper.get(entry.get("entity")).get('location_mapper').get(entry.get("location"))), 'debug')
            _location = master_data_obj.mapper.get(entry.get("entity")).get('location_mapper').get(entry.get("location"))
            update_params["entity_id"] = int(master_data_obj.mapper.get('entity_mapper').get(entry.get("entity")))
            if entry.get("location"):
                update_params["location_id"] = int(_location)
        user_obj = async_data_process.select(table=UserProfile, filter_params={'id': entry["id"]}, get_first_row=True)
        if entry["username"] == user_obj.login_name:
            async_data_process.update(table=UserProfile, update_params=update_params,
                                      filter_params={'id': int(entry["id"])})
            return jsonify({"status": "User edited"})
        else:
            filter_params = {'login_name': entry["username"]}
            obj = async_data_process.select(table=UserProfile, filter_params=filter_params)
            if not obj:
                filter_params = {"id": int(entry["id"])}
                async_data_process.update(table=UserProfile, update_params=update_params, filter_params=filter_params)
                return jsonify({"status": "User edited"})

            else:
                return Response("User Name already exists", status=400, mimetype='application/json')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("edit user exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/delete_user', methods=['GET'])
@cross_origin(supports_credentials=True)
def delete_user():
    try:
        connect.loginfo("delete user api  is called")
        entry = request.values
        connect.loginfo('data received - {}'.format(str(entry)), level='debug')
        filter_params = {"id": int(entry["id"])}
        connect.loginfo('deletion in tableuser profile ', level='debug')
        async_data_process.delete(table=UserProfile, filter_params=filter_params)
        connect.loginfo('deletion done')
        return jsonify({"status": "User deleted"})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("delete user" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/insert_event_data', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def insert_event_data():
    try:
        connect.loginfo('checking for json data for inserting the event data', level='debug')
        data = request.json
        feature = data.get('feature')
        image_end_point = data.get('image_end_point')
        event_data = data.get('event_data')
        connect.loginfo('json data received {}'.format(str(data)), level='debug')
        for i in event_data:
            connect.loginfo("master_data_obj.feature_mapper.get(str(feature))  = {}".format(master_data_obj.feature_mapper.get(str(feature))), 'debug')
            connect.loginfo("str(master_data_obj.camera_mapper.get(str(i.get('camera_name'))))  = {}".format(str(master_data_obj.camera_mapper.get(str(i.get('camera_name'))))), 'debug')

            insert_params = {
                'feature_id': master_data_obj.feature_mapper.get(str(feature)),
                'image_end_point': str(image_end_point),
                'start_datetime': str(i.get('start_datetime')),
                'end_datetime': str(i.get('end_datetime')),
                'camera_id': str(master_data_obj.camera_mapper.get(str(i.get('camera_name'))))
            }
            connect.loginfo('inserting data in event table', level='debug')
            async_data_process.insert(table=Event, insert_params=insert_params)
        data['api_end_point'] = 'insert_event_data'
        if 'sync' not in data:
            if hq_connect:
                hq_connect.publish(event=json.dumps(data))
            else:
                sql = '''select area_id from m_camera where name = '{}' '''.format(event_data[0]['camera_name'])
                rows, no_of_rows = connect.query_database(sql=sql)
                if no_of_rows > 0:
                    area_id = rows[0][0]
                    sql = '''select location_id from m_area where id = '{}' '''.format(area_id)
                    rows, no_of_rows = connect.query_database(sql=sql)
                    if no_of_rows > 0:
                        location_id = rows[0][0]
                        sql = '''select ip from m_edge where location_id = '{}' '''.format(location_id)
                        rows, no_of_rows = connect.query_database(sql=sql)
                        if no_of_rows > 0:
                            ip = rows[0][0]
                            constants.hq_rabbitmq_publisher["rabbitmq_host"] = ip
                            edge_connect = Utility(configuration=constants.hq_flask_utility_configuration, rabbitmq_publisher=constants.hq_rabbitmq_publisher)
                            edge_connect.publish(event=json.dumps(data))
        response = "added event data successfully"
        return jsonify(response)
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in insert event data " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_event_data', methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_event_data():
    try:
        connect.loginfo('fetch event data')
        date = request.args.get('date')
        response = event_data.event_fetch_data(connect, date)
        return json.loads(json.dumps(response['dashboard']))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("fetch event data exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/re_annotate', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def re_annotate():
    try:
        """api for re annotate  """
        connect.loginfo("re annotate api is called")
        connect.loginfo('checking for json data')
        _data = {'media_id': request.args.get('media_id'), 'userid': request.headers.get('user-id')}
        connect.loginfo('json data received {}'.format(str(_data)), level='debug')
        updated = async_data_process.update(table=Media, update_params={"state_id": master_data_obj.state_mapper.get(connect.config_json['status']['annotate_pending'])}, filter_params={"id": _data.get('media_id')})
        connect.loginfo('calling fastapi/re_annotate_images in fastapp')
        response = requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/re_annotate_images", json=_data)
        response = {'message': 'added successfully!', 'status_code': 200}
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("re annotate" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route("/api/fetch_live_feed_annotations", methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_live_feed_annotations():
    try:
        timer = connect.config_json.get("timer")
        connect.loginfo('fetch_live_feed_annotations api is called')
        from_datetime = request.args.get('from_datetime')
        from_year, from_month, from_date, from_hour, from_minute = datetime.strptime(from_datetime, '%Y-%m-%d %H:%M').year, datetime.strptime(from_datetime, '%Y-%m-%d %H:%M').month, datetime.strptime(from_datetime, '%Y-%m-%d %H:%M').day, datetime.strptime(from_datetime, '%Y-%m-%d %H:%M').hour, datetime.strptime(from_datetime, '%Y-%m-%d %H:%M').minute
        to_datetime = request.args.get('to_datetime')
        to_year, to_month, to_date, to_hour, to_minute = datetime.strptime(to_datetime, '%Y-%m-%d %H:%M').year, datetime.strptime(to_datetime, '%Y-%m-%d %H:%M').month, datetime.strptime(to_datetime, '%Y-%m-%d %H:%M').day, datetime.strptime(to_datetime, '%Y-%m-%d %H:%M').hour, datetime.strptime(to_datetime, '%Y-%m-%d %H:%M').minute
        camera_name = request.args.get('camera_name')
        _area = request.args.get('area')
        _location = request.args.get('location')
        _entity = request.args.get('entity')
        camera_id = int(master_data_obj.mapper.get(_entity).get(_location).get(_area).get('camera_mapper').get(camera_name))
        entity_location = request.headers.get('entity-location')
        if entity_location:
            entity_location = json.loads(entity_location)
            if len(entity_location) == 0:
                entity_location = master_data.get('entity_location')
        else:
            entity_location = master_data.get('entity_location')
        from_date_datetime = datetime(from_year, from_month, from_date, from_hour, from_minute, 00)
        to_date_datetime = datetime(to_year, to_month, to_date, to_hour, to_minute, 00)
        filter_params = {"year": [item for item in range(from_date_datetime.year, to_date_datetime.year + 1)],
                         "month": [item for item in range(from_date_datetime.month, to_date_datetime.month + 1)],
                         "day": [item for item in range(from_date_datetime.day, to_date_datetime.day + 1)],
                         "hour": [item for item in range(from_date_datetime.hour, to_date_datetime.hour + 1)],
                         "minute_15": [item for item in range(from_date_datetime.minute // timer, (to_date_datetime.minute // timer) + 1)],
                         "camera_id": camera_id}
        data = async_data_process.select(FeedRemarks, filter_params=filter_params)
        response = {"camera_id": camera_id, "remarks": {}}
        for data_item in data:
            key = str(data_item.year) + "_" + str(data_item.month) + "_" + str(data_item.day) + "_" + str(data_item.hour) + "_" + str(data_item.minute_15)
            remark_json = data_item.remarks
            response['remarks'][key] = remark_json
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("fetch_live_feed_annotations exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/get_remarks', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_remarks():
    try:
        connect.loginfo('get remarks api is called')
        response = []
        remarks_obj = async_data_process.select(table=Remarks)
        for remarks in remarks_obj:
            response.append(remarks.remarks)
        return jsonify(response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in get  remarks" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/fetch_master_data', methods=['GET'])
@cross_origin(supports_credentials=True)
def fetch_master_data():
    try:
        """api for fetching the master data ie the data needed n homepage for fetching the videos """
        connect.loginfo("1. Fetch master data is called", level='info')
        entity_location = request.headers.get('entity-location')
        entity_location = master_data_obj.get_entity_location(entity_location)
        response = copy.deepcopy(master_data)
        response_1 = response.copy()
        response['entity_product_cam'] = {}
        response['classes'] = []
        for key, value in entity_location.items():
            entity = key
            entity_id = str(master_data_obj.mapper.get('entity_mapper').get(entity))
            filter_params = {'entity_id': entity_id}
            entries = async_data_process.select(table=Classes, filter_params=filter_params, get_distinct_rows={"columns": ['name']})
            connect.loginfo('2. Classes fetch successful', level='info')
            response['classes'] = ([x.name for x in entries])
            for location in value['locations']:
                response['entity_product_cam'] = {key: {"locations": {location: response_1['entity_product_cam'][key]['locations'][location]}, 'products': {key: response_1['entity_product_cam'][key]['products'][key]}}}
        connect.loginfo('3. Master data fetched for {entity_location}'.format(entity_location=str(entity_location)), level='info')
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Fetch master data exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/event_status', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def event_status():
    try:
        connect.loginfo('checking for json data in event status', level='debug')
        data = request.json
        connect.loginfo('json data received {}'.format(str(data)), level='debug')
        connect.loginfo('querying status in database table Event', level='debug')
        async_data_process.update(table=Event, update_params={"status": data.get("status")}, filter_params={"id": data.get("id")})
        connect.loginfo('update successful')
        return jsonify("successfully changed")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("event status exception" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

@app.route('/api/mark_event', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def mark_event():
    try:
        if request.method == 'POST':
            data = request.json
            id, image_end_point, mark_as = data.get("id"), data.get("image_end_point"), data.get("mark_as")
            if mark_as:
                connect.loginfo('1. Marking {id}/{image_end_point} as {mark_as}'.format(id=id,
                                                                                        image_end_point=image_end_point,
                                                                                        mark_as=mark_as), level='info')
                filter_params = {"id": id} if id else {"image_end_point": image_end_point}
                async_data_process.update(table=Event, update_params={"confusion_matrix": mark_as}, filter_params=filter_params)
                connect.loginfo('2. Marked successfully', level='info')
                return jsonify("successfully changed")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in mark_event" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

@app.route('/api/ack_event', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def ack_event():
    try:
        if request.method == 'POST':
            data = request.json
            id, image_end_point,= data.get("id"), data.get("image_end_point")
            connect.loginfo('1. Acknowledging {id}/{image_end_point}'.format(id=id,
                                                                             image_end_point=image_end_point), level='info')
            filter_params = {"id": id} if id else {"image_end_point": image_end_point}
            async_data_process.update(table=Event, update_params={"user_ack": 1}, filter_params=filter_params)
            connect.loginfo('2. Acknowledged successfully', level='info')
            return jsonify("successfully changed")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("#. Exception in ack_event" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

@app.route('/api/video_live_feed', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def video_live_feed():
    connect.loginfo('video live feed  api is called')
    user_id = request.headers.get("user-id")
    area = request.args.get('area')
    connect.loginfo("Entry " + area, level='debug')
    try:
        # con_str = connect.config_json.get("celery_broker")
        # if con_str:
        #     mq_conn = Connection(con_str)
        #     channel = mq_conn.channel()
        #     vhost = '/'
        #     manager = mq_conn.get_manager()
        #
        #     queues = manager.get_queues(vhost)
        #     for queue in queues:
        #         queue_name = queue['name']
        #         if queue_name == "live_feed_{}".format(area):
        #             channel.queue_delete(queue_name)
        #
        # if con_str:
        #     mq_conn = Connection(con_str)
        #     channel = mq_conn.channel()
        #     vhost = '/'
        #     manager = mq_conn.get_manager()
        #     queues = manager.get_queues(vhost)
        #     for queue in queues:
        #         queue_name = queue['name']
        #         if queue_name == "live_feed_area_{}".format(user_id):
        #             channel.queue_delete(queue_name)

        connect.loginfo('getting frames')
        connect.loginfo('trying to make a consumer connection')
        # area_user_id = str(area)+ "_" + str(user_id)
        # video_stream = VideoStreamConsumer(area_user_id, Utility)
        video_stream = VideoStreamConsumer(area, Utility)
        connect.loginfo('Checking if client connection exists already')
        # if video_stream.hpcl_client:
        #     connect.loginfo('client connection exists')
        #     try:
        #         connect.loginfo('closing the client connection')
        #         video_stream.hpcl_client.close()
        #         connect.loginfo('client connection closed')
        #     except Exception as e_:
        #         connect.loginfo('Exception:{}'.format(e_), level='error')
        #         pass
        #     video_stream.hpcl_client = None
        connect.loginfo('initiating new socket connection')
        video_stream.connect = video_stream.initiate_socket()
        connect.loginfo('new consumer connection established')
        connect.loginfo('getting frames from area {}'.format(area))
        return Response(video_stream.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("exception in video_feed_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


@app.route('/api/submit_remarks', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def submit_remarks():
    camera_id = request.json['camera_id']
    remarks = request.json['remarks']
    _data = {'remarks': remarks, 'userid': request.headers.get('user-id'), 'camera_id': camera_id}
    connect.loginfo('calling fastapi/re_annotate_images in fastapp')
    response = requests.post(connect.config_json.get('host_name_fastapi') + "/fastapi/submit_remarks", json=_data)
    response = {'message': 'added successfully!', 'status_code': 200}
    return jsonify(response)


@app.route('/api/global_dashboard', methods=['GET'])
@cross_origin(supports_credentials=True)
def global_dashboard():
    try:
        connect.loginfo('global_dashboard api is called')
        response = {}
        result = cards_data(app)
        response['cards'] = result
        return jsonify(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in global_dashboard api" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

@app.route('/api/dashboard_cards', methods=['GET'])
@cross_origin(supports_credentials=True)
def dashboard_cards():
    try:
        connect.loginfo('edge_dashboard api is called')
        connect.loginfo('edge_dashboard api is called ' +str(request.headers.get('entity-location')))
        response = {}
        date = request.args.get('date')
        if not date:
            date = datetime.now().date()
        else:
            date = datetime.strptime(date, "%Y-%m-%d").date()

        entity_location = json.loads(request.headers.get('entity-location'))
        connect.loginfo('edge_dashboard api is called ' + str(entity_location))
        _entity = list(entity_location.keys())[0]
        _location = entity_location[_entity]['locations'][0]
        result = cards_data(connect, _entity, _location, date)
        response['cards'] = result
        return jsonify(response)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in edge_dashboard api" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')

@app.route('/api/latest_events', methods=['GET'])
@cross_origin(supports_credentials=True)
def latest_events():
    try:
        connect.loginfo('latest_events api is called')
        response = {}
        entity_location = json.loads(request.headers.get('entity-location'))
        connect.loginfo('edge_dashboard api is called ' + str(entity_location))
        _entity = list(entity_location.keys())[0]
        _location = entity_location[_entity]['locations'][0]
        result = latest_events_data(connect, _entity, _location)
        return jsonify(result)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in global_dashboard api" + str(e) + ' ' + str(exc_tb.tb_lineno), level='error')


# app.run(host="localhost", port=8080)

#
# @app.route('/api/video_feed')
# @cross_origin(supports_credentials=True)
# def video_feed():
#     connect.loginfo('video feed  api is called')
#     camera_name = request.args.get('camera_name')
#     connect.loginfo("Entry " + camera_name, level='debug')
#     filter_params = {'name': camera_name}
#     connect.loginfo('querying database using filter {}'.format(filter_params), level='debug')
#     obj = async_data_process.select(table=Camera, filter_params=filter_params, get_first_row=True)
#     connect.loginfo('querying database using filter {} successful'.format(filter_params), level='debug')
#     _data = {'userid': request.headers.get('user-id'),
#              'ip': obj.ip,
#              'camera_name': obj.name}
#     userid = _data.get('userid')
#     camera_name = _data.get('camera_name')
#     try:
#         connect.loginfo('getting frames')
#         connect.loginfo('trying to make a socket connection')
#         video_stream = VideoStream(connect.config_json, camera_name, connect)
#         connect.loginfo('Checking if client connection exists already')
#         if video_stream.hpcl_client:
#             connect.loginfo('client connection exists')
#             try:
#                 connect.loginfo('closing the client connection')
#                 video_stream.hpcl_client.close()
#                 connect.loginfo('client connection closed')
#             except Exception as e_:
#                 connect.loginfo('Exception:{}'.format(e_), level='error')
#                 pass
#             video_stream.hpcl_client = None
#         connect.loginfo('initiating new socket connection')
#         video_stream.hpcl_client = video_stream.initiate_socket()
#         connect.loginfo('new socket connection established')
#         video_stream.hpcl_client.send(video_stream.camera_name.encode())
#         message = video_stream.hpcl_client.recv(5 * 1024 * 1024)
#         if b'ok' in message:
#             # frame = video_stream.gen_frames()
#             connect.loginfo('getting frames from camera {}'.format(camera_name))
#             return Response(video_stream.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#         else:
#             connect.loginfo('failed to create socket connection')
#             task_result = {"user_id": userid, "name": "Failed to create socket connection", "status": "Failed"}
#             task_result = json.dumps(task_result)
#             return task_result
#     except Exception as e_:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         connect.loginfo("exception in video_feed_background " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')
#
