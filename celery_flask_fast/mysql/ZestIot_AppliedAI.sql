--
-- Table structure for table `m_user_session`
--

DROP TABLE IF EXISTS `m_user_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_user_session` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_key` varchar(255) CHARACTER SET utf8mb4 DEFAULT NULL,
  `user_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_key`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_user_session`
--

LOCK TABLES `m_user_session` WRITE;
/*!40000 ALTER TABLE `m_user_session` DISABLE KEYS */;
{m_user_session};
/*!40000 ALTER TABLE `m_user_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_department`
--

DROP TABLE IF EXISTS `m_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_department` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_department`
--

LOCK TABLES `m_department` WRITE;
/*!40000 ALTER TABLE `m_department` DISABLE KEYS */;
{m_department};
/*!40000 ALTER TABLE `m_department` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `m_designation`
--

DROP TABLE IF EXISTS `m_designation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_designation` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_designation`
--

LOCK TABLES `m_designation` WRITE;
/*!40000 ALTER TABLE `m_designation` DISABLE KEYS */;
{m_designation};
/*!40000 ALTER TABLE `m_designation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_roles_permissions`
--

DROP TABLE IF EXISTS `m_roles_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_roles_permissions` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `access_rules` text,
  `role_name` varchar(100) DEFAULT NULL,
  `department_id` int unsigned DEFAULT NULL,
  `designation_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `m_roles_permissions_FK` (`designation_id`),
  KEY `m_roles_permissions_FK_1` (`department_id`),
  CONSTRAINT `m_roles_permissions_FK` FOREIGN KEY (`designation_id`) REFERENCES `m_designation` (`id`),
  CONSTRAINT `m_roles_permissions_FK_1` FOREIGN KEY (`department_id`) REFERENCES `m_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_roles_permissions`
--

LOCK TABLES `m_roles_permissions` WRITE;
/*!40000 ALTER TABLE `m_roles_permissions` DISABLE KEYS */;
{m_roles_permissions};
/*!40000 ALTER TABLE `m_roles_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_location_type`
--

DROP TABLE IF EXISTS `m_location_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_location_type` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_location_type`
--

LOCK TABLES `m_location_type` WRITE;
/*!40000 ALTER TABLE `m_location_type` DISABLE KEYS */;
{m_location_type};
/*!40000 ALTER TABLE `m_location_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_entity`
--

DROP TABLE IF EXISTS `m_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_entity` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `code` varchar(45) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_entity`
--

LOCK TABLES `m_entity` WRITE;
/*!40000 ALTER TABLE `m_entity` DISABLE KEYS */;
{m_entity};
/*!40000 ALTER TABLE `m_entity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_location`
--

DROP TABLE IF EXISTS `m_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_location` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) DEFAULT NULL,
  `code` varchar(45) DEFAULT NULL,
  `address` mediumtext,
  `city` varchar(20) DEFAULT NULL,
  `pincode` varchar(20) DEFAULT NULL,
  `state` varchar(20) DEFAULT NULL,
  `country` varchar(20) DEFAULT NULL,
  `entity_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_FK` (`entity_id`),
  KEY `configuration_FK` (`city`) USING BTREE,
  CONSTRAINT `location_FK` FOREIGN KEY (`entity_id`) REFERENCES `m_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_location`
--

LOCK TABLES `m_location` WRITE;
/*!40000 ALTER TABLE `m_location` DISABLE KEYS */;
{m_location};
/*!40000 ALTER TABLE `m_location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location_mapping`
--

DROP TABLE IF EXISTS `location_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location_mapping` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `location_type_id` int unsigned DEFAULT NULL,
  `location_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_mapping_FK` (`location_id`),
  KEY `location_mapping_FK_1` (`location_type_id`),
  CONSTRAINT `location_mapping_FK` FOREIGN KEY (`location_id`) REFERENCES `m_location` (`id`),
  CONSTRAINT `location_mapping_FK_1` FOREIGN KEY (`location_type_id`) REFERENCES `m_location_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location_mapping`
--

LOCK TABLES `location_mapping` WRITE;
/*!40000 ALTER TABLE `location_mapping` DISABLE KEYS */;
{location_mapping};
/*!40000 ALTER TABLE `location_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_user_profile`
--

DROP TABLE IF EXISTS `m_user_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_user_profile` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `full_name` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `login_name` varchar(20) DEFAULT NULL,
  `password` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `entity_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `role_id` int unsigned DEFAULT NULL,
  `employee_id` varchar(10) DEFAULT NULL,
  `gender` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `location_id` int unsigned DEFAULT NULL,
  `user_login_type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `m_user_profile_UN` (`login_name`),
  KEY `user_profile_FK` (`entity_id`),
  KEY `m_user_profile_FK` (`role_id`),
  KEY `m_user_profile_FK_1` (`location_id`),
  CONSTRAINT `m_user_profile_FK` FOREIGN KEY (`role_id`) REFERENCES `m_roles_permissions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `m_user_profile_FK_1` FOREIGN KEY (`location_id`) REFERENCES `m_location` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `user_profile_FK` FOREIGN KEY (`entity_id`) REFERENCES `m_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_user_profile`
--

LOCK TABLES `m_user_profile` WRITE;
/*!40000 ALTER TABLE `m_user_profile` DISABLE KEYS */;
{m_user_profile};
/*!40000 ALTER TABLE `m_user_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_user_group`
--

DROP TABLE IF EXISTS `m_user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_user_group` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) DEFAULT NULL,
  `created_by` varchar(50) DEFAULT NULL,
  `created_on` date DEFAULT NULL,
  `entity_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `configuration_FK` (`created_on`) USING BTREE,
  KEY `location_FK` (`entity_id`) USING BTREE,
  CONSTRAINT `user_group_FK` FOREIGN KEY (`entity_id`) REFERENCES `m_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_user_group`
--

LOCK TABLES `m_user_group` WRITE;
/*!40000 ALTER TABLE `m_user_group` DISABLE KEYS */;
{m_user_group};
/*!40000 ALTER TABLE `m_user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_mapping`
--

DROP TABLE IF EXISTS `user_group_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_mapping` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int unsigned DEFAULT NULL,
  `group_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_mapping_FK` (`group_id`) USING BTREE,
  KEY `location_mapping_FK_1` (`user_id`) USING BTREE,
  CONSTRAINT `user_group_mapping_FK` FOREIGN KEY (`group_id`) REFERENCES `m_user_group` (`id`),
  CONSTRAINT `user_group_mapping_FK_1` FOREIGN KEY (`user_id`) REFERENCES `m_user_profile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_mapping`
--

LOCK TABLES `user_group_mapping` WRITE;
/*!40000 ALTER TABLE `user_group_mapping` DISABLE KEYS */;
{user_group_mapping};
/*!40000 ALTER TABLE `user_group_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_group_permission`
--

DROP TABLE IF EXISTS `m_group_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_group_permission` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `group_id` int unsigned DEFAULT NULL,
  `permissions` mediumtext,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_permission_FK` (`group_id`),
  CONSTRAINT `group_permission_FK` FOREIGN KEY (`group_id`) REFERENCES `m_user_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_group_permission`
--

LOCK TABLES `m_group_permission` WRITE;
/*!40000 ALTER TABLE `m_group_permission` DISABLE KEYS */;
{m_group_permission};
/*!40000 ALTER TABLE `m_group_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_access_views`
--

DROP TABLE IF EXISTS `m_access_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_access_views` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_access_views`
--

LOCK TABLES `m_access_views` WRITE;
/*!40000 ALTER TABLE `m_access_views` DISABLE KEYS */;
{m_access_views};
/*!40000 ALTER TABLE `m_access_views` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_edge`
--

DROP TABLE IF EXISTS `m_edge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_edge` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `location_id` int unsigned DEFAULT NULL,
  `synch_duration_hrs` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `m_edge_FK` (`location_id`),
  CONSTRAINT `m_edge_FK` FOREIGN KEY (`location_id`) REFERENCES `m_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 ;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_edge`
--

LOCK TABLES `m_edge` WRITE;
/*!40000 ALTER TABLE `m_edge` DISABLE KEYS */;
{m_edge};
/*!40000 ALTER TABLE `m_edge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_area`
--

DROP TABLE IF EXISTS `m_area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_area` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `location_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `area_FK` (`location_id`),
  CONSTRAINT `area_FK` FOREIGN KEY (`location_id`) REFERENCES `m_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_area`
--

LOCK TABLES `m_area` WRITE;
/*!40000 ALTER TABLE `m_area` DISABLE KEYS */;
{m_area};
/*!40000 ALTER TABLE `m_area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_camera`
--

DROP TABLE IF EXISTS `m_camera`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_camera` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(200) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `rtsp_link` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `name` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `owner` varchar(50) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `model` varchar(45) DEFAULT NULL,
  `roi1` varchar(45) DEFAULT NULL,
  `roi2` varchar(45) DEFAULT NULL,
  `roi3` varchar(45) DEFAULT NULL,
  `roi4` varchar(45) DEFAULT NULL,
  `roi5` varchar(45) DEFAULT NULL,
  `specifications` mediumtext,
  `area_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `resolution` varchar(100) DEFAULT NULL,
  `user_name` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `base_image_end_point` mediumtext,
  `frame_rate` int unsigned DEFAULT NULL,
  `max_height` int unsigned DEFAULT NULL,
  `max_width` int unsigned DEFAULT NULL,
  `health` varchar(100) DEFAULT NULL,
  `last_active` datetime DEFAULT NULL,
  `last_checked` datetime DEFAULT NULL,
  `asset_description` varchar(100) DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `stream_1` varchar(100) DEFAULT NULL,
  `stream_2` varchar(100) DEFAULT NULL,
  `camera_status` varchar(45) DEFAULT NULL,
  `analytics_applied` varchar(45) DEFAULT NULL,
  `port_lan` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `camera_FK_1` (`area_id`),
  CONSTRAINT `camera_FK_1` FOREIGN KEY (`area_id`) REFERENCES `m_area` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_camera`
--

LOCK TABLES `m_camera` WRITE;
/*!40000 ALTER TABLE `m_camera` DISABLE KEYS */;
{m_camera};
/*!40000 ALTER TABLE `m_camera` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `m_feature_roi`
--

DROP TABLE IF EXISTS `m_feature_roi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_feature_roi` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `camera_id` int unsigned DEFAULT NULL,
  `roi_json` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `m_feature_roi_FK` (`camera_id`),
  CONSTRAINT `m_feature_roi_FK` FOREIGN KEY (`camera_id`) REFERENCES `m_camera` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_feature_roi`
--

LOCK TABLES `m_feature_roi` WRITE;
/*!40000 ALTER TABLE `m_feature_roi` DISABLE KEYS */;
{m_feature_roi};
/*!40000 ALTER TABLE `m_feature_roi` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `m_event_type`
--

DROP TABLE IF EXISTS `m_event_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_event_type` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) DEFAULT NULL,
  `description` mediumtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_event_type`
--

LOCK TABLES `m_event_type` WRITE;
/*!40000 ALTER TABLE `m_event_type` DISABLE KEYS */;
{m_event_type};
/*!40000 ALTER TABLE `m_event_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_state`
--

DROP TABLE IF EXISTS `m_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_state` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'annotation_class_tag_mapping',
  `action` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_state`
--

LOCK TABLES `m_state` WRITE;
/*!40000 ALTER TABLE `m_state` DISABLE KEYS */;
{m_state};
/*!40000 ALTER TABLE `m_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_media`
--

DROP TABLE IF EXISTS `t_media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_media` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `cam_id` int unsigned DEFAULT NULL,
  `capture_start_datetime` datetime DEFAULT NULL,
  `capture_end_datetime` datetime DEFAULT NULL,
  `video_upload_start_datetime` datetime DEFAULT NULL,
  `video_upload_end_datetime` datetime DEFAULT NULL,
  `video_end_point` mediumtext,
  `video_upload_source` varchar(50) DEFAULT NULL,
  `video_upload_source_id` varchar(50) DEFAULT NULL,
  `state_id` int unsigned DEFAULT NULL,
  `image_end_point` mediumtext,
  `remarks` mediumtext,
  `partial_save_end_point` mediumtext CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `annotation_end_point` mediumtext,
  `video_filename` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `video_asset_FK` (`cam_id`),
  KEY `media_FK` (`state_id`),
  CONSTRAINT `media_FK` FOREIGN KEY (`state_id`) REFERENCES `m_state` (`id`),
  CONSTRAINT `video_asset_FK` FOREIGN KEY (`cam_id`) REFERENCES `m_camera` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_media`
--

LOCK TABLES `t_media` WRITE;
/*!40000 ALTER TABLE `t_media` DISABLE KEYS */;
{t_media};
/*!40000 ALTER TABLE `t_media` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_media_durations`
--

DROP TABLE IF EXISTS `t_media_durations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_media_durations` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `media_status_id` int unsigned DEFAULT NULL,
  `start_time` varchar(20) DEFAULT NULL,
  `end_time` varchar(20) DEFAULT NULL,
  `image_count` int unsigned DEFAULT NULL,
  `remark` mediumtext,
  `media_end_point` varchar(100) DEFAULT NULL,
  `extraction_status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `media_extraction_mapping_FK` (`media_status_id`),
  CONSTRAINT `media_extraction_mapping_FK` FOREIGN KEY (`media_status_id`) REFERENCES `t_media` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_media_durations`
--

LOCK TABLES `t_media_durations` WRITE;
/*!40000 ALTER TABLE `t_media_durations` DISABLE KEYS */;
{t_media_durations};
/*!40000 ALTER TABLE `t_media_durations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_tags`
--

DROP TABLE IF EXISTS `m_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tags` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_tags`
--

LOCK TABLES `m_tags` WRITE;
/*!40000 ALTER TABLE `m_tags` DISABLE KEYS */;
{m_tags};
/*!40000 ALTER TABLE `m_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_tags_mapping`
--

DROP TABLE IF EXISTS `media_tags_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media_tags_mapping` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `media_duration_id` int unsigned DEFAULT NULL,
  `tag_id` int unsigned DEFAULT NULL,
  `status` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_mapping_FK` (`tag_id`) USING BTREE,
  KEY `location_mapping_FK_1` (`media_duration_id`) USING BTREE,
  CONSTRAINT `media_tags_mapping_FK` FOREIGN KEY (`media_duration_id`) REFERENCES `t_media_durations` (`id`),
  CONSTRAINT `media_tags_mapping_FK_1` FOREIGN KEY (`tag_id`) REFERENCES `m_tags` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_tags_mapping`
--

LOCK TABLES `media_tags_mapping` WRITE;
/*!40000 ALTER TABLE `media_tags_mapping` DISABLE KEYS */;
{media_tags_mapping};
/*!40000 ALTER TABLE `media_tags_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_rule_kind`
--

DROP TABLE IF EXISTS `m_rule_kind`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_rule_kind` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `kind_type` varchar(100) DEFAULT NULL,
  `major_class` varchar(100) DEFAULT NULL,
  `minor_class` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_rule_kind`
--

LOCK TABLES `m_rule_kind` WRITE;
/*!40000 ALTER TABLE `m_rule_kind` DISABLE KEYS */;
{m_rule_kind};
/*!40000 ALTER TABLE `m_rule_kind` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_rule_type`
--

DROP TABLE IF EXISTS `m_rule_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_rule_type` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  `rule_descripion` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_rule_type`
--

LOCK TABLES `m_rule_type` WRITE;
/*!40000 ALTER TABLE `m_rule_type` DISABLE KEYS */;
{m_rule_type};
/*!40000 ALTER TABLE `m_rule_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_model_type`
--

DROP TABLE IF EXISTS `m_model_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_model_type` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 NOT NULL,
  `conv_end_point` mediumtext CHARACTER SET utf8mb4,
  PRIMARY KEY (`id`),
  UNIQUE KEY `m_model_UN` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_model_type`
--

LOCK TABLES `m_model_type` WRITE;
/*!40000 ALTER TABLE `m_model_type` DISABLE KEYS */;
{m_model_type};
/*!40000 ALTER TABLE `m_model_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_model`
--

DROP TABLE IF EXISTS `m_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_model` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 NOT NULL,
  `end_point` mediumtext CHARACTER SET utf8mb4,
  `model_type_id` int unsigned DEFAULT NULL,
  `model_category` varchar(30) DEFAULT NULL,
  `number_of_instance` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `m_model_UN` (`name`),
  KEY `m_model_FK` (`model_type_id`),
  CONSTRAINT `m_model_FK` FOREIGN KEY (`model_type_id`) REFERENCES `m_model_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_model`
--

LOCK TABLES `m_model` WRITE;
/*!40000 ALTER TABLE `m_model` DISABLE KEYS */;
{m_model};
/*!40000 ALTER TABLE `m_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_operator`
--

DROP TABLE IF EXISTS `m_operator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_operator` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(10) CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_operator`
--

LOCK TABLES `m_operator` WRITE;
/*!40000 ALTER TABLE `m_operator` DISABLE KEYS */;
{m_operator};
/*!40000 ALTER TABLE `m_operator` ENABLE KEYS */;
UNLOCK TABLES;

