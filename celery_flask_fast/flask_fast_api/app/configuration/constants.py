import logging
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
print(BASE_DIR)
api_v2_cors_config = {"origins": ["*"],
                      "methods": ["OPTIONS", "GET", "POST", "DELETE"],
                      "allow_headers": ["Authorization", "Content-Type", "user-id", "key", "entity-location"],
                      "exposedHeaders": "Access-Control-Allow-Origin"}
flask_utility_configuration = {"debug": 1,
                               "log_file": 'flask.log',
                               "mode": 1,
                               "enable_db": True,
                               "enable_redis": True,
                               "enable_rabbitmq_consumer": False,
                               "enable_rabbitmq_publisher": True,
                               "redis_db": 1,
                               "log_level": logging.DEBUG,
                               "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                               "database": "ZestIot_AppliedAI",
                               "server": ''}

dump_configuration = {"debug": 1,
                      "log_file": 'mysql_dump.log',
                      "mode": 1,
                      "enable_db": True,
                      "enable_redis": True,
                      "enable_rabbitmq_consumer": False,
                      "enable_rabbitmq_publisher": False,
                      "redis_db": 0,
                      "log_level": logging.DEBUG,
                      "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                      "database": "ZestIot_AppliedAI_HQ",
                      "server": ''}

fast_api_utility_configuration = {"debug": 1,
                                  "log_file": 'fast_api.log',
                                  "mode": 1,
                                  "enable_db": False,
                                  "enable_redis": True,
                                  "enable_rabbitmq_consumer": False,
                                  "enable_rabbitmq_publisher": True,
                                  "redis_db": 1,
                                  "log_level": logging.DEBUG,
                                  "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                                  "database": "ZestIot_AppliedAI",
                                  "server": ''}
fast_api_publisher = {"exchange": "Task", "routing_key": "task.#", "exchange_type": 'topic', "durable": 'False'}

celery_configuration = {"debug": 1,
                        "log_file": 'celery.log',
                        "mode": 1,
                        "enable_db": True,
                        "enable_redis": False,
                        "enable_rabbitmq_consumer": False,
                        "enable_rabbitmq_publisher": True,
                        "redis_db": 8,
                        "log_level": logging.DEBUG,
                        "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                        "database": "ZestIot_AppliedAI",
                        "server": ''}
celery_rabbitmq_publisher = {"exchange": "Task", "routing_key": "task.{}.{}.#", "exchange_type": 'topic', "durable": 'False'}

hq_flask_utility_configuration = {"debug": 1,
                                  "log_file": 'flask.log',
                                  "mode": 1,
                                  "enable_db": False,
                                  "enable_redis": False,
                                  "enable_rabbitmq_consumer": False,
                                  "enable_rabbitmq_publisher": True,
                                  "redis_db": 0,
                                  "log_level": logging.DEBUG,
                                  "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                                  "database": "ZestIot_AppliedAI",
                                  "server": '_HQ'}
video_feed_utility_configuration = {"debug": 1,
                                    "log_file": 'video_feed.log',
                                    "mode": 1,
                                    "enable_db": False,
                                    "enable_redis": False,
                                    "enable_rabbitmq_consumer": False,
                                    "enable_rabbitmq_publisher": False,
                                    "redis_db": 0,
                                    "log_level": logging.DEBUG,
                                    "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                                    "database": "ZestIot_AppliedAI",
                                    "server": ''}
user_utility_configuration = {"debug": 1,
                              "log_file": 'user_login.log',
                              "mode": 1,
                              "enable_db": False,
                              "enable_redis": True,
                              "enable_rabbitmq_consumer": False,
                              "enable_rabbitmq_publisher": False,
                              "redis_db": 0,
                              "log_level": logging.DEBUG,
                              "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                              "database": "ZestIot_AppliedAI",
                              "server": ''}
camera_subscriber_feed_configuration = {"debug": 1,
                                  "log_file": 'consumer_feed.log',
                                  "mode": 1,
                                  "enable_db": True,
                                  "enable_redis": True,
                                  "enable_rabbitmq_consumer": True,
                                  "enable_rabbitmq_publisher": True,
                                  "arguments": {'x-max-length': 100},
                                  "redis_db": 1,
                                  "log_level": logging.DEBUG,
                                  "config_file_path": os.path.join(BASE_DIR, "configuration/config.json"),
                                  "database": "ZestIot_AppliedAI",
                       "server": ''}


rabbitmq_publisher = {"exchange": "Event", "routing_key": "train.#", "exchange_type": 'topic', "durable": 'False'}
hq_rabbitmq_publisher = {"exchange": "Event", "routing_key": "edge_status.#", "exchange_type": 'topic', "durable": 'False', "rabbitmq_host": ''}
edge_rabbitmq_publisher = {"exchange": "Event", "routing_key": "hq_status.#", "exchange_type": 'topic', "durable": 'False', "rabbitmq_host": ''}
camera_subscriber_rabbitmq_feed_consumer = {"exchange": "Feed", "routing_keys": {}, "exchange_type": 'topic', "durable": 'False', "queue": "camera_video_feed"}

