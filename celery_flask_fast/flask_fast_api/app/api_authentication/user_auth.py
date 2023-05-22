import json
import logging
import os
from functools import wraps
from flask import request
from base64 import b64decode, b64encode
from rsa import PublicKey, encrypt, PrivateKey, decrypt
from flask import Response
import sys

from api_connectivity.utility import Utility
from configuration import constants

connect = Utility(configuration=constants.user_utility_configuration)


class SecurePassword:
    def encrypt_password(self, password):
        public_key = b'-----BEGIN RSA PUBLIC KEY-----\nMEgCQQCKmaKWnYgHjkAQS8A05WxBX0hvguU82L9BVyUpdDOtiTgdRURLHT/MbQlQ\nZOMRv1OO+jwnNzs7kHMU03pLKdwFAgMBAAE=\n-----END RSA PUBLIC KEY-----\n'
        public_key = PublicKey.load_pkcs1(public_key)
        encrypted_password = encrypt(password.encode(), public_key)
        return b64encode(encrypted_password).decode()

    def decrypt_password(self, encrypted_password):
        # Please add this in config json
        # "private_key_for_secure_password": "-----BEGIN RSA PRIVATE KEY-----\\nMIIBPAIBAAJBAIqZopadiAeOQBBLwDTlbEFfSG+C5TzYv0FXJSl0M62JOB1FREsd\\nP8xtCVBk4xG/U476PCc3OzuQcxTTeksp3AUCAwEAAQJAZd6gIwWsGqmSKqgSoI5T\\nsATBb7yMktlYUUUk+j/+vTSP5g5V21owvU1Ay+GvhptONJ+4FDwwKWJ/ll9MqFGf\\nLQIjAMdXm0zpGBqpp5VKVhUFO15PoHLc72ZZ4EqbWYYGFFXek48CHwCx/luNiOa9\\nxmKWcliL69leV3vdD5JRAtPvfymCPSsCIwDEpCYdq37MpnkbKvZZzAxxj2j+hfVe\\n6N/5mN+p9wtOXb7/Ah5c89l5+4GMn7rCmKp3P86/fu5Xjpc5qUFmtEDIHAsCIgj4\\n44LdTfoXYmG5lSvPCrWl0xw6Yz5JQew8AMmer7VDiBQ=\\n-----END RSA PRIVATE KEY-----\\n",
        private_key = connect.config_json.get("private_key_for_secure_password").encode()
        private_key = PrivateKey.load_pkcs1(private_key)
        decrypted_message = decrypt(b64decode(encrypted_password.encode()), private_key).decode()
        return decrypted_message


secure_password = SecurePassword()