-- Table structure for table `m_product`
--

DROP TABLE IF EXISTS `m_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_product` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `name` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `entity_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_FK` (`entity_id`),
  CONSTRAINT `project_FK` FOREIGN KEY (`entity_id`) REFERENCES `m_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_product`
--

LOCK TABLES `m_product` WRITE;
/*!40000 ALTER TABLE `m_product` DISABLE KEYS */;
{m_product};
/*!40000 ALTER TABLE `m_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_configuration`
--

DROP TABLE IF EXISTS `m_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_configuration` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `configuration` varchar(20) DEFAULT NULL,
  `value` varchar(50) DEFAULT NULL,
  `product_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `configuration_FK` (`product_id`),
  CONSTRAINT `configuration_FK` FOREIGN KEY (`product_id`) REFERENCES `m_product` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_configuration`
--

LOCK TABLES `m_configuration` WRITE;
/*!40000 ALTER TABLE `m_configuration` DISABLE KEYS */;
{m_configuration};
/*!40000 ALTER TABLE `m_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_feature_category`
--

DROP TABLE IF EXISTS `m_feature_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_feature_category` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_feature_category`
--

LOCK TABLES `m_feature_category` WRITE;
/*!40000 ALTER TABLE `m_feature_category` DISABLE KEYS */;
{m_feature_category};
/*!40000 ALTER TABLE `m_feature_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_feature`
--

DROP TABLE IF EXISTS `m_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_feature` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `description` mediumtext,
  `product_id` int unsigned DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `category_id` int unsigned DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ai_model_FK` (`product_id`),
  KEY `m_feature_FK` (`category_id`),
  CONSTRAINT `ai_model_FK` FOREIGN KEY (`product_id`) REFERENCES `m_product` (`id`),
  CONSTRAINT `m_feature_FK` FOREIGN KEY (`category_id`) REFERENCES `m_feature_category` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_feature`
--

LOCK TABLES `m_feature` WRITE;
/*!40000 ALTER TABLE `m_feature` DISABLE KEYS */;
{m_feature};
/*!40000 ALTER TABLE `m_feature` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `m_rule`
--

DROP TABLE IF EXISTS `m_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_rule` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `feature_id` int unsigned DEFAULT NULL,
  `tag_id` int unsigned DEFAULT NULL,
  `rule_id` int unsigned DEFAULT NULL,
  `operator_id` int unsigned DEFAULT NULL,
  `Value` varchar(100) DEFAULT NULL,
  `model_id` int unsigned DEFAULT NULL,
  `tag_type` varchar(100) DEFAULT NULL,
  `rule_kind_id` int unsigned DEFAULT NULL,
  `camera_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `feature_rule_mapping_FK` (`feature_id`),
  KEY `feature_rule_mapping_FK_1` (`tag_id`),
  KEY `feature_rule_mapping_FK_2` (`rule_id`),
  KEY `feature_rule_mapping_FK_3` (`operator_id`),
  KEY `m_rule_FK` (`model_id`),
  KEY `m_rule_FK_1` (`rule_kind_id`),
  KEY `m_rule_FK_2` (`camera_id`),
  CONSTRAINT `feature_rule_mapping_FK` FOREIGN KEY (`feature_id`) REFERENCES `m_feature` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `feature_rule_mapping_FK_1` FOREIGN KEY (`tag_id`) REFERENCES `m_tags` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `feature_rule_mapping_FK_2` FOREIGN KEY (`rule_id`) REFERENCES `m_rule_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `feature_rule_mapping_FK_3` FOREIGN KEY (`operator_id`) REFERENCES `m_operator` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `m_rule_FK` FOREIGN KEY (`model_id`) REFERENCES `m_model` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `m_rule_FK_1` FOREIGN KEY (`rule_kind_id`) REFERENCES `m_rule_kind` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `m_rule_FK_2` FOREIGN KEY (`camera_id`) REFERENCES `m_camera` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_rule`
--

LOCK TABLES `m_rule` WRITE;
/*!40000 ALTER TABLE `m_rule` DISABLE KEYS */;
{m_rule};
/*!40000 ALTER TABLE `m_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `camera_feature_mapping`
--

DROP TABLE IF EXISTS `camera_feature_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `camera_feature_mapping` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `feature_id` int unsigned DEFAULT NULL,
  `camera_id` int unsigned DEFAULT NULL,
  `status` tinyint DEFAULT NULL,
  `alert` tinyint DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_mapping_FK` (`camera_id`) USING BTREE,
  KEY `location_mapping_FK_1` (`feature_id`) USING BTREE,
  CONSTRAINT `camera_ai_model_mapping_FK` FOREIGN KEY (`feature_id`) REFERENCES `m_feature` (`id`),
  CONSTRAINT `camera_ai_model_mapping_FK_1` FOREIGN KEY (`camera_id`) REFERENCES `m_camera` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camera_feature_mapping`
--

LOCK TABLES `camera_feature_mapping` WRITE;
/*!40000 ALTER TABLE `camera_feature_mapping` DISABLE KEYS */;
{camera_feature_mapping};
/*!40000 ALTER TABLE `camera_feature_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_event`
--

DROP TABLE IF EXISTS `t_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_event` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `type_id` int unsigned DEFAULT NULL,
  `image_end_point` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `start_datetime` datetime DEFAULT NULL,
  `end_datetime` datetime DEFAULT NULL,
  `camera_id` int unsigned DEFAULT NULL,
  `iot_event_id` int DEFAULT NULL,
  `event_json` text,
  `severity` varchar(100) DEFAULT NULL,
  `rule_id` int unsigned DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `iot_evenet_id` (`iot_event_id`),
  KEY `event_FK` (`type_id`),
  KEY `event_FK_1` (`camera_id`),
  KEY `t_event_FK` (`rule_id`),
  CONSTRAINT `event_FK` FOREIGN KEY (`type_id`) REFERENCES `m_event_type` (`id`),
  CONSTRAINT `event_FK_1` FOREIGN KEY (`camera_id`) REFERENCES `m_camera` (`id`),
  CONSTRAINT `t_event_FK` FOREIGN KEY (`rule_id`) REFERENCES `m_rule` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_event`
--

LOCK TABLES `t_event` WRITE;
/*!40000 ALTER TABLE `t_event` DISABLE KEYS */;
{t_event};
/*!40000 ALTER TABLE `t_event` ENABLE KEYS */;
UNLOCK TABLES;