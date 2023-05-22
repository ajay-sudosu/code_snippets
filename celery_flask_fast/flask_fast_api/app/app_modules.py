from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.middleware.proxy_fix import ProxyFix
from azure.storage.blob import ContainerClient
from sqlalchemy import create_engine, and_
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from dictalchemy import DictableModel
from flask_login import LoginManager
from collections import defaultdict
from flask_login import UserMixin
from flask_session import Session
from flask import Flask, session
from sqlalchemy.sql import case
from time import sleep
from PIL import Image
import pandas as pd
import numpy as np
import zipfile
import logging
import socket
import struct
import pickle
import redis
import msal
import json
import cv2
import sys
import os
import io
import copy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from configuration import app_config


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


config = json.loads(open(os.path.join(BASE_DIR, "configuration/config.json")).read())
config = {"config": config[config['env']]}
config = Struct(**config)


def db_connection():
    engine = create_engine(config.config.get('database_uri'), pool_pre_ping=True, pool_size=200, max_overflow=0, connect_args={'connect_timeout': 10})
    Session_db = scoped_session(sessionmaker(engine))
    return engine, Session_db


engine, Session_db = db_connection()


class Rabbitmq:
    def publish(event, utility):
        try:
            try:
                utility.publisher_channel.basic_publish(exchange=utility.rabbitmq_publisher.get('exchange'), routing_key=utility.rabbitmq_publisher.get('routing_key'), body=json.dumps(event))
                utility.loginfo("published : " + str(event) + "with routingkey " + utility.rabbitmq_publisher.get('routing_key'))
            except Exception as e:
                try:
                    utility.publisher_channel.close()
                except:
                    pass
                utility.loginfo("exception >> " + str(e))
                utility.get_rabbitmq_publisher(utility.rabbitmq_publisher.get('exchange'))
                try:
                    utility.publisher_channel.basic_publish(exchange=utility.rabbitmq_publisher.get('exchange'), routing_key=utility.rabbitmq_publisher.get('routing_key'), body=json.dumps(event))
                    utility.loginfo("published>>" + str(event) + "with routingkey " + utility.rabbitmq_publisher.get('routing_key'))
                except Exception as e:
                    utility.loginfo("except in inner publish : " + str(e))
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            utility.loginfo("except in publish " + str(e_) + ' ' + str(exc_tb.tb_lineno))


class InitializeApp:
    CONFIG = json.loads(open(os.path.join(BASE_DIR, 'configuration/config.json')).read())
    ENVIRONMENT = CONFIG.get('env', 'dev')
    CONFIG = CONFIG.get(ENVIRONMENT)
    DEBUG = CONFIG.get('debug')

    @classmethod
    def initialize_app(cls):
        app_ = Flask(__name__)
        app_.secret_key = os.urandom(16)
        app_.config.update(cls.CONFIG)
        app_.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)
        app_.config.from_object(app_config)
        app_.wsgi_app = ProxyFix(app_.wsgi_app, x_proto=1, x_host=1)
        cls.initialize_directoy(app_)

        redis_ = redis.Redis(host='127.0.0.1')

        login_manager = LoginManager()
        login_manager.init_app(app_)
        login_manager.login_view = "/api/user_login"
        login_manager.login_message = u"please login"

        database = SQLAlchemy(app_)
        app_.config['SESSION_SQLALCHEMY'] = database
        user_session = Session(app_)
        user_session.app.session_interface.db.create_all()
        return app_, redis_, login_manager

    @classmethod
    def initialize_directoy(cls, app):
        for directory in [app.config.get('video_location_to_resume'), app.config.get('chunk_location_to_resume'), app.config.get('static_path'), app.config.get('video_location'), app.config.get('annotation_location'), app.config.get('chunk_location_to_rabbitmq'), app.config.get('video_zip_path')]:
            if not os.path.exists(directory):
                os.makedirs(directory)


class RedisData:
    def __init__(self, connect):
        self.upload_status = connect.master_redis.get_val(key='upload_status')
        if not self.upload_status:
            self.upload_status = {}
        else:
            self.upload_status = json.loads(self.upload_status)


class Event_data:
    def event_fetch_data(self, connect, date):
        try:
            connect.loginfo("************* starttime = " + datetime.now().isoformat())
            sql = "SELECT A.event_id, A.camera_ip, A.camera_id, A.category_id, A.category_name, A.severity_id, A.severity_name, A.feature_id, A.feature_name, A.feature_alias_name, A.image_end_point, A.start_datetime, A.end_datetime, A.event_json, A.confusion_matrix, A.user_ack, B.camera_name, B.area_id, B.area_name, B.location_id, B.location_name, B.entity_id, B.entity_name, B.product_id, B.product_name FROM event_data A left join master_data B on A.camera_id = B.camera_id where date(start_datetime) = '{date}' order by start_datetime desc".format(date=date)
            events = pd.read_sql(sql, engine)
            # df['date'] = df['start_datetime'].apply(lambda x: x.date())
            # events = df[df['date'] == todays_date]
            events = events[events['event_json'].notnull()]
            # events = events.sort_values('start_datetime',ascending=False)
            df_cat = events.groupby("category_name").size()
            df_area = events.groupby("area_name").size()
            df_severity = events.groupby("severity_name").size()
            df_category_area = events.groupby(["category_name", "area_name"]).size()
            df_category_severity = events.groupby(["category_name", "severity_name"]).size()
            df_area_category = events.groupby(["area_name", "category_name"]).size()
            df_area_severity = events.groupby(["area_name", "severity_name"]).size()
            df_severity_category = events.groupby(["severity_name", "category_name"]).size()
            df_severity_area = events.groupby(["severity_name", "area_name"]).size()

            pie_chart = {'category': {}, "area": {}, "severity": {}}
            for cat in events['category_name'].unique():
                pie_chart['category'][cat] = {
                    "data_1": [{"name": k, "value": v} for k, v in df_category_area[cat].to_dict().items()],
                    "data_2": [{"name": k, "value": v} for k, v in df_category_severity[cat].to_dict().items()]}

            for area in events['area_name'].unique():
                pie_chart['area'][area] = {
                    "data_1": [{"name": k, "value": v} for k, v in df_area_category[area].to_dict().items()],
                    "data_2": [{"name": k, "value": v} for k, v in df_area_severity[area].to_dict().items()]}

            for sev in events['severity_name'].unique():
                pie_chart['severity'][sev] = {
                    "data_1": [{"name": k, "value": v} for k, v in df_severity_category[sev].to_dict().items()],
                    "data_2": [{"name": k, "value": v} for k, v in df_severity_area[sev].to_dict().items()]}

            tabular_data_1 = [{
                "id": int(row['event_id']),
                "image": row['image_end_point'],
                "date": str(row['end_datetime']),
                "area": row['area_name'],
                "Camera": row['camera_ip'],
                "event_type": row['feature_alias_name'],
                "event_disc": "",
                "confusion_matrix": row['confusion_matrix'],
                "user_ack": row['user_ack']
            } for index, row in events.iterrows()]

            response = {'dashboard':
                            {"summary-cards": [{"name": "Category",
                                                "data": {key: value for key, value in df_cat.to_dict().items()}
                                                },
                                               {'name': 'Area',
                                                'data': {key: value for key, value in df_area.to_dict().items()}
                                                },
                                               {'name': 'Severity',
                                                'data': {key: value for key, value in df_severity.to_dict().items()}
                                                },
                                               # {'name': 'Unloaded Cylinders',
                                               #  'data': {}
                                               # },
                                               # {'name': 'Loaded Cylinders',
                                               #  'data': {}
                                               # },
                                               # {'name': 'Defect Cylinders',
                                               #  'data': {}
                                               # }
                                               ],
                             'category': {'chart': {'type': 'pie', 'data': pie_chart['category']}, 'table': []},
                             'area': {'chart': {'type': 'pie', 'data': pie_chart['area']}, 'table': []},
                             'severity': {'chart': {'type': 'pie', 'data': pie_chart['severity']}, 'table': []},
                             # 'unloaded cylinders': {'chart': {'type': 'bar', 'data': {'tittle': 'unloaded cylinders', 'yaxis': 'Count', 'xaxis': 'Truck', 'name': [], 'data': []}}, 'table': []},
                             # 'loaded cylinders': {'chart': {'type': 'bar', 'data': {'tittle': 'loaded cylinders', 'yaxis': 'Count', 'xaxis': 'Truck', 'name': [], 'data': []}}, 'table': []},
                             # 'defect cylinders': {'chart': {'type': 'bar', 'data': {'tittle': 'defect cylinders', 'yaxis': 'Count', 'xaxis': 'Truck', 'name': [], 'data': []}}, 'table': []},
                             'table': tabular_data_1
                             }}
            connect.loginfo("************* endtime = " + datetime.now().isoformat())
            return response

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            connect.loginfo("Exception in fetch_event_data " + str(e) + ' ' + str(exc_tb.tb_lineno))
        #     df = df[df['event_json'].notnull()]
        #     df_cat = df.groupby("category_name").size()
        #     df_area = df.groupby("area_name").size()
        #     df_severity = df.groupby("severity").size()
        #     df_category_area = df.groupby(["category_name", "area_name"]).size()
        #     df_category_severity = df.groupby(["category_name", "severity"]).size()
        #     df_area_category = df.groupby(["area_name", "category_name"]).size()
        #     df_area_severity = df.groupby(["area_name", "severity"]).size()
        #     df_severity_category = df.groupby(["severity", "category_name"]).size()
        #     df_severity_area = df.groupby(["severity", "area_name"]).size()
        #
        #     pie_chart = {'category': {}, "area": {}, "severity": {}}
        #     for cat in df['category_name'].unique():
        #         pie_chart['category'][cat] = {"data_1": [{"name": k, "value": v} for k, v in df_category_area[cat].to_dict().items()], "data_2": [{"name": k, "value": v} for k, v in df_category_severity[cat].to_dict().items()]}
        #
        #     for area in df['area_name'].unique():
        #         pie_chart['area'][area] = {"data_1": [{"name": k, "value": v} for k, v in df_area_category[area].to_dict().items()], "data_2": [{"name": k, "value": v} for k, v in df_area_severity[area].to_dict().items()]}
        #
        #     for sev in df['severity'].unique():
        #         pie_chart['severity'][sev] = {"data_1": [{"name": k, "value": v} for k, v in df_severity_category[sev].to_dict().items()], "data_2": [{"name": k, "value": v} for k, v in df_severity_area[sev].to_dict().items()]}
        #
        #     tabular_data_1 = [{
        #         "id": int(row['event_id']),
        #         "image": row['image_end_point'],
        #         "date": str(row['end_datetime']),
        #         "area": row['area_name'],
        #         "Camera": row['camera_ip'],
        #         "event_type": row['feature_name'],
        #         "event_disc": ""
        #     } for index, row in df.iterrows()]
        #
        #     response = {'dashboard': {"summary-cards": [{
        #         "name": "Category",
        #         "data": {key: value for key, value in df_cat.to_dict().items()}
        #     },
        #         {
        #             'name': 'Area',
        #             'data': {key: value for key, value in df_area.to_dict().items()}
        #         },
        #         {
        #             'name': 'Severity',
        #             'data': {key: value for key, value in df_severity.to_dict().items()}
        #         }
        #         # {
        #         #     'name': 'Unloaded Cylinders',
        #         #     'data': {}
        #         # },
        #         # {
        #         #     'name': 'Loaded Cylinders',
        #         #     'data': {}
        #         # },
        #         # {
        #         #     'name': 'Defect Cylinders',
        #         #     'data': {}
        #         # }
        #     ],
        #         'category': {'chart': {'type': 'pie', 'data': pie_chart['category']}, 'table': tabular_data_1},
        #         'area': {'chart': {'type': 'pie', 'data': pie_chart['area']}, 'table': tabular_data_1},
        #         'severity': {'chart': {'type': 'pie', 'data': pie_chart['severity']}, 'table': tabular_data_1},
        #         # 'unloaded cylinders': {'chart': {'type': 'bar', 'data': {'tittle': 'unloaded cylinders', 'yaxis': 'Count', 'xaxis': 'Truck', 'name': [], 'data': []}}, 'table': []},
        #         # 'loaded cylinders': {'chart': {'type': 'bar', 'data': {'tittle': 'loaded cylinders', 'yaxis': 'Count', 'xaxis': 'Truck', 'name': [], 'data': []}}, 'table': []},
        #         # 'defect cylinders': {'chart': {'type': 'bar', 'data': {'tittle': 'defect cylinders', 'yaxis': 'Count', 'xaxis': 'Truck', 'name': [], 'data': []}}, 'table': []}
        #     }}
        #     connect.loginfo("************* endtime = " + datetime.now().isoformat())
        #     return response
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     print("Exception in fetch_event_data " + str(e) + ' ' + str(exc_tb.tb_lineno))



def latest_events_data(connect, _entity, _location):
    try:
        entity_id = int(master_data_obj.mapper.get('entity_mapper').get(_entity))
        location_id = int(master_data_obj.mapper.get(_entity).get('location_mapper').get(_location))
        events = connect.query_database_df("SELECT area_name, feature_name, start_datetime, severity_name, category_name FROM event_data where event_id in (select max(event_id) from event_data where entity_id = {entity_id} and location_id = {location_id} group by area_name)".format(entity_id=entity_id, location_id=location_id))
        events = events.set_index('area_name').T.to_dict()
        return events
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in cards_data " + str(e_) + ' ' + str(exc_tb.tb_lineno))

def cards_data(connect, _entity, _location, date):
    try:
        entity_id = int(master_data_obj.mapper.get('entity_mapper').get(_entity))
        location_id = int(master_data_obj.mapper.get(_entity).get('location_mapper').get(_location))
        cameras = connect.query_database_df('SELECT * FROM master_data where entity_id = {entity_id} and location_id = {location_id}'.format(entity_id=entity_id,
                                                                                                                               location_id=location_id))
        cameras['count'] = [1 for i in range(cameras.shape[0])]
        cameras['camera_health'] = cameras['camera_health'].apply(
            lambda x: 'failed' if str(x).lower() in ['nan', 'none'] else x)
        cameras['camera_health'] = cameras['camera_health'].apply(
            lambda x: 'active' if str(x).lower() in ['active', 'Active'] else x)
        camera_pivot = pd.pivot_table(cameras, index=['area_name', 'camera_health'], values='count',
                                      aggfunc=np.sum).reset_index()
        health_list = list(cameras['camera_health'].unique())
        total_cameras = int(cameras['count'].sum())
        total_active = int(camera_pivot[camera_pivot['camera_health'] == 'active']['count'].sum())
        total_inactive = int(camera_pivot[camera_pivot['camera_health'] == 'failed']['count'].sum())
        areas = list(cameras['area_name'].unique())
        area_active = camera_pivot[camera_pivot['camera_health'] == 'active']
        if area_active.shape[0] != 0:
            area_active_dict = dict(zip(area_active['area_name'], area_active['count']))
        else:
            area_active_dict = {}
        area_inactive = camera_pivot[camera_pivot['camera_health'] == 'failed']
        if area_inactive.shape[0] != 0:
            area_inactive_dict = dict(zip(area_inactive['area_name'], area_inactive['count']))
        else:
            area_inactive_dict = {}

        # deviation card
        # today = datetime.now().replace(microsecond=0).date().isoformat() if not date else date
        # connect.loginfo("location_id " + str(today))
        events = connect.query_database_df("SELECT * FROM event_data where entity_id = {entity_id} and location_id = '{location_id}' and date(start_datetime) = '{date}'".format(entity_id=entity_id,location_id=location_id,date=date))
        # events = connect.query_database_df("SELECT * FROM event_data where entity_id = {entity_id} and date(start_datetime) = '{date}'".format(entity_id=entity_id,date=date))
        hours_list = [hour for hour in range(24)]
        if events.shape[0] != 0:
            events['count'] = events['start_datetime'].apply(lambda x: 1)
            total_deviations = int(events['count'].sum())
            category_pivot = pd.pivot_table(events, index=['category_name'], values='count',
                                            aggfunc=np.sum).reset_index()
            severity_pivot = pd.pivot_table(events, index=['severity_name'], values='count',
                                            aggfunc=np.sum).reset_index()
            severity_list = list(severity_pivot['severity_name'].unique())
            low_impact = int(severity_pivot[severity_pivot['severity_name'] == 'Low Impact']['count']) if 'Low Impact' in severity_list else 0
            high_impact = int(severity_pivot[severity_pivot['severity_name'] == 'High Impact']['count']) if 'High Impact' in severity_list else 0
            significant_impact = int(severity_pivot[severity_pivot['severity_name'] == 'Significant Impact']['count']) if 'Significant Impact' in severity_list else 0
            # for bar graph1
            category_sql = "select name from m_feature_category where entity_id={entity_id} and ".format(entity_id=entity_id)
            category_ = connect.query_database_df(sql=category_sql)
            category_list = list(category_['name'].unique())
            category_dict = dict(zip(category_pivot['category_name'], category_pivot['count']))

            # for bar graph2
            areas_list = list(events['area_name'].unique())
            area_deviation_pivot = pd.pivot_table(events, index=['area_name', 'severity_name'], values='count',
                                                  aggfunc=np.sum).reset_index()
            low_pivot = area_deviation_pivot[area_deviation_pivot['severity_name'] == 'Low Impact']
            low_impact_dict = dict(zip(low_pivot['area_name'], low_pivot['count']))
            high_pivot = area_deviation_pivot[area_deviation_pivot['severity_name'] == 'High Impact']
            high_impact_dict = dict(zip(high_pivot['area_name'], high_pivot['count']))
            significant_pivot = area_deviation_pivot[area_deviation_pivot['severity_name'] == 'Significant Impact']
            significant_impact_dict = dict(zip(significant_pivot['area_name'], significant_pivot['count']))

            # for line graph
            today = date
            yesterday = today - timedelta(days=1)
            events['date'] = events['start_datetime'].apply(lambda x: x.date())
            events['hour'] = events['start_datetime'].apply(lambda x: x.hour)
            today_category = events[events['date'] == today]
            yesterday_category = events[events['date'] == yesterday]
            today_category_pivot = pd.pivot_table(today_category, index=['hour'], values='count',
                                                  aggfunc=np.sum).reset_index()
            if today_category.shape[0] != 0:
                today_category_pivot_dict = dict(zip(today_category_pivot['hour'], today_category_pivot['count']))
            else:
                today_category_pivot_dict = {}
            yesterday_category_pivot = pd.pivot_table(yesterday_category, index=['hour'], values='count',
                                                      aggfunc=np.sum).reset_index()
            if yesterday_category.shape[0] != 0:
                yesterday_category_pivot_dict = dict(
                    zip(yesterday_category_pivot['hour'], yesterday_category_pivot['count']))
            else:
                yesterday_category_pivot_dict = {}
            current_hour = datetime.now().hour
            total_events_yesterday = 0
            total_events_today = 0
            for hour in range(0, current_hour + 1):
                if hour in today_category_pivot_dict:
                    total_events_today = total_events_today + today_category_pivot_dict[hour]
                if hour in yesterday_category_pivot_dict:
                    total_events_yesterday = total_events_yesterday + yesterday_category_pivot_dict[hour]
            if total_events_yesterday == 0:
                percent_deviation = total_events_today
            else:
                percent_events = (total_events_today / total_events_yesterday) * 100
                if total_events_yesterday - total_events_today > 0:
                    percent_deviation = 100 - percent_events

                elif total_events_yesterday - total_events_today < 0:
                    percent_deviation = percent_events

                elif total_events_yesterday - total_events_today == 0:
                    percent_deviation = 0

        else:
            category_list = areas_list = []
            category_dict = low_impact_dict = high_impact_dict = significant_impact_dict = today_category_pivot_dict = {}
            percent_deviation = total_deviations = low_impact = high_impact = significant_impact = 0

        # lpg cyclinder count card
        cyclinder_count_events = events[events['feature_name'] == 'Cylinder-Count']
        cyc_event_json_list = [eval(event['event_json']) for key, event in cyclinder_count_events.iterrows()]
        cyclinder_df = pd.DataFrame(cyc_event_json_list)
        if cyclinder_count_events.shape[0] != 0:
            cyclinder_df['count'] = cyclinder_df['cyclinder_type'].apply(lambda x: 1)
            cyclinder_df['datetime'] = cyclinder_df['datetime'].apply(lambda x: datetime.fromisoformat(x))
            cyc_entry_df = cyclinder_df[cyclinder_df['type'] == 'Entry']
            cyc_exit_df = cyclinder_df[cyclinder_df['type'] == 'Exit']
            cyc_entry_df['entry_time'] = cyc_entry_df['datetime'].apply(lambda x: x.time().replace(microsecond=0))
            cyc_exit_df['exit_time'] = cyc_exit_df['datetime'].apply(lambda x: x.time().replace(microsecond=0))
            cyc_merge_df = cyc_entry_df.merge(cyc_exit_df, on='truckNumber', how='outer')
            loaded_cyc = int(cyc_merge_df['Loading_x'].sum())
            unloaded_cyc = int(cyc_merge_df['Unloading_y'].sum())
            total_cyc = loaded_cyc + unloaded_cyc
            cyclinder_type = list(cyclinder_df['cyclinder_type'].unique())
            cyc_type_dict = pd.pivot_table(cyclinder_df, index=['cyclinder_type'], values='count',
                                           aggfunc=np.sum).to_dict()

            # loaded_cyc = int(cyclinder_df['Loading'].sum())
            # unloaded_cyc = int(cyclinder_df['Unloading'].sum())
            # total_cyc = loaded_cyc+unloaded_cyc
            # cyclinder_type = list(cyclinder_df['cyclinder_type'].unique())
            # cyc_type_dict = pd.pivot_table(cyclinder_df, index=['cyclinder_type'], values='count',aggfunc=np.sum).to_dict()

        else:
            loaded_cyc = unloaded_cyc = total_cyc = 0
            cyc_type_dict = {}
            cyclinder_type = []
            cyc_merge_df = cyclinder_df

        # cyclinder defect card
        cyclinder_defects_events = events[events['feature_name'] == 'Cylinder-Defect']
        defects_event_json_list = [eval(event['event_json']) for key, event in cyclinder_defects_events.iterrows()]
        cyclinder_defects_df = pd.DataFrame(defects_event_json_list)
        if cyclinder_defects_events.shape[0] != 0:
            cyclinder_defects_df['count'] = cyclinder_defects_df['defectType'].apply(lambda x: 1)
            defect_types = list(cyclinder_defects_df['defectType'].unique())
            defect_pivot = pd.pivot_table(cyclinder_defects_df, index=['defectType'], values='count', aggfunc=np.sum)
            total_defects = int(cyclinder_defects_df['count'].sum())
            maxDefects = int(defect_pivot['count'].max())
            minDefects = int(defect_pivot['count'].min())
            defect_dict = defect_pivot.to_dict()
        else:
            total_defects = maxDefects = minDefects = 0
            defect_types = []
            defect_dict = {}

        # conveyer belt defects
        conveyer_defects = events[events['feature_name'] == 'Conveyor_Belt_Defects']
        conveyer_event_json_list = [eval(event['event_json']) for key, event in conveyer_defects.iterrows()]
        conveyer_df = pd.DataFrame(conveyer_event_json_list)
        if conveyer_defects.shape[0] != 0:
            conveyer_df['count'] = conveyer_df['defectType'].apply(lambda x: 1)
            total_conveyer_defects = conveyer_df.shape[0]
            conveyer_defects_type_list = list(conveyer_df['defectType'].unique())
            conveyer_defects_pivot = pd.pivot_table(conveyer_df, index=['defectType', 'severity'], values='count',
                                                    aggfunc=np.sum).reset_index().set_index('defectType')
            defect_type_dict = {}
            for defecttype, value in conveyer_defects_pivot.iterrows():
                defect_type_dict[defecttype] = {value.values[0]: value.values[1]}
            critical_defects = conveyer_defects_pivot[conveyer_defects_pivot['severity'] == 'critical']['count'].sum()
            non_critical_defects = conveyer_defects_pivot[conveyer_defects_pivot['severity'] == 'non-critical'][
                'count'].sum()
            critical_defects_percentage = round((int(critical_defects) / int(total_conveyer_defects)) * 100)
        else:
            conveyer_defects_type_list = []
            defect_type_dict = {}
            total_conveyer_defects = critical_defects = non_critical_defects = critical_defects_percentage = 0

        # truck movement card
        anpr_events = events[events['feature_name'] == 'Anpr']
        anpr_event_json_list = [eval(event['event_json']) for key, event in anpr_events.iterrows()]
        anpr_df = pd.DataFrame(anpr_event_json_list)
        if anpr_events.shape[0] != 0:
            anpr_df['count'] = anpr_df['Type'].apply(lambda x: 1)
            anpr_df['datetime'] = anpr_df['datetime'].apply(lambda x: datetime.fromisoformat(x))
            anpr_df['hour'] = anpr_df['datetime'].apply(lambda x: x.hour)
            entry_df = anpr_df[anpr_df['Type'] == 'Entry']
            exit_df = anpr_df[anpr_df['Type'] == 'Exit']
            entry_pivot = pd.pivot_table(entry_df, index=['hour'], values='count', aggfunc=np.sum).reset_index()
            trucks_entry_hourly_dict = dict(zip(entry_pivot['hour'], entry_pivot['count']))
            entry_df['entry_time'] = entry_df['datetime'].apply(lambda x: x.time().replace(microsecond=0))
            exit_df['exit_time'] = exit_df['datetime'].apply(lambda x: x.time().replace(microsecond=0))
            merge_df = entry_df.merge(exit_df, on='truckNumber', how='outer')
            merge_df['diff'] = pd.to_datetime(merge_df.datetime_y) - pd.to_datetime(merge_df.datetime_x)
            merge_df['seconds'] = merge_df['diff'].apply(lambda x: x.seconds)
            turnOverTime = str(timedelta(seconds=int(merge_df['seconds'].sum())))
            tt_trucks = int(merge_df[merge_df['truckType_x'] == 'TT']['count_x'].sum())
            lpg_trucks = int(merge_df[merge_df['truckType_x'] == 'LPG']['count_x'].sum())
            total_trucks = tt_trucks + lpg_trucks
            hourly_trucks_pivot = pd.pivot_table(merge_df, index=['hour_x', 'truckType_x'], values='count_x',
                                                 aggfunc=np.sum).reset_index()
            tt_truck_hourly = hourly_trucks_pivot[hourly_trucks_pivot['truckType_x'] == 'TT'].reset_index()
            tt_truck_hourly_dict = dict(zip(tt_truck_hourly['hour_x'], tt_truck_hourly['count_x']))
            lpg_truck_hourly = hourly_trucks_pivot[hourly_trucks_pivot['truckType_x'] == 'LPG'].reset_index()
            lpg_truck_hourly_dict = dict(zip(lpg_truck_hourly['hour_x'], lpg_truck_hourly['count_x']))
        else:
            tt_trucks = lpg_trucks = total_trucks = turnOverTime = 0
            tt_truck_hourly_dict = lpg_truck_hourly_dict = trucks_entry_hourly_dict = {}
            merge_df = anpr_df

        response = {"cameras": {"cardName": "Cameras",
                                "subHeader": "Analytics of overall cameras globally",
                                "expanded": False,
                                "overall": total_cameras,
                                "active": total_active,
                                "inActive": total_inactive,
                                "bottomBelt": int((total_active / total_cameras) * 100),
                                "tableSource": [{"area": value.area_name,
                                                 "ip": value.camera_ip,
                                                 "name": value.camera_name,
                                                 "model": value.camera_model,
                                                 "status": 'Inactive' if "active" not in health_list else value.camera_health}
                                                for row, value in cameras.iterrows()],
                                "barChart": {"xAxisName": "Areas",
                                             "xAxisData": areas,
                                             "yAxisName": "Name",
                                             "series": [{'name': 'Active',
                                                         'data': [{'value': int(area_active_dict.get(area, 0))} for area
                                                                  in areas]}, {'name': 'Inactive', 'data': [
                                                 {'value': int(area_inactive_dict.get(area, 0))} for area in areas]}]}},
                    "deviations": {"cardName": "Deviations",
                                   "subHeader": "Analytics of overall deviations globally",
                                   "deviationCondition": percent_deviation,
                                   "expanded": False,
                                   "overall": total_deviations,
                                   "overallCategory": int(len(category_list)),
                                   "lowImpact": low_impact,
                                   "highImpact": high_impact,
                                   "severeImpact": significant_impact,
                                   "bottomBelt": "Severity of Deviation",
                                   "tableSource": [{'event_id':value.event_id,
                                                    'image': value.image_end_point,
                                                    'area': value.area_name,
                                                    'date': value.start_datetime.date(),
                                                    'time': value.start_datetime.time().replace(
                                                        microsecond=0).isoformat(),
                                                    'ip': value.camera_ip,
                                                    'name': value.camera_name,
                                                    'useCase': value.feature_name} for row, value in events.iterrows()],
                                   "lineGraph": {"xAxisData": hours_list,
                                                 "series": [{"name": "Hours",
                                                             "data": [int(today_category_pivot_dict.get(hour, 0)) for
                                                                      hour in hours_list]}]},
                                   "donutGraph": {"series": [{"data": [{'value': round((int(category_dict.get(category,0)) / int(events.shape[0])) * 100),'name':category} for category in category_list] if category_list else [{'value': 0,'name':'No category present'}]}]},
                                   "barGraph1": {"xAxisData": category_list,
                                                 "series": [{"name": "Severity",
                                                             "data": [{'value': int(category_dict.get(category, 0))} for
                                                                      category in category_list] if category_list else [
                                                                 {'value': 0}]}]},
                                   "barGraph2": {"xAxisData": areas_list,
                                                 "series": [{"name": "Low Impact",
                                                             "data": [{'value': int(low_impact_dict.get(area, 0))} for
                                                                      area in areas_list] if areas_list else [
                                                                 {'value': 0}]},
                                                            {"name": "High Impact",
                                                             "data": [{'value': int(high_impact_dict.get(area, 0))} for
                                                                      area
                                                                      in areas_list] if areas_list else [{'value': 0}]},
                                                            {"name": "Significant Impact",
                                                             "data": [
                                                                 {'value': int(significant_impact_dict.get(area, 0))}
                                                                 for area in areas_list] if areas_list else [
                                                                 {'value': 0}]}
                                                            ]}},
                    "truck_movement": {"cardName": "Truck Movement",
                                       "subHeader": "Analytics of count and movement of trucks",
                                       "expanded": False,
                                       "overall": total_trucks,
                                       "ttTrucks": tt_trucks,
                                       "lpgTrucks": lpg_trucks,
                                       "turnOverTime": turnOverTime,
                                       "tableSource": [{"sort": value.image_x,
                                                        "area": value.area_x,
                                                        "date": value.datetime_x.date(),
                                                        "entry": value.entry_time.isoformat(),
                                                        "exit": str(0) if str(value.exit_time).lower() in ['nan',
                                                                                                           'none'] else value.exit_time.isoformat(),
                                                        "turnaround": str(0) + ' ' + 'min' if str(
                                                            value.seconds).lower() in ['nan', 'none'] else str(
                                                            int(value.seconds / 60)) + ' ' + 'min',
                                                        "type": value.Type_x,
                                                        "truckNumber": value.truckNumber} for key, value in
                                                       merge_df.iterrows()],
                                       "lineGraph": {"xAxisData": hours_list,
                                                     "series": [{"name": "Hourly Entry",
                                                                 "data": [int(trucks_entry_hourly_dict.get(hour, 0)) for
                                                                          hour in hours_list]}]},
                                       "barGraph": {"xAxisData": hours_list,
                                                    "series": [{"name": "TT", "data": [
                                                        {'value': int(tt_truck_hourly_dict.get(hour, 0))} for hour in
                                                        hours_list]},
                                                               {"name": "LPG", "data": [
                                                                   {"value": int(lpg_truck_hourly_dict.get(hour, 0))}
                                                                   for hour in hours_list]}]}},
                    "lpg_cylinder_count": {"cardName": "LPG Cylinder Count",
                                           "subHeader": "Total count of loaded/unloaded Cylinders",
                                           "expanded": False,
                                           "overall": total_cyc,
                                           "loadedCyl": loaded_cyc,
                                           "unLoadedCyl": unloaded_cyc,
                                           "tableSource": [{"sort": value.image_x,
                                                            "truckNumber": value.truckNumber,
                                                            "ip": value.camera_ip_x,
                                                            "bayEntry": value.entry_time.isoformat(),
                                                            "bayExit": value.exit_time.isoformat(),
                                                            "type": value.cyclinder_type_x,
                                                            "totalCy": 0 if str(value.Unloading_x).lower() in ['nan',
                                                                                                               'none'] else int(
                                                                value.Unloading)} for key, value in
                                                           cyc_merge_df.iterrows()],
                                           "donutGraph": {"series": [{"name": "Access From",
                                                                      "data": [{"value": loaded_cyc, "name": "Loaded"},
                                                                               {"value": unloaded_cyc,
                                                                                "name": "Unloaded"}]}]},
                                           "barGraph": {"xAxisData": cyclinder_type,
                                                        "series": [{'name': 'cyclinder_type', 'data': [
                                                            {'data': int(cyc_type_dict['count'].get(value, 0)) for value
                                                             in cyclinder_type}]}]}},
                    "defective_cylinders": {"cardName": "Defective Cylinders",
                                            "subHeader": "Analytics of overall faulty cylinders",
                                            "expanded": False,
                                            "overall": total_defects,
                                            "maxDefects": maxDefects,
                                            "minDefects": minDefects,
                                            "tableSource": [{'image': value.image,
                                                             'defectType': value.defectType,
                                                             'date': datetime.fromisoformat(value.datetime).date(),
                                                             'time': datetime.fromisoformat(
                                                                 value.datetime).time().replace(
                                                                 microsecond=0).isoformat(),
                                                             'cylinderType': value.cyclinder_type} for key, value in
                                                            cyclinder_defects_df.iterrows()],
                                            "barChart": {"xAxisData": defect_types,
                                                         "series": [{"name": "Defect Types", "data": [
                                                             {'value': int(defect_dict['count'].get(defect, 0))} for
                                                             defect in defect_types]}]}},
                    "conveyor_belt_defects": {"cardName": "Conveyer Belt Defects",
                                              "subHeader": "Analytics of overall defective CB",
                                              "expanded": False,
                                              "overall": int(total_conveyer_defects),
                                              "critical": int(critical_defects),
                                              "nonCritical": int(non_critical_defects),
                                              "bottomBelt": critical_defects_percentage,
                                              "tableSource": [{"sort": value.image,
                                                               "defectType": value.defectType,
                                                               "date": datetime.fromisoformat(value.datetime).date(),
                                                               "time": datetime.fromisoformat(
                                                                   value.datetime).time().replace(
                                                                   microsecond=0).isoformat(),
                                                               "severity": value.severity} for key, value in
                                                              conveyer_df.iterrows()],
                                              "barChart": {"xAxisData": conveyer_defects_type_list,
                                                           "series": [{"name": "Critical", "data": [{'value': int(
                                                               defect_type_dict.get(defect, 0).get('critical', 0))} for
                                                                                                    defect in
                                                                                                    conveyer_defects_type_list]},
                                                                      {"name": "Non-Critical", "data": [{'value': int(
                                                                          defect_type_dict.get(defect, 0).get(
                                                                              'non-critical', 0))} for defect in
                                                                                                        conveyer_defects_type_list]}]}}}
        return response
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        connect.loginfo("Exception in cards_data " + str(e_) + ' ' + str(exc_tb.tb_lineno))