def user_login_auth(data, async_data_process, UserProfile, UserSession, master_data_obj, master_data, RolePermissions, main_connect):
    """ function to check and verify the user name nad password and in result send the user details response"""
    if data.get("user") is None or data.get("password") is None:
        response = "Please enter username or password", 404
        main_connect.loginfo("2. Some field is left empty", level='info')
        return response
    else:
        username = data.get("user")
        password = data.get("password")
        try:
            filter_params = {
                'login_name': username
            }
            User = async_data_process.select(table=UserProfile, filter_params=filter_params, get_first_row=True, get_distinct_rows=False, retry_count=1)
            if User is not None:
                decrypted_password = secure_password.decrypt_password(encrypted_password=User.password)
                if password == str(decrypted_password):
                    main_connect.loginfo("2. User data {data} is verified".format(data=str(data)), level='info')
                    main_connect.loginfo("3. Fetching the role from roles permission table", level='info')
                    permission = async_data_process.select(table=RolePermissions, filter_params={'id': User.role_id}, get_first_row=True)
                    main_connect.loginfo("4. Fetching data from master data", level='info')
                    master_entity_location = master_data["entity_product_cam"]
                    entity_location = {}
                    for entity in master_entity_location:
                        if entity not in entity_location:
                            entity_location[entity] = {'locations': []}
                        entity_location[entity]['locations'] = list(master_entity_location[entity]['locations'].keys())
                    if User.entity_id is None:
                        user_entities = entity_location
                    else:
                        _entity = master_data_obj.mapper.get('entity_mapper').get(str(User.entity_id))
                        if User.location_id is None:
                            user_entities = {
                                str(_entity): {'locations': entity_location[str(_entity)]['locations']}}
                        else:
                            location = str(master_data_obj.mapper.get(_entity).get('location_mapper').get(str(User.location_id)))
                            user_entities = {str(_entity): {'locations': [location]}}
                    response = {"user_id": str(User.id),
                                "full_name": str(User.full_name),
                                "employee_id": str(User.employee_id),
                                "gender": str(User.gender),
                                "mobile": str(User.mobile),
                                "email": str(User.email),
                                "login_name": str(User.login_name),
                                "user_entity_location": json.dumps(user_entities),
                                "status": str(User.status),
                                "role": permission.role_name,
                                "key": b64encode(os.urandom(16)).decode('utf-8'),
                                "permissions": permission.access_rules}
                    insert_params = {'user_id': response['user_id'],
                                     'session_key': response['key']}
                    main_connect.loginfo("5. Inseting the user session in user session table", level='info')
                    async_data_process.insert(table=UserSession, insert_params=insert_params)
                    main_connect.loginfo("6. Saving the key user id and session in redis", level='info')
                    redis_login_data = connect.master_redis.get_val(key="login_data_{}".format(str(User.id)))
                    if redis_login_data:
                        redis_login_data = json.loads(redis_login_data)
                        redis_login_data['session_key'].append(response['key'])
                        connect.master_redis.set_val(key="login_data_{}".format(str(User.id)), val=json.dumps(redis_login_data))

                    else:
                        redis_login_data = {'user_id': str(User.id), 'session_key': [response['key']]}
                        connect.master_redis.set_val(key="login_data_{}".format(str(User.id)), val=json.dumps(redis_login_data))
                    return response
                else:
                    main_connect.loginfo("2. Password is wrong  {data}".format(str(data)), level='info')
                    response = "password is wrong ", 404
                    return response
            else:
                main_connect.loginfo("2. user {username} not found".format(username=username), level='info')
                response = "user not found", 404
                return response
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            main_connect.loginfo("#. Found exception when tries to login   by the data " + str(e) + str(data) + str(exc_tb.tb_lineno), level='error')
            response = "Exception in user_login api", 404
            return response

def user_login_auth_new(data, async_data_process, UserProfile, UserSession, master_data_obj, master_data, RolePermissions, main_connect):
    """ function to check and verify the user name nad password and in result send the user details response"""
    if data.get("user") is None or data.get("password") is None:
        response = "Please enter username or password", 404
        main_connect.loginfo("2. Some field is left empty", level='info')
        return response
    else:
        username = data.get("user")
        password = data.get("password")
        try:
            filter_params = {
                'login_name': username
            }
            User = async_data_process.select(table=UserProfile, filter_params=filter_params, get_first_row=True, get_distinct_rows=False, retry_count=1)
            if User is not None:
                decrypted_password = secure_password.decrypt_password(encrypted_password=User.password)
                if password == str(decrypted_password):
                    main_connect.loginfo("2. User data {username} is verified".format(username=str(username)), level='info')
                    main_connect.loginfo("3. Fetching the role from roles permission table", level='info')
                    permission = async_data_process.select(table=RolePermissions, filter_params={'id': User.role_id}, get_first_row=True)
                    main_connect.loginfo("4. Fetching data from master data", level='info')
                    master_entity_location = master_data["entity_product_cam"]
                    entity_location = {}
                    for entity in master_entity_location:
                        if entity not in entity_location:
                            entity_location[entity] = {'locations': []}
                        entity_location[entity]['locations'] = list(master_entity_location[entity]['locations'].keys())
                    if User.entity_id is None:
                        user_entities = entity_location
                    else:
                        _entity = master_data_obj.mapper.get('entity_mapper').get(str(User.entity_id))
                        if User.location_id is None:
                            user_entities = {
                                str(_entity): {'locations': entity_location[str(_entity)]['locations']}}
                        else:
                            location = str(master_data_obj.mapper.get(_entity).get('location_mapper').get(str(User.location_id)))
                            user_entities = {str(_entity): {'locations': [location]}}
                    response = {"user_id": str(User.id),
                                "full_name": str(User.full_name),
                                "employee_id": str(User.employee_id),
                                "gender": str(User.gender),
                                "mobile": str(User.mobile),
                                "email": str(User.email),
                                "login_name": str(User.login_name),
                                "user_entity_location": json.dumps(user_entities),
                                "status": str(User.status),
                                "role": permission.role_name,
                                "key": b64encode(os.urandom(16)).decode('utf-8'),
                                "permissions": permission.access_rules}
                    insert_params = {'user_id': response['user_id'],
                                     'session_key': response['key']}
                    main_connect.loginfo("5. Inseting the user session in user session table", level='info')
                    async_data_process.insert(table=UserSession, insert_params=insert_params)
                    main_connect.loginfo("6. Saving the key user id and session in redis", level='info')
                    redis_login_data = connect.master_redis.get_val(key="login_data_{}".format(str(User.id)))
                    if redis_login_data:
                        redis_login_data = json.loads(redis_login_data)
                        redis_login_data['session_key'].append(response['key'])
                        connect.master_redis.set_val(key="login_data_{}".format(str(User.id)), val=json.dumps(redis_login_data))

                    else:
                        redis_login_data = {'user_id': str(User.id), 'session_key': [response['key']]}
                        connect.master_redis.set_val(key="login_data_{}".format(str(User.id)), val=json.dumps(redis_login_data))
                    return response
                else:
                    main_connect.loginfo("2. Password is wrong {username}".format(username=str(username)), level='info')
                    response = -1
                    return response
            else:
                main_connect.loginfo("2. user {username} not found".format(username=username), level='info')
                return -2
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            main_connect.loginfo("#. Found exception when tries to login   by the data " + str(e) + str(data) + str(exc_tb.tb_lineno), level='error')
            response = "Exception in user_login api", 404
            return response



