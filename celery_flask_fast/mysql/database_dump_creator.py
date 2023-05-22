from datetime import datetime, date
import numpy as np
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from flask_fast_api.app.api_connectivity.utility import Utility
from flask_fast_api.app.configuration import constants


class MysqlDump:

    def __init__(self):
        self.dump = open(os.path.join(BASE_DIR, 'mysql/ZestIot_AppliedAI.sql')).read()
        self.connect = Utility(configuration=constants.dump_configuration)
        self.edge_id = self.connect.config_json.get("edge_id")
        self.ip, self.location_id, self.synch_duration_hrs =  self.get_edge( self.edge_id)
        self.location_name, self.location_code, self.entity_id, self.entity_name, self.entity_code = self.get_entity(self.location_id)
        self.product_id, self.product_name = self.get_product(self.entity_id)
        self.area_ids = self.get_area_ids(self.location_id)
        self.camera_ids = self.get_camera_ids(self.area_ids)
        self.tables = {'m_user_session': {'table_name': 'm_user_session',
                                          'query': '',
                                          'columns': ['session_key', 'user_id'],
                                          'insert_query': 'insert into m_user_session (session_key, user_id) values '},
                       'm_department': {'table_name': 'm_department',
                                        'query': 'select * from m_department',
                                        'columns': ['name'],
                                        'insert_query': 'insert into m_department (name) values '},
                       'm_designation': {'table_name': 'm_designation',
                                         'query': 'select * from m_designation',
                                         'columns': ['name'],
                                         'insert_query': 'insert into m_designation (name) values '},
                       'm_roles_permissions': {'table_name': 'm_roles_permissions',
                                               'query': 'select * from m_roles_permissions',
                                               'columns': ['access_rules', 'role_name', 'department_id', 'designation_id'],
                                               'columns_map': {'department_id': 'm_department', 'designation_id': 'm_designation'},
                                               'insert_query': 'insert into m_roles_permissions (access_rules, role_name, department_id, designation_id) values '},
                       'm_location_type': {'table_name': 'm_location_type',
                                           'query': 'select * from m_location_type',
                                           'columns': ['type', 'status'],
                                           'insert_query': 'insert into m_location_type (type, status) values '},
                       'm_entity': {'table_name': 'm_entity',
                                    'query': 'select * from m_entity where id = {entity_id}'.format(entity_id=self.entity_id),
                                    'columns': ['name', 'code', 'type', 'status'],
                                    'insert_query': 'insert into m_entity (name, code, type, status) values '},
                       'm_location': {'table_name': 'm_location',
                                      'query': 'select * from m_location where entity_id = {entity_id}'.format(entity_id=self.entity_id),
                                      'columns': ['name', 'code', 'address', 'city', 'pincode', 'state', 'country', 'entity_id', 'status'],
                                      'insert_query': 'insert into m_location (name, code, address, city, pincode, state, country, entity_id, status) values '},
                       'location_mapping': {'table_name': 'location_mapping',
                                            'query': 'select * from location_mapping where location_id = {location_id}'.format(location_id=self.location_id),
                                            'columns': ['location_type_id', 'location_id', 'status'],
                                            'insert_query': 'insert into location_mapping (location_type_id, location_id, status) values '},
                       'm_user_profile': {'table_name': 'm_user_profile',
                                          'query': "select * from m_user_profile where login_name = 'zest_admin' ",
                                          'columns': ['full_name',
                                                      'login_name',
                                                      'password',
                                                      'entity_id',
                                                      'status',
                                                      'role_id',
                                                      'employee_id',
                                                      'gender',
                                                      'mobile',
                                                      'email',
                                                      'location_id',
                                                      'user_login_type'],
                                          'columns_map': {'role_id': 'm_roles_permissions'},
                                          'insert_query': 'insert into m_user_profile (full_name, login_name, password, entity_id, status, role_id, employee_id, gender, mobile, email, location_id, user_login_type) values '},
                       'm_user_group': {'table_name': 'm_user_group',
                                        'query': '',
                                        'columns': ['name', 'created_by', 'created_on', 'entity_id', 'status'],
                                        'insert_query': 'insert into m_user_group (name, created_by, created_on, entity_id, status) values '},
                       'user_group_mapping': {'table_name': 'user_group_mapping',
                                              'query': '',
                                              'columns': ['user_id', 'group_id', 'status'],
                                              'columns_map': {'group_id': 'm_user_group'},
                                              'insert_query': 'insert into user_group_mapping (user_id, group_id, status) values '},
                       'm_group_permission': {'table_name': 'm_group_permission',
                                              'query': '',
                                              'columns': ['group_id', 'permissions', 'status'],
                                              'columns_map': {'group_id': 'm_user_group'},
                                              'insert_query': 'insert into m_group_permission (group_id, permissions, status) values '},
                       'm_access_views': {'table_name': 'm_access_views',
                                          'query': 'select * from m_access_views',
                                          'columns': ['name'],
                                          'insert_query': 'insert into m_access_views (name) values '},
                       'm_edge': {'table_name': 'm_edge',
                                  'query': 'select * from m_edge',
                                  'columns': ['name', 'ip', 'location_id', 'synch_duration_hrs'],
                                  'insert_query': 'insert into m_edge (name, ip, location_id, synch_duration_hrs) values '},
                       'm_area': {'table_name': 'm_area',
                                  'query': "select * from m_area where location_id = {location_id}".format(location_id=self.location_id),
                                  'columns': ['name', 'location_id', 'status', 'updated_at', 'created_at'],
                                  'insert_query': 'insert into m_area (name, location_id, status, updated_at, created_at) values '},
                       'm_camera': {'table_name': 'm_camera',
                                    'query': "select * from m_camera where area_id in ({area_ids}) ".format(area_ids=self.area_ids),
                                    'columns': ['ip',
                                                'rtsp_link',
                                                'name',
                                                'owner',
                                                'description',
                                                'model',
                                                'roi1',
                                                'roi2',
                                                'roi3',
                                                'roi4',
                                                'roi5',
                                                'specifications',
                                                'area_id',
                                                'status',
                                                'resolution',
                                                'user_name',
                                                'password',
                                                'base_image_end_point',
                                                'frame_rate',
                                                'max_height',
                                                'max_width',
                                                'health',
                                                'last_active',
                                                'last_checked',
                                                'asset_description',
                                                'updated_at',
                                                'created_at',
                                                'stream_1',
                                                'stream_2',
                                                'camera_status',
                                                'analytics_applied',
                                                'port_lan'],
                                    'columns_map': {'area_id': 'm_area'},
                                    'insert_query': 'insert into m_camera (ip, rtsp_link, name, owner, description, model, roi1, roi2, roi3, roi4, roi5, specifications, area_id, status, resolution, user_name, password, base_image_end_point, frame_rate, max_height, max_width, health, last_active, last_checked, asset_description, updated_at, created_at, stream_1, stream_2, camera_status, analytics_applied, port_lan) values '},
                       'm_feature_roi': {'table_name': 'm_feature_roi',
                                         'query': "select * from m_feature_roi where camera_id in ({camera_ids})".format(camera_ids=self.camera_ids),
                                         'columns': ['camera_id', 'roi_json'],
                                         'columns_map': {'camera_id': 'm_camera'},
                                         'insert_query': 'insert into m_feature_roi (camera_id, roi_json) values '},
                       'm_event_type': {'table_name': 'm_event_type',
                                        'query': 'select * from m_event_type',
                                        'columns': ['name', 'description'],
                                        'insert_query': 'insert into m_event_type (name, description) values '},
                       't_event': {'table_name': 't_event',
                                   # 'query':  "select * from t_event where camera_id in ({camera_ids})".format(camera_ids=self.camera_ids),
                                   'query': "",
                                   'columns': ['type_id',
                                               'image_end_point',
                                               'start_datetime',
                                               'end_datetime',
                                               'camera_id',
                                               'iot_event_id',
                                               'event_json',
                                               'severity',
                                               'rule_id',
                                               'updated_at',
                                               'created_at',
                                               'status'],
                                   'columns_map': {'camera_id': 'm_camera', 'type_id': 'm_event_type'},
                                   'insert_query': 'insert into t_event (type_id, image_end_point, start_datetime, end_datetime, camera_id, iot_event_id, event_json, severity, rule_id, updated_at, created_at, status) values '},
                       'm_state': {'table_name': 'm_state',
                                   'query': 'select * from m_state',
                                   'columns': ['name', 'action'],
                                   'insert_query': 'insert into m_state (name, action) values '},
                       't_media': {'table_name': 't_media',
                                   'query': '',
                                   'columns': ['cam_id',
                                               'capture_start_datetime',
                                               'capture_end_datetime',
                                               'video_upload_start_datetime',
                                               'video_upload_end_datetime',
                                               'video_end_point',
                                               'video_upload_source',
                                               'video_upload_source_id',
                                               'state_id',
                                               'image_end_point',
                                               'remarks',
                                               'partial_save_end_point',
                                               'annotation_end_point',
                                               'video_filename'],
                                   'columns_map': {'cam_id': 'm_camera', 'state_id': 'm_state'},
                                   'insert_query': 'insert into t_media (cam_id, capture_start_datetime, capture_end_datetime, video_upload_start_datetime, video_upload_end_datetime, video_end_point, video_upload_source, video_upload_source_id, state_id, image_end_point, remarks, partial_save_end_point, annotation_end_point, video_filename) values '},
                       't_media_durations': {'table_name': 't_media_durations',
                                             'query': '',
                                             'columns': ['media_status_id',
                                                         'start_time',
                                                         'end_time',
                                                         'image_count',
                                                         'remark',
                                                         'media_end_point',
                                                         'extraction_status'],
                                             'columns_map': {'media_status_id': 't_media'},
                                             'insert_query': 'insert into t_media_durations (media_status_id, start_time, end_time, image_count, remark, media_end_point, extraction_status) values '},
                       'm_tags': {'table_name': 'm_tags',
                                  'query': 'select * from m_tags',
                                  'columns': ['name', 'status'],
                                  'insert_query': 'insert into m_tags (name, status) values '},
                       'media_tags_mapping': {'table_name': 'media_tags_mapping',
                                              'query': '',
                                              'columns': ['media_duration_id', 'tag_id', 'status'],
                                              'insert_query': 'insert into media_tags_mapping (media_duration_id, tag_id, status) values '},
                       'm_rule_kind': {'table_name': 'm_rule_kind',
                                       'query': 'select * from m_rule_kind',
                                       'columns': ['name', 'kind_type', 'major_class', 'minor_class'],
                                       'insert_query': 'insert into m_rule_kind (name, kind_type, major_class, minor_class) values '},
                       'm_rule_type': {'table_name': 'm_rule_type',
                                       'query': 'select * from m_rule_type',
                                       'columns': ['type', 'rule_descripion'],
                                       'insert_query': 'insert into m_rule_type (type, rule_descripion) values '},
                       'm_model_type': {'table_name': 'm_model_type',
                                        'query': 'select * from m_model_type',
                                        'columns': ['name', 'conv_end_point'],
                                        'insert_query': 'insert into m_model_type (name, conv_end_point) values '},
                       'm_model': {'table_name': 'm_model',
                                   'query': 'select * from m_model',
                                   'columns': ['name',
                                               'end_point',
                                               'model_type_id',
                                               'model_category',
                                               'number_of_instance'],
                                   'columns_map': {'model_type_id': 'm_model_type'},
                                   'insert_query': 'insert into m_model (name, end_point, model_type_id, model_category, number_of_instance) values '},
                       'm_operator': {'table_name': 'm_operator',
                                      'query': 'select * from m_operator',
                                      'columns': ['name'],
                                      'insert_query': 'insert into m_operator (name) values '},
                       'm_product': {'table_name': 'm_product',
                                     'query': 'select * from m_product where entity_id = {entity_id}'.format(entity_id=self.entity_id),
                                     'columns': ['code', 'name', 'start_date', 'end_date', 'entity_id', 'status'],
                                     'insert_query': 'insert into m_product (code, name, start_date, end_date, entity_id, status) values '},
                       'm_configuration': {'table_name': 'm_configuration',
                                           'query': '',
                                           'columns': ['configuration', 'value', 'product_id', 'status'],
                                           'insert_query': 'insert into m_configuration (configuration, value, product_id, status) values '},
                       'm_feature_category': {'table_name': 'm_feature_category',
                                              'query': 'select * from m_feature_category',
                                              'columns': ['name'],
                                              'insert_query': 'insert into m_feature_category (name) values '},
                       'm_feature': {'table_name': 'm_feature',
                                     'query': "select * from m_feature where product_id = {product_id}".format(product_id=self.product_id),
                                     'columns': ['name',
                                                 'description',
                                                 'product_id',
                                                 'status',
                                                 'category_id',
                                                 'updated_at',
                                                 'created_at'],
                                     'columns_map': {'category_id': 'm_feature_category'},
                                     'insert_query': 'insert into m_feature (name, description, product_id, status, category_id, updated_at, created_at) values '},
                       'm_rule': {'table_name': 'm_rule',
                                  'query': '',
                                  'columns': ['feature_id',
                                              'tag_id',
                                              'rule_id',
                                              'operator_id',
                                              'Value',
                                              'model_id',
                                              'tag_type',
                                              'rule_kind_id',
                                              'camera_id'],
                                  'insert_query': 'insert into m_rule (feature_id, tag_id, rule_id, operator_id, Value, model_id, tag_type, rule_kind_id, camera_id) values '},
                       'camera_feature_mapping': {'table_name': 'camera_feature_mapping',
                                                  'query': '',
                                                  'columns': ['feature_id',
                                                              'camera_id',
                                                              'status',
                                                              'alert',
                                                              'updated_at',
                                                              'created_at'],
                                                  'insert_query': 'insert into camera_feature_mapping (feature_id, camera_id, status, alert, updated_at, created_at) values '}}

    def get_edge(self, edge_id):
        sql = '''select ip, location_id, synch_duration_hrs from m_edge where id = '{edge_id}' '''.format(edge_id=edge_id)
        rows, no_of_rows = self.connect.query_database(sql=sql)
        if no_of_rows > 0:
            return rows[0][0], rows[0][1], rows[0][2]

    def get_entity(self, location_id):
        sql = '''select name, code, entity_id from m_location where id = '{location_id}' '''.format(location_id=location_id)
        rows, no_of_rows = self.connect.query_database(sql=sql)
        if no_of_rows > 0:
            location_name, location_code, entity_id = rows[0][0], rows[0][1], rows[0][2]
            sql = '''select name, code from m_entity where id = '{entity_id}' '''.format(entity_id=entity_id)
            rows, no_of_rows = self.connect.query_database(sql=sql)
            if no_of_rows > 0:
                entity_name, entity_code = rows[0][0], rows[0][1]
                return location_name, location_code, entity_id, entity_name, entity_code

    def get_product(self, entity_id):
        sql = '''select id, name from m_product where entity_id = '{entity_id}' '''.format(entity_id=entity_id)
        rows, no_of_rows = self.connect.query_database(sql=sql)
        if no_of_rows > 0:
            return rows[0][0], rows[0][1]

    def get_area_ids(self, location_id):
        sql = '''select id from m_area where location_id = {location_id} '''.format(location_id=location_id)
        rows, no_of_rows = self.connect.query_database(sql=sql)
        if no_of_rows > 0:
            return ",".join([str(row[0]) for row in rows])

    def get_camera_ids(self, area_ids):
        sql = '''select id from m_camera where area_id in ({area_ids}) '''.format(area_ids=area_ids)
        rows, no_of_rows = self.connect.query_database(sql=sql)
        if no_of_rows > 0:
            return ",".join([str(row[0]) for row in rows])

    def create_dump(self):
        dump_inserts = {}
        for table_index in self.tables:
            if self.tables[table_index]['query'] == '':
                dump_inserts[self.tables[table_index]['table_name']] = ''
            else:
                table = self.connect.query_database_df(sql=self.tables[table_index]['query'])
                table = table.replace({np.nan: None})
                self.tables[table_index]['id_mapper'] = {str(rwx['id']): idx + 1 for idx, rwx in table.iterrows()}
                print(table_index)
                if 'columns_map' in self.tables[table_index]:
                    for column in self.tables[table_index]['columns_map']:
                        print(column)
                        print(table[column])
                        table[column] = [self.tables[self.tables[table_index]['columns_map'][column]]['id_mapper'][str(rwx[column])] for idx, rwx in table.iterrows()]
                insert_query = self.tables[table_index]['insert_query']
                values_list = []
                insert_final_query = ''
                for idx, rwx in table.iterrows():
                    values_list.append('(' + ','.join([(str(rwx[column]) if rwx[column] else 'null') if not isinstance(rwx[column], (str, datetime, date)) else "'" + str(rwx[column]) + "'" for column in self.tables[table_index]['columns']]) + ')')
                while len(values_list) >= 999:
                    insert_sub_query = insert_query + ", ".join(values_list[:999])
                    values_list = values_list[999:]
                    insert_final_query = insert_final_query + insert_sub_query + '\nr'
                if len(values_list) != 0:
                    insert_sub_query = insert_query + ", ".join(values_list)
                    insert_final_query = insert_final_query + insert_sub_query + '\n'
                    dump_inserts[self.tables[table_index]['table_name']] = insert_final_query
                else:
                    if insert_final_query == '':
                        dump_inserts[self.tables[table_index]['table_name']] = ''
                    else:
                        dump_inserts[self.tables[table_index]['table_name']] = insert_final_query
        print(dump_inserts)
        self.dump = self.dump.format(**dump_inserts)
        with open(os.path.join(BASE_DIR, 'mysql/ZestIot_AppliedAI_0.sql'), 'w') as fo:
            fo.write(self.dump)


mysql_dump = MysqlDump()
mysql_dump.create_dump()