class MasterData:
    state_mapper = {}
    state_action_mapper = {}
    camera_mapper = {}
    feature_mapper = {}
    master_data = {}
    event_mapper = {}
    class_mapper = {}
    product_entity_mapper = {}
    entity_mapper = {}
    location_mapper = {}
    user_entity_mapper = {}
    user_user_access_mapper = {}
    camera_entity_location_area_mapper = {}
    user_location_mapper = {}
    role_mapper = {}
    area_mapper = {}
    model_type_mapper = {}
    mapper = {'entity_mapper': {}}
    camera_id_mapper = {}

    def get_entity_location(self, entity_location):
        if entity_location:
            entity_location = json.loads(entity_location)
            if len(entity_location) == 0:
                entity_location = master_data.get('entity_location')
        else:
            entity_location = master_data.get('entity_location')
        return entity_location

    def master_data_(self, Session_db):
        with Session_db() as db_session:
            table_data = db_session.execute('SELECT * FROM master_data A left join rule_data B on A.camera_id = B.camera_id')
        columns = [column[0] for column in table_data.cursor.description]
        response = defaultdict(list)
        response['entity_product_cam'] = {}
        response['entity_product_id'] = {}
        response['entity_location'] = {}
        for row in table_data.fetchall():
            row_dict = dict(zip(columns, row))
            [response[column].append(row_dict[column]) for column in columns if
             row_dict[column] and row_dict[column] not in response[column]]
            response['results'].append(row_dict)
            self.camera_id_mapper[str(row['camera_id'])] = row_dict
            if row_dict['entity_name'] and row_dict['entity_name'] not in response['entity_product_cam']:
                response['entity_product_cam'][row_dict['entity_name']] = {'products': defaultdict(list),
                                                                           'locations': {}}
                response['entity_product_id'][row_dict['entity_name']] = {'products': defaultdict(list),
                                                                          'locations': {}}
                response['entity_location'][row_dict['entity_name']] = {'locations': []}
            if row_dict['feature_name'] and row_dict['product_name'] not in \
                    response['entity_product_cam'][row_dict['entity_name']]['products']:
                response['entity_product_cam'][row_dict['entity_name']]['products'][row_dict['product_name']].append(
                    row_dict['feature_name'])
                response['entity_product_id'][row_dict['entity_name']]['products'][row_dict['product_name']].append(
                    row_dict['feature_name'])
            elif row_dict['feature_name'] and row_dict['feature_name'] not in \
                    response['entity_product_cam'][row_dict['entity_name']]['products'][row_dict['product_name']]:
                response['entity_product_cam'][row_dict['entity_name']]['products'][row_dict['product_name']].append(
                    row_dict['feature_name'])
                response['entity_product_id'][row_dict['entity_name']]['products'][row_dict['product_name']].append(
                    row_dict['feature_name'])
            # response['entity_product_cam'][row_dict['entity_name']]['products'].append(row_dict['product_name']) if row_dict['product_name'] else None
            if row_dict['location_name'] not in response['entity_product_cam'][row_dict['entity_name']]['locations']:
                response['entity_product_cam'][row_dict['entity_name']]['locations'][
                    row_dict['location_name']] = defaultdict(list)
                response['entity_product_id'][row_dict['entity_name']]['locations'][
                    row_dict['location_name']] = defaultdict(list)
            if row_dict['location_name'] not in response['entity_location'][row_dict['entity_name']]['locations']:
                response['entity_location'][row_dict['entity_name']]['locations'].append(row_dict['location_name'])
            if row_dict['camera_name'] and row_dict['camera_name'] not in \
                    response['entity_product_cam'][row_dict['entity_name']]['locations'][row_dict['location_name']][
                        row_dict['area_name']]:
                response['entity_product_cam'][row_dict['entity_name']]['locations'][row_dict['location_name']][
                    row_dict['area_name']].append(row_dict['camera_name'])
                response['entity_product_id'][row_dict['entity_name']]['locations'][row_dict['location_name']][
                    row_dict['area_name']].append(row_dict['camera_id'])
        with Session_db() as db_session:
            table_data = db_session.execute('SELECT id, name, action FROM m_state')
            for row in table_data.fetchall():
                states_1 = []
                self.state_mapper[str(row[0])] = str(row[1])
                self.state_mapper[str(row[1])] = str(row[0])
                states_1 = [state.strip() for state in str(row[2]).split(',')] if row[2] is not None else None
                self.state_action_mapper[str(row[0])] = states_1
                if states_1 is not None:
                    for st in states_1:
                        if st not in self.state_action_mapper:
                            self.state_action_mapper[st] = []
                            self.state_action_mapper[st] = str(row[0])
                response['state'].append(str(row[1])) if str(row[1]) and str(row[1]) not in response['state'] else None
        with Session_db() as db_session:
            table_data = db_session.execute('SELECT id, name FROM m_event_type')
        for row in table_data.fetchall():
            self.event_mapper[str(row[0])] = str(row[1])
            self.event_mapper[str(row[1])] = str(row[0])
            response['event'].append(str(row[1]))
        with Session_db() as db_session:
            table_data = db_session.execute('SELECT id, name FROM m_tags')
        for row in table_data.fetchall():
            self.class_mapper[str(row[0])] = str(row[1])
            self.class_mapper[str(row[1])] = str(row[0])
            response['classes'].append(str(row[1]))
        with Session_db() as db_session:
            table_data = db_session.execute('SELECT id, name, conv_end_point FROM m_model_type')
            response['model'] = {}
        for row in table_data.fetchall():
            response['model'][str(row[1])] = str(row[2])
            self.model_type_mapper[str(row[0])] = str(row[1])
            self.model_type_mapper[str(row[1])] = str(row[0])

        # with Session_db() as db_session:
        #    table_data = db_session.execute('SELECT id, entity_name, access_rules,location_name,role_name FROM user_data')
        # for row in table_data.fetchall():
        #    self.user_entity_mapper[str(row['id'])] = str(row['entity_name'])
        #    self.user_user_access_mapper[str(row['id'])] = str(row['access_rules'])
        #    self.user_location_mapper[str(row['id'])] = str(row['location_name'])
        #    self.role_mapper[str(row['id'])] = str(row['role_name'])
        # mapper = {'hpcl': {'location': {'area': {'camera_mapper': {}},
        #                        'area_mapper': {},
        #                        'feature_mapper': {}},
        #           'location_mapper': {}},
        #  'entity_mapper': {}}
        for row in response['results']:
            if str(row['entity_name']) in self.mapper:
                if str(row['location_name']) in self.mapper[str(row['entity_name'])]:
                    if str(row['feature_name']) in self.mapper[str(row['entity_name'])][str(row['location_name'])]['feature_mapper']:
                        pass
                    else:
                        self.mapper[str(row['entity_name'])][str(row['location_name'])]['feature_mapper'][str(row['feature_id'])] = str(row['feature_name'])
                        self.mapper[str(row['entity_name'])][str(row['location_name'])]['feature_mapper'][str(row['feature_name'])] = str(row['feature_id'])
                    if str(row['area_name']) in self.mapper[str(row['entity_name'])][str(row['location_name'])]:
                        self.mapper[str(row['entity_name'])][str(row['location_name'])][str(row['area_name'])]['camera_mapper'][str(row['camera_id'])] = str(row['camera_name'])
                        self.mapper[str(row['entity_name'])][str(row['location_name'])][str(row['area_name'])]['camera_mapper'][str(row['camera_name'])] = str(row['camera_id'])
                    else:
                        self.mapper[str(row['entity_name'])][str(row['location_name'])][str(row['area_name'])] = {'camera_mapper': {str(row['camera_id']): str(row['camera_name']), str(row['camera_name']): str(row['camera_id'])}}
                        self.mapper[str(row['entity_name'])][str(row['location_name'])]['area_mapper'][str(row['area_name'])] = str(row['area_id'])
                        self.mapper[str(row['entity_name'])][str(row['location_name'])]['area_mapper'][str(row['area_id'])] = str(row['area_name'])
                else:
                    self.mapper[str(row['entity_name'])][str(row['location_name'])] = {'area_mapper': {str(row['area_name']): str(row['area_id']), str(row['area_id']): str(row['area_name'])}, 'feature_mapper': {str(row['feature_id']): str(row['feature_name']), str(row['feature_name']): str(row['feature_id'])}}
                    self.mapper[str(row['entity_name'])]['location_mapper'][str(row['location_id'])] = str(row['location_name'])
                    self.mapper[str(row['entity_name'])]['location_mapper'][str(row['location_name'])] = str(row['location_id'])
            else:
                self.mapper[str(row['entity_name'])] = {'location_mapper': {str(row['location_id']): str(row['location_name']),
                                                                            str(row['location_name']): str(row['location_id'])},
                                                        str(row['location_name']): {'area_mapper': {str(row['area_name']): str(row['area_id']),
                                                                                                    str(row['area_id']): str(row['area_name'])},
                                                                                    'feature_mapper': {str(row['feature_id']): str(row['feature_name']),
                                                                                                       str(row['feature_name']): str(row['feature_id'])},
                                                                                    str(row['area_name']): {'camera_mapper': {str(row['camera_id']): str(row['camera_name']),
                                                                                                                              str(row['camera_name']): str(row['camera_id'])}}}}
                self.mapper['entity_mapper'][str(row['entity_id'])] = str(row['entity_name'])
                self.mapper['entity_mapper'][str(row['entity_name'])] = str(row['entity_id'])
            # self.camera_mapper[str(row['camera_id'])] = str(row['camera_name'])
            # self.camera_mapper[str(row['camera_name'])] = str(row['camera_id'])
            # self.[str(row['feature_id'])] = str(row['feature_name'])
            # self.feature_mapper[str(row['feature_name'])] = str(row['feature_id'])
            # self.location_mapper[str(row['location_id'])] = str(row['location_name'])
            # self.location_mapper[str(row['location_name'])] = str(row['location_id'])
            # self.feature_mapper[str(row['location_name'])] = str(row['location_id'])
            # self.entity_mapper[str(row['entity_id'])] = str(row['entity_name'])
            # self.entity_mapper[str(row['entity_name'])] = str(row['entity_id'])
            # self.camera_entity_location_area_mapper[str(row['camera_name'])] = {}
            # self.camera_entity_location_area_mapper[str(row['camera_name'])]['entity'] = str(row['entity_name'])
            # self.camera_entity_location_area_mapper[str(row['camera_name'])]['location'] = str(row['location_name'])
            # self.camera_entity_location_area_mapper[str(row['camera_name'])]['area'] = str(row['area_name'])
            # self.area_mapper[str(row['area_name'])] = str(row['area_id'])
            # self.area_mapper[str(row['area_id'])] = str(row['area_name'])

        for row in response['results']:
            self.product_entity_mapper[str(row['camera_id'])] = str(row['product_name']) + "/" + str(row['entity_name'])

        print("Fetch master data successful")
        return response


class Master_rule:
    """class master rule to fetch the data like location , camera, feature, tags, rule kinds , rule types etc for the rule homepage dropdown and fetching the rules according to the user selected feature name """

    def master_rule_(self, Session_db):
        response = defaultdict(list)
        response['dropdown'] = {}
        response['values'] = []
        response = defaultdict(list)

        with Session_db() as db_session:
            table_data = db_session.execute('SELECT * FROM rule_data WHERE feature_name IS NOT NULL ')
            rule_data = db_session.execute('SELECT * FROM m_rule_type')
            operator_data = db_session.execute('SELECT * FROM m_operator')
            rule_kind_data = db_session.execute('SELECT * FROM m_rule_kind')

        columns_rule_kinds = [column[0] for column in rule_kind_data.cursor.description]
        response["rule_kinds"] = {}
        for row_rule_kind in rule_kind_data.fetchall():
            row_dict = dict(zip(columns_rule_kinds, row_rule_kind))
            if row_dict['name'] not in response["rule_kinds"]:
                response["rule_kinds"][row_dict['name']] = {}
            response["rule_kinds"][row_dict['name']][str(row_dict['kind_type'])] = {}
            response["rule_kinds"][row_dict['name']][str(row_dict['kind_type'])]['major_class'] = str(row_dict['major_class'])
            response["rule_kinds"][row_dict['name']][str(row_dict['kind_type'])]['minor_class'] = str(row_dict['minor_class'])

        columns_operators = [column[0] for column in operator_data.cursor.description]
        response["operators"] = []
        for row_operator in operator_data.fetchall():
            row_dict = dict(zip(columns_operators, row_operator))
            response["operators"].append(row_dict['name'])

        columns_rule = [column[0] for column in rule_data.cursor.description]
        response_1 = defaultdict(list)
        response_1['rule_types'] = {}
        response["rule_types"] = []
        for row_rule in rule_data.fetchall():
            row_dict = dict(zip(columns_rule, row_rule))
            response_1["rule_types"][row_dict['type']] = {'operator': response['operators'], 'value': []}
            response["rule_types"].append(row_dict['type'])

        columns = [column[0] for column in table_data.cursor.description]
        response['dropdown'] = {}
        response['feature_rule'] = {}
        for row in table_data.fetchall():
            row_dict = dict(zip(columns, row))
            if row_dict['entity_name'] not in response['dropdown']:
                response['dropdown'][row_dict['entity_name']] = {'location': {}, 'separate': {}}
                response['dropdown'][row_dict['entity_name']]['separate']['rule_types'] = response['rule_types']
                response['dropdown'][row_dict['entity_name']]['separate']['rule_kinds'] = response['rule_kinds']
                response['dropdown'][row_dict['entity_name']]['separate']['operators'] = response['operators']
                response['dropdown'][row_dict['entity_name']]['separate']['values'] = response['values']

            if row_dict['location_name'] not in response['dropdown'][row_dict['entity_name']]['location']:
                response['dropdown'][row_dict['entity_name']]['location'][row_dict['location_name']] = {}
            response['dropdown'][row_dict['entity_name']]['location'][row_dict['location_name']][row_dict['camera_name']] = {}
            if row_dict['feature_name'] not in response['dropdown'][row_dict['entity_name']]['location'][row_dict['location_name']][row_dict['camera_name']]:
                response['dropdown'][row_dict['entity_name']]['location'][row_dict['location_name']][row_dict['camera_name']][row_dict['feature_name']] = {}

            if row_dict['tag_name'] not in response['dropdown'][row_dict['entity_name']]['location'][row_dict['location_name']][row_dict['camera_name']][row_dict['feature_name']]:
                response['dropdown'][row_dict['entity_name']]['location'][row_dict['location_name']][row_dict['camera_name']][row_dict['feature_name']][row_dict['tag_name']] = response_1['rule_types']

            if row_dict['entity_name'] not in response['feature_rule']:
                response['feature_rule'][row_dict['entity_name']] = {}

            if row_dict['feature_name'] not in response['feature_rule'][row_dict['entity_name']]:
                response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']] = {}

            if row_dict['rule_kind_name'] is not None:
                if row_dict['rule_kind_name'] not in response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']]:
                    response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']] = {}

                if row_dict['rule_kind_type'] not in response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']]:
                    response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']] = {"major": {}, "minor": {}, "custom": []}
                if row_dict['tag_type'] == "major":
                    if row_dict['tag_name'] not in response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["major"]:
                        response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["major"][row_dict["tag_name"]] = []
                    response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["major"][row_dict["tag_name"]].append({row_dict['rule_type']: row_dict['value'], "operator": row_dict['operator_name']})

                if row_dict['tag_type'] == "minor":
                    if row_dict['tag_name'] not in response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["minor"]:
                        response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["minor"][row_dict["tag_name"]] = []
                    response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["minor"][row_dict["tag_name"]].append({row_dict['rule_type']: row_dict['value'], "operator": row_dict['operator_name']})

                if row_dict['tag_name'] is None and row_dict['tag_type'] is None:
                    response['feature_rule'][row_dict['entity_name']][row_dict['feature_name']][row_dict['rule_kind_name']][row_dict['rule_kind_type']]["custom"].append({row_dict['rule_type']: row_dict['value'], "operator": row_dict['operator_name']})

        print("Fetch rule master data successful")
        return response


class ExtractImages:

    def __init__(self, config):
        self.local_file_path = config.config.get('video_location')
        self.img_num = 0
        self.config = config

    def zip(self, image_directory):
        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

        zipf = zipfile.ZipFile(image_directory + '.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(image_directory, zipf)
        zipf.close()
        return image_directory + '.zip'

    @classmethod
    def unzip(cls, zip_directory):
        zipf = zipfile.ZipFile(zip_directory)
        zipf.extractall(os.path.split(zip_directory)[0])

    def convert(self, mins):
        h, m, s = mins.split(':')
        sec = int(int(h) * 3600) + int((int(m) * 60) + int(s) * 1)
        return sec

    def ext_imgs(self, cap, fps, start, end, no_of_imgs, duration_id, local_image_end_point):
        local_image_end_point = os.path.join(local_image_end_point, str(duration_id))
        if not os.path.exists(local_image_end_point):
            os.makedirs(local_image_end_point)
        i = 0
        start, end = start * fps, end * fps
        total_frames = end - start
        interval = total_frames / no_of_imgs
        if interval == 0:
            interval = 1
        print("total frames {}, interval {}".format(total_frames, interval))
        image_count = int(start / interval)
        while True:
            try:
                ret, img = cap.read()
                if ret and ((i < end) and (i >= start) and int(i % interval) == 0):
                    image_count = image_count + 1
                    self.img_num = self.img_num + 1
                    print("iteration {}, image number {}".format(i, self.img_num))
                    cv2.imwrite(os.path.join(local_image_end_point, '{}_{}_{}.{}'.format(str(self.img_num), img.shape[1], img.shape[0], 'jpg')), img)
                elif not ret:
                    print("************** Breaking **************")
                    break
                i = i + 1
            except Exception as e:
                print(str(e))

    def extract_images(self, video_end_point, durations, _durations_ids, media_status_id):
        try:
            image_end_points = os.path.splitext(video_end_point)[0] + self.config.config.get('image_directory_tag')
            image_end_points = image_end_points.replace(self.config.config.get('video_header'), self.config.config.get('image_header'))
            local_video_end_point = os.path.join(self.local_file_path, video_end_point)
            local_image_end_point = os.path.join(self.local_file_path, image_end_points)

            for duration, duration_id in zip(durations, _durations_ids):
                start = self.convert(duration["start"])
                end = self.convert(duration["end"])
                no_of_imgs = int(duration["images_count"])
                cap = cv2.VideoCapture(local_video_end_point)
                fps = cap.get(cv2.CAP_PROP_FPS)
                print("Start time = {}, End time = {}, Number of images = {}, Frames per second = {}".format(start, end, no_of_imgs, fps))
                self.ext_imgs(cap, fps, start, end, no_of_imgs, duration_id, local_image_end_point)

            zip_path = self.zip(local_image_end_point)

            for duration, duration_id in zip(durations, _durations_ids):
                filter_params = {'id': duration_id}
                update_params = {'extraction_status': config.config['status']['upload_pending']}
                async_data_process.update(MediaDuration, update_params=update_params, filter_params=filter_params)

            async_data_process.upload(zip_path, image_end_points + '.zip')

            for duration, duration_id in zip(durations, _durations_ids):
                filter_params = {'id': duration_id}
                update_params = {'media_end_point': image_end_points + '.zip',
                                 'extraction_status': 'process_complete'}
                async_data_process.update(MediaDuration, update_params=update_params, filter_params=filter_params)

            filter_params = {'id': media_status_id}
            update_params = {'image_end_point': image_end_points + '.zip',
                             'state_id': int(master_data_obj.state_mapper.get(config.config['status']['extract_completed']))}
            async_data_process.update(Media, update_params=update_params, filter_params=filter_params)
            return True
        except Exception as e:
            print(str(e))
            return False


class Video_Stream:
    def __init__(self, obj):
        self.obj = obj
        self.counter = 0

    def gen_2(self):
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
            while True:
                img = self.obj.GetImage()
                if not img.IsEmpty():
                    imgarr = (cv2.putText(img.GetNPArray(), str(datetime.now()), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA))
                    cv2.namedWindow("combined", cv2.WINDOW_NORMAL)
                    combined = cv2.hconcat([imgarr])
                    frame = cv2.resize(combined, (1280, 720))
                    result, frame = cv2.imencode('.jpg', frame, encode_param)
                    self.counter = self.counter + 1
                    frame_data1 = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    cv2.imwrite("one11.jpg", frame_data1)
                    img1 = Image.open('one11.jpg', mode='r')
                    imgByteArr = io.BytesIO()
                    img1.save(imgByteArr, format=img1.format)
                    imgByteArr = imgByteArr.getvalue()

                    if cv2.waitKey(1) == 27:
                        break
                    else:
                        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'

        except Exception as exc:
            print('error: ', exc)


class VideoStream:

    def __init__(self, app, data_str, connect):
        self.host = app.get('live_stream_host')
        self.port = app.get('live_stream_port')
        self.data_str = data_str
        self.hpcl_client = None
        self.connect = connect

    def gen_frames(self):
        try:
            frame = b''
            if self.hpcl_client:
                payload_size = struct.calcsize(">L")
                while True:
                    while len(frame) < payload_size:
                        frame += self.hpcl_client.recv(5 * 1024 * 1024)
                    packed_msg_size = frame[:payload_size]
                    frame = frame[payload_size:]
                    msg_size = struct.unpack(">L", packed_msg_size)[0]
                    while len(frame) < msg_size:
                        frame += self.hpcl_client.recv(5 * 1024 * 1024)
                    frame_data = frame[:msg_size]
                    frame = b''
                    frame_data = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                    frame_data1 = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                    cv2.imwrite("one11.jpg", frame_data1)
                    img1 = Image.open('one11.jpg', mode='r')
                    imgByteArr = io.BytesIO()
                    img1.save(imgByteArr, format=img1.format)
                    imgByteArr = imgByteArr.getvalue()
                    self.hpcl_client.send(b'sucess')
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'
            else:
                self.hpcl_client = self.initiate_socket()
                self.hpcl_client.send(self.data_str.encode())
                message = self.hpcl_client.recv(5 * 1024 * 1024)
                if message == 'ok':
                    payload_size = struct.calcsize(">L")
                    while True:
                        while len(frame) < payload_size:
                            frame += self.hpcl_client.recv(5 * 1024 * 1024)
                        packed_msg_size = frame[:payload_size]
                        frame = frame[payload_size:]
                        msg_size = struct.unpack(">L", packed_msg_size)[0]
                        while len(frame) < msg_size:
                            frame += self.hpcl_client.recv(5 * 1024 * 1024)
                        frame_data = frame[:msg_size]
                        frame = b''
                        frame_data = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                        frame_data1 = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                        cv2.imwrite("one11.jpg", frame_data1)
                        img1 = Image.open('one11.jpg', mode='r')
                        imgByteArr = io.BytesIO()
                        img1.save(imgByteArr, format=img1.format)
                        imgByteArr = imgByteArr.getvalue()
                        self.hpcl_client.send(b'sucess')
                        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'
        except Exception as e_:
            self.hpcl_client.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.connect.loginfo("#. Except in gen_frames " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')

    def initiate_socket(self):
        try:
            tcp_host, tcp_port = self.host, self.port
            hpcl_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hpcl_server.bind((tcp_host, tcp_port))
            hpcl_server.listen(5)
            (connection, (client_address, port)) = hpcl_server.accept()
            return connection
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.connect.loginfo("#. Exception in initiate_socket " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='error')


class VideoStreamConsumer:

    def __init__(self, camera_name, Utility, sample_connect, unique_name, entity, location, feature=None):
        self.sample_connect = sample_connect
        self.unique_name = unique_name
        self.camera_name = camera_name
        self.unique_number = str(int(datetime.now().timestamp() * 1000))
        self.Utility = Utility
        self.utility_configuration = {"debug": 1,
                                      "log_file": 'VideoStreamConsumer.log',
                                      "mode": 1,
                                      "enable_db": False,
                                      "enable_redis": False,
                                      "enable_rabbitmq_consumer": True,
                                      "enable_rabbitmq_publisher": False,
                                      "redis_db": 0,
                                      "log_level": logging.DEBUG,
                                      "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                                      "database": "ZestIot_AppliedAI",
                                      "server": ''}
        self.features = None
        if feature:
            self.features = self.find_r_key(entity, location, self.camera_name)
        self.sample_connect.loginfo("#. Routing key = {}".format(str(["#.{camera_name}.#".format(camera_name=self.camera_name)] if not self.features else [self.features])))
        self.rabbitmq_consumer = {"exchange": "Feed" if not feature else "Inference",
                                  "routing_keys": ["#.{camera_name}.#".format(camera_name=self.camera_name)] if not self.features else [self.features],
                                  "exchange_type": 'topic',
                                  "durable": 'False',
                                  "exclusive": True,
                                  "arguments": {'x-max-length': 100},
                                  "queue": "live_feed_{camera_name}".format(camera_name=self.camera_name)}
        self.sample_connect.loginfo("#. configuration = {}".format(str(self.utility_configuration)))
        self.sample_connect.loginfo("#. consumer = {}".format(str(self.rabbitmq_consumer)))
        self.connect = None
        self.first_frame = True
        self.last_frame = b''
        # try:
        # self.capture = cv2.VideoCapture('rtsp://admin:Pass@123@192.168.1.15:554/ch2/main/av_stream')
        #     self.capture = cv2.VideoCapture('rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4')
        # except Exception as e_:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     self.sample_connect.loginfo("except in cv connection " + str(e_) + ' ' + str(exc_tb.tb_lineno))

    def find_r_key(self, entity, location, area_name):
        try:
            sql = "select feature_name, model_name from master_data A left join rule_data B on A.camera_id = B.camera_id where A.entity_name = '{entity}' and A.location_name = '{location}' and A.area_name = '{area_name}'".format(entity=entity,
                                                                                                                                                                                                              location=location,
                                                                                                                                                                                                              area_name=area_name)
            features = self.sample_connect.query_database_df(sql=sql)
            if features.empty:
                pass
            else:
                features_list = list(set(features['feature_name']))
                models_list = [model_name.lower() for model_name in list(set(features['model_name']))]
            self.sample_connect.loginfo("#. Features fetched are " + str(features))
            if any(['material_detection' in x for x in models_list]):
                return '#.{area_name}.#.Material_Detection.#'.format(area_name=area_name)
            else:
                return '#.{area_name}.#.Conveyor_Belt_Defects.#'.format(area_name=area_name)
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.sample_connect.loginfo("#. Except in find_r_key " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')

    def gen_frames(self):
        try:
            frame = b''
            if self.connect:
                while True:
                    # message_count = self.connect.consumer_result.method.message_count
                    # self.sample_connect.loginfo(str(message_count))
                    # if message_count > 0:
                    close_connection = self.sample_connect.master_redis.get_val(key='video_feed_{}_{}'.format(self.camera_name, self.unique_name))
                    close_connection = close_connection if close_connection else 'None'
                    if close_connection == 'close':
                        if len(self.last_frame) < 1:
                            close_connection = 'None'
                            self.sample_connect.master_redis.set_val(key='video_feed_{}_{}'.format(self.camera_name, self.unique_name), val=close_connection)
                    try:
                        if close_connection != 'close':
                            message = self.connect.consumer_channel.basic_get('', auto_ack=True)[2]
                            if message:
                                message = json.loads(message)
                                self.sample_connect.loginfo("Fream read from queue ....", 'info')
                                # sleep(0.2)
                                if message.get('frame'):
                                    imgByteArr = bytes.fromhex(message.get('frame'))
                                    self.last_frame = imgByteArr
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                                elif message.get('inf_op_img'):
                                    imgByteArr = bytes.fromhex(message.get('inf_op_img'))
                                    self.last_frame = imgByteArr
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                                elif message.get('image'):
                                    images = message.get('image')
                                    l2 = []
                                    for camera_name, frame in images.items():
                                        frame_array = cv2.imdecode(np.frombuffer(bytes.fromhex(frame), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                                        l2.append(frame_array)
                                    img_enc = np.hstack(tuple(l2))
                                    _, img_enc = cv2.imencode('.jpg', img_enc)
                                    self.last_frame = img_enc.tobytes()
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                            else:
                                self.sample_connect.loginfo("No frames in queue ....", 'info')
                                sleep(0.2)
                                if self.first_frame:
                                    self.first_frame = False
                                    frame = np.zeros([1080, 1920, 3], dtype=np.uint8)
                                    frame.fill(255)
                                    _, imgencode = cv2.imencode('.jpg', frame)
                                    imgByteArr = imgencode.tobytes()
                                    self.last_frame = imgByteArr
                                    self.sample_connect.loginfo(" **** Created message **** ")
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'
                                else:
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                        else:
                            self.sample_connect.master_redis.set_val(key='video_feed_{}_{}'.format(self.camera_name, self.unique_name), val='None')
                            break
                    except Exception as e_:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        self.sample_connect.loginfo("#. Except in gen_frames " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')
                        break
                    # sleep(1/10)
                return b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
            else:
                self.connect = self.initiate_socket()
                while True:
                    close_connection = self.sample_connect.master_redis.get_val(key='video_feed_{}_{}'.format(self.camera_name, self.unique_name))
                    close_connection = close_connection if close_connection else 'None'
                    if close_connection == 'close':
                        if len(self.last_frame) < 1:
                            close_connection = 'None'
                            self.sample_connect.master_redis.set_val(key='video_feed_{}_{}'.format(self.camera_name, self.unique_name), val=close_connection)
                    try:
                        if close_connection != 'close':
                            message = self.connect.consumer_channel.basic_get('', auto_ack=True)[2]
                            # sleep(0.2)
                            if message:
                                message = json.loads(message)
                                if message.get('frame'):
                                    imgByteArr = bytes.fromhex(message.get('frame'))
                                    self.last_frame = imgByteArr
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                                elif message.get('inf_op_img'):
                                    imgByteArr = bytes.fromhex(message.get('inf_op_img'))
                                    self.last_frame = imgByteArr
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                                elif message.get('image'):
                                    images = message.get('image')
                                    l2 = []
                                    for camera_name, frame in images.items():
                                        frame_array = cv2.imdecode(np.frombuffer(bytes.fromhex(frame), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                                        print(frame_array.shape)
                                        l2.append(frame_array)
                                    img_enc = np.hstack(tuple(l2))
                                    print(img_enc.shape)
                                    _, img_enc = cv2.imencode('.jpg', img_enc)
                                    self.last_frame = img_enc.tobytes()
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                            else:
                                self.sample_connect.loginfo("No frames in queue ....", 'info')
                                sleep(0.2)
                                if self.first_frame:
                                    self.first_frame = False
                                    frame = np.zeros([1080, 1920, 3], dtype=np.uint8)
                                    frame.fill(255)
                                    _, imgencode = cv2.imencode('.jpg', frame)
                                    imgByteArr = imgencode.tobytes()
                                    self.last_frame = imgByteArr
                                    self.sample_connect.loginfo(" **** Created message **** ")
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'
                                else:
                                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
                        else:
                            self.sample_connect.master_redis.set_val(key='video_feed_{}_{}'.format(self.camera_name, self.unique_name), val='None')
                            break
                    except Exception as e_:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        self.sample_connect.loginfo("#. Except in gen_frames " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')
                        break
                    # sleep(1/10)
                return b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.last_frame + b'\r\n'
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.sample_connect.loginfo("#. Except in gen_frames " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')

    def gen_frames1(self):
        try:
            while True:
                frame_key = 'frame' + '_' + self.camera_name
                self.sample_connect.loginfo(" **** key " + str(frame_key))
                message = self.sample_connect.master_redis.get_val(key=frame_key)
                if message:
                    message = json.loads(message)
                    imgByteArr = bytes.fromhex(message.get('frame'))
                    self.sample_connect.loginfo(" **** Got message from redis **** ")
                    sleep(0.1)
                else:
                    frame = np.zeros([1080, 1920, 3], dtype=np.uint8)
                    frame.fill(255)
                    _, imgencode = cv2.imencode('.jpg', frame)
                    imgByteArr = imgencode.tobytes()
                    self.sample_connect.loginfo(" **** Created message **** ")
                    sleep(0.1)
                yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'
        except Exception as e_:
            self.connect.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.sample_connect.loginfo("#. Except in gen_frames " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')

    def gen_frames2(self):
        while True:
            try:
                ret, frame = self.capture.read()
                if ret:
                    frame = cv2.resize(frame, (224, 224))
                    self.cam_health = True
                    _, imgencode = cv2.imencode('.jpg', frame)
                    imgByteArr = imgencode.tobytes()
                    yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n'
            except Exception as e_:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                self.sample_connect.loginfo("#. Except in gen_frames " + str(e_) + ' ' + str(exc_tb.tb_lineno))

    def initiate_socket(self):
        try:
            self.connect = self.Utility(configuration=self.utility_configuration,
                                        rabbitmq_consumer=self.rabbitmq_consumer)
            return self.connect
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.connect.loginfo("#. Exception in initiate_socket " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')

    def complete_socket(self):
        try:
            self.connect.loginfo("Trying to clomplete socket")
            self.close = True
            self.connect.consumer_channel.close()
            self.connect.consumer_connection.close()
        except Exception as e_:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.connect.loginfo("#. Exception in complete_socket " + str(e_) + ' ' + str(exc_tb.tb_lineno), level='info')


class AsyncDataProcess:

    def __init__(self, config, engine, Session_db):
        self.connection_string = config.config.get("azure_storage_connection_string")
        self.container_name = config.config.get("container_name_video")
        self.blob_name = config.config.get("blob_name")
        self.engine = engine
        self.Session_db = Session_db

    def re_connect(self):
        try:
            self.Session_db.close()
            self.engine.dispose()
        except Exception as e:
            print("re establishing the connection")
            print(e)

    def insert(self, table, insert_params=None, connect=None, multiple_param_insert=None, retry_count=0):
        self.re_connect()
        self.engine, self.Session_db = db_connection()
        try:
            if insert_params:
                table_object = table(**insert_params)
                with self.Session_db() as db_session:
                    db_session.add(table_object)
                    db_session.commit()
                    return table_object.id
            elif multiple_param_insert:
                table_object = [table(**insert) for insert in multiple_param_insert]
                with self.Session_db() as db_session:
                    db_session.add_all(table_object)
                    db_session.commit()
                    print("successfully added")

        except Exception as e:
            if "Lost connection to MySQL server during query" in str(e) or "MySQL server has gone away" in str(e) or "(0, '')" in str(e) or "(2013" in str(e):
                connect.loginfo("DB connection lost ... re-connecting for {} time".format(retry_count + 1))
                self.engine, self.Session_db = db_connection()
                self.insert(table, insert_params, retry_count=retry_count + 1)
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()

                connect.loginfo("Exception in insert " + str(e) + ' ' + str(exc_tb.tb_lineno))

    def update(self, table, update_params=None, filter_params=None, bulk_update_params=None, retry_count=0):
        self.re_connect()
        self.engine, self.Session_db = db_connection()
        try:
            with self.Session_db() as db_session:
                if update_params:
                    where_clauses = [getattr(table, column) == filter_params[column] for column in filter_params]
                    x = db_session.query(table).where(and_(*where_clauses)).update(values=update_params)
                    db_session.commit()
                    return x
                elif bulk_update_params:
                    db_session.query(table).filter(table.col1.in_(payload)
                                                   ).update({
                        MyTable.col2: case(
                            payload,
                            value=MyTable.col1,
                        )
                    }, synchronize_session=False)

        except Exception as e:
            if "Lost connection to MySQL server during query" in str(e) or "MySQL server has gone away" in str(e) or "(0, '')" in str(e) or "(2013" in str(e):
                print("DB connection lost ... re-connecting for {} time".format(retry_count + 1))
                self.engine, self.Session_db = db_connection()
                self.update(table, update_params, filter_params, retry_count=retry_count + 1)
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("Exception in insert " + str(e) + ' ' + str(exc_tb.tb_lineno))

    def select(self, table, filter_params=None, get_first_row=False, get_distinct_rows=None, retry_count=0):  # if no is false it means all result else if no is true it means one result
        self.re_connect()
        self.engine, self.Session_db = db_connection()
        try:
            with self.Session_db() as db_session:
                if not filter_params and not get_distinct_rows:
                    result = db_session.query(table).all()
                    return result
                elif not filter_params and get_distinct_rows:
                    result = db_session.query(table).distinct(','.join(get_distinct_rows.get("columns")))
                    return result
                else:
                    if get_first_row:
                        where_clauses = [getattr(table, column) == filter_params[column] for column in filter_params]
                        result = db_session.query(table).where(and_(*where_clauses)).first()
                        return result
                    elif any([isinstance(filter_params[column], list) for column in filter_params]):
                        result = db_session.query(table)
                        for column in filter_params:
                            if isinstance(filter_params[column], list):
                                result = result.filter(getattr(table, column).in_(filter_params[column]))
                            else:
                                result = result.filter(getattr(table, column) == filter_params[column])
                        return result
                    else:
                        where_clauses = [getattr(table, column) == filter_params[column] for column in filter_params]
                        result = db_session.query(table).where(and_(*where_clauses)).all()
                        return result
        except Exception as e:
            if "Lost connection to MySQL server during query" in str(e) or "MySQL server has gone away" in str(e) or "(0, '')" in str(e) or "(2013" in str(e):
                print("DB connection lost ... re-connecting for {} time".format(retry_count + 1))
                self.engine, self.Session_db = db_connection()
                self.select(table, filter_params=None, get_first_row=False, get_distinct_rows=None, retry_count=retry_count + 1)
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("Exception in insert " + str(e) + ' ' + str(exc_tb.tb_lineno))

    def join_select(self, tables, join_params, add_column_params, table_names, filter_params=None, join='inner', retry_count=0):
        self.re_connect()
        self.engine, self.Session_db = db_connection()
        try:
            tables_filter = copy.deepcopy(tables)
            with self.Session_db() as db_session:
                if filter_params:
                    for filter_param_index in range(len(filter_params)):
                        for index in filter_params[filter_param_index]:
                            result = db_session.query(tables[filter_param_index][index])
                            for column in filter_params[filter_param_index][index]:
                                if isinstance(filter_params[filter_param_index][index][column], list):
                                    result = result.filter(getattr(tables[filter_param_index][index], column).in_(filter_params[filter_param_index][index][column]))
                                else:
                                    result = result.filter(getattr(tables[filter_param_index][index], column) == filter_params[filter_param_index][index][column])
                            tables_filter[filter_param_index][index] = result
                result = db_session.query(tables[0][0]) if (filter_params and not 0 in filter_params[0]) or (not filter_params) else tables_filter[0][0]
                for tables_list, join_params_dict in zip(tables, join_params):
                    for table_index in range(1, len(tables_list[1:]) + 1):
                        if join == 'left':
                            result = result.join(tables_list[table_index],
                                                 getattr(tables_list[table_index], join_params_dict[table_index][1]) == getattr(tables_list[0], join_params_dict[table_index][0]), isouter=True)
                        else:
                            result = result.join(tables_list[table_index],
                                                 getattr(tables_list[table_index],
                                                         join_params_dict[table_index][1]) == getattr(tables_list[0],
                                                                                                      join_params_dict[
                                                                                                          table_index][
                                                                                                          0]))
                for (tables_list, add_column_params_dict, table_names_list) in zip(tables, add_column_params,
                                                                                   table_names):
                    for table_index, table_name_prefix in zip(range(1, len(tables_list[1:]) + 1), table_names_list[1:]):
                        if len(add_column_params_dict) > 0:
                            for column in add_column_params_dict[table_index]:
                                result = result.add_columns(
                                    getattr(tables_list[table_index], column).label(table_name_prefix + "_" + column))
                # result = db_session.query(RolePermissions).add_columns(Designation.name, Department.name)
            return result
        except Exception as e:
            if "Lost connection to MySQL server during query" in str(e) or "MySQL server has gone away" in str(
                    e) or "(0, '')" in str(e) or "(2013" in str(e):
                print("DB connection lost ... re-connecting for {} time".format(retry_count + 1))
                self.engine, self.Session_db = db_connection()
                self.join_select(tables, join_params, add_column_params, table_names, retry_count=retry_count + 1)
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("Exception in join_select " + str(e) + ' ' + str(exc_tb.tb_lineno))

    def delete(self, table, filter_params, retry_count=0):
        self.re_connect()
        self.engine, self.Session_db = db_connection()
        try:
            with self.Session_db() as db_session:
                where_clauses = [getattr(table, column) == filter_params[column] for column in filter_params]
                db_session.query(table).where(and_(*where_clauses)).delete()
                db_session.commit()
                return True
        except Exception as e:
            if "Lost connection to MySQL server during query" in str(e) or "MySQL server has gone away" in str(e) or "(0, '')" in str(e) or "(2013" in str(e):
                print("DB connection lost ... re-connecting for {} time".format(retry_count + 1))
                self.engine, self.Session_db = db_connection()
                self.delete(table, filter_params, retry_count=retry_count + 1)
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("Exception in insert " + str(e) + ' ' + str(exc_tb.tb_lineno))

    def insert_update(self, table, insert_update_params, filter_params, retry_count=0):
        self.re_connect()
        self.engine, self.Session_db = db_connection()
        try:
            rows_updated = async_data_process.update(table, insert_update_params, filter_params)
            if rows_updated == 0:
                async_data_process.insert(table, insert_update_params)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Exception in insert_update " + str(e) + ' ' + str(exc_tb.tb_lineno))

    def upload(self, file_to_upload, _upload_location):
        try:
            container_client = ContainerClient.from_connection_string(self.connection_string, self.container_name)
            print("uploading in progress ...")
            blob_client = container_client.get_blob_client(_upload_location)
            with open(file_to_upload, 'rb') as data:
                blob_client.upload_blob(data)
                print("Uploaded {} to container {} ...".format(file_to_upload, self.container_name))
                # os.remove(file_to_upload)
                # print("Successfully removed file {}".format(file_to_upload))
            return 1
        except Exception as e_:
            print(str(e_))
            return 0

    def remove_blob(self, _remove_location):
        try:
            container_client = ContainerClient.from_connection_string(self.connection_string, self.container_name)
            print("deleting in progress ...")
            blob_client = container_client.get_blob_client(_remove_location)
            blob_client.delete_blob()
            return 1
        except Exception as e_:
            print(str(e_))
            return 0

    def download(self, file_to_download, download_location, container_name=None):
        try:
            if not container_name:
                container_name = self.container_name
            container_client = ContainerClient.from_connection_string(self.connection_string, container_name)
            print("downloading in progress ...")
            blob_client = container_client.get_blob_client(file_to_download)
            with open(download_location, "wb+") as data:
                blob_data = blob_client.download_blob()
                blob_data.readinto(data)
        except Exception as e_:
            print(str(e_))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [])


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    # if accounts:  # So all account(s) belong to the current signed-in user
    result = cca.acquire_token_silent(scope, account=None)
    _save_cache(cache)
    return result


Base = declarative_base(cls=DictableModel)
Base.metadata.reflect(engine)

master_data_obj = MasterData()
master_data = master_data_obj.master_data_(Session_db)
# master_rule_obj = Master_rule()
# master_rule = master_rule_obj.master_rule_(Session_db)
master_rule = ''
async_data_process = AsyncDataProcess(config=config, engine=engine, Session_db=Session_db)
extract_images = ExtractImages(config)
event_data = Event_data()
# event_d_data = event_data.event_fetch_data()
rabbitmq = Rabbitmq()


class Media(Base):
    __table__ = Base.metadata.tables['t_media']


class Event(Base):
    __table__ = Base.metadata.tables['t_event']


class MediaTagMap(Base):
    __table__ = Base.metadata.tables['media_tags_mapping']


class MediaDuration(Base):
    __table__ = Base.metadata.tables['t_media_durations']


class Classes(Base):
    __table__ = Base.metadata.tables['m_tags']


class UserProfile(Base, UserMixin):
    __table__ = Base.metadata.tables['m_user_profile']


class Entities(Base):
    __table__ = Base.metadata.tables['m_entity']


class Locations(Base):
    __table__ = Base.metadata.tables['m_location']


class Areas(Base):
    __table__ = Base.metadata.tables['m_area']


class Camera(Base):
    __table__ = Base.metadata.tables['m_camera']


class Camera_Feature(Base):
    __table__ = Base.metadata.tables['camera_feature_mapping']


class Operators(Base):
    __table__ = Base.metadata.tables['m_operator']


class Rule_Type(Base):
    __table__ = Base.metadata.tables['m_rule_type']


class Rule(Base):
    __table__ = Base.metadata.tables['m_rule']


class Feature(Base):
    __table__ = Base.metadata.tables['m_feature']


class EventLogs(Base):
    __table__ = Base.metadata.tables['t_event_logs']


class UserSession(Base):
    __table__ = Base.metadata.tables['m_user_session']


class RolePermissions(Base):
    __table__ = Base.metadata.tables['m_roles_permissions']


class Department(Base):
    __table__ = Base.metadata.tables['m_department']


class Designation(Base):
    __table__ = Base.metadata.tables['m_designation']


class AccessViews(Base):
    __table__ = Base.metadata.tables['m_access_views']


class Rule_json(Base):
    __table__ = Base.metadata.tables['m_rule_json']


class ModelType(Base):
    __table__ = Base.metadata.tables['m_model_type']


class Model(Base):
    __table__ = Base.metadata.tables['m_model']


class FeatureRoi(Base):
    __table__ = Base.metadata.tables['m_feature_roi']


class Remarks(Base):
    __table__ = Base.metadata.tables['remarks']


class FeedRemarks(Base):
    __table__ = Base.metadata.tables['t_image_remarks']