def user_logout_auth(key, async_data_process, UserSession, user_id, main_connect):
    """User to log out user by accessing the headers ie  header['key'] and header['user-id']"""
    try:
        filter_params = {'session_key': key}
        main_connect.loginfo("2. Deleting the session from table", level='info')
        async_data_process.delete(table=UserSession, filter_params=filter_params)
        main_connect.loginfo("3. Clearing the user id and session key from redis", level='info')
        redis_login_data = connect.master_redis.get_val(key="login_data_{}".format(str(user_id)))
        if redis_login_data:
            redis_login_data = json.loads(redis_login_data)
            redis_login_data['session_key'].remove(key)
            connect.master_redis.set_val(key="login_data_{}".format(str(user_id)), val=json.dumps(redis_login_data))
        response = "logged out successfully"
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        main_connect.loginfo("#. Found exception when tries to logout" + str(e) + str(exc_tb.tb_lineno), level='error')
        response = "Exception in user_logout api", 404
        return response


def login_required(f):
    """Decorator to check whether the user is already logged in or not by using the headers """

    @wraps(f)
    def wrap(*args, **kwargs):
        user_id = request.headers.get('user-id')
        key = request.headers.get('key')
        connect.loginfo("checking whether uses is logged in or not ", level='debug')
        if (user_id and user_id.strip() != '') and (key and key.strip() != ''):
            connect.loginfo("checking in redis", level='debug')
            redis_login_data = connect.master_redis.get_val(key="login_data_{}".format(str(user_id)))
            connect.loginfo("checking the user data in redis ", level='debug')
            if redis_login_data:
                connect.loginfo("user data is there", level='debug')
                redis_login_data = json.loads(redis_login_data)
                connect.loginfo("checking the session key in redis", level='debug')
                if key in redis_login_data['session_key']:
                    connect.loginfo("key is there", level='debug')
                    return f(*args, **kwargs)
                else:
                    connect.loginfo("session key is not in the redis", level='debug')
                    return Response({"Not a valid session key or may be time expired please login again": "Not a valid session key or may be time expired please login again"})
            else:
                connect.loginfo("user data is not in redis", level='debug')
                return Response({"please login again": "please login with correct username and password"})
        else:
            connect.loginfo("no data is entered")
            return Response({"login first": "login first"})

    return wrap
