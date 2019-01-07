/*
Navicat MySQL Data Transfer

Source Server         : dbmon
Source Server Version : 50717
Source Host           : 192.168.48.50:3306
Source Database       : db_monitor

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2019-01-07 19:28:49
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for bak_conf
-- ----------------------------
DROP TABLE IF EXISTS `bak_conf`;
CREATE TABLE `bak_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `conf_no` varchar(255) DEFAULT NULL,
  `conf_name` varchar(255) DEFAULT NULL,
  `bak_type` varchar(255) DEFAULT NULL,
  `bak_begin_time` varchar(255) DEFAULT NULL,
  `bak_end_time` varchar(255) DEFAULT NULL,
  `frequency` varchar(255) DEFAULT NULL,
  `full_bak_day` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for check_info
-- ----------------------------
DROP TABLE IF EXISTS `check_info`;
CREATE TABLE `check_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `check_tag` varchar(255) DEFAULT NULL,
  `check_type` varchar(255) DEFAULT NULL,
  `server_tag` varchar(255) DEFAULT NULL,
  `check_err_type` varchar(255) DEFAULT NULL,
  `check_err` varchar(1000) DEFAULT NULL,
  `begin_time` varchar(255) DEFAULT NULL,
  `end_time` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=316 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for check_list
-- ----------------------------
DROP TABLE IF EXISTS `check_list`;
CREATE TABLE `check_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `check_tag` varchar(255) DEFAULT NULL,
  `check_type` varchar(255) DEFAULT NULL,
  `server_tag` varchar(255) DEFAULT NULL,
  `begin_time` varchar(255) DEFAULT NULL,
  `end_time` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for easy_start_conf
-- ----------------------------
DROP TABLE IF EXISTS `easy_start_conf`;
CREATE TABLE `easy_start_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `oper_type` varchar(255) DEFAULT NULL,
  `app_name` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `do_cmd` varchar(255) DEFAULT NULL,
  `process_check` varchar(255) DEFAULT NULL,
  `process_check_result` varchar(255) DEFAULT NULL,
  `check_log` varchar(255) DEFAULT NULL,
  `check_log_result` varchar(255) DEFAULT NULL,
  `oper_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for event_recorder
-- ----------------------------
DROP TABLE IF EXISTS `event_recorder`;
CREATE TABLE `event_recorder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_type` varchar(255) NOT NULL,
  `event_type_color` varchar(255) NOT NULL,
  `event_section` varchar(255) NOT NULL,
  `event_content` text NOT NULL,
  `record_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for linux_io_stat
-- ----------------------------
DROP TABLE IF EXISTS `linux_io_stat`;
CREATE TABLE `linux_io_stat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `disk` varchar(255) DEFAULT NULL,
  `rd_s` float DEFAULT NULL,
  `rd_avgkb` float DEFAULT NULL,
  `rd_m_s` float DEFAULT NULL,
  `rd_mrg_s` float DEFAULT NULL,
  `rd_cnc` float DEFAULT NULL,
  `rd_rt` float DEFAULT NULL,
  `wr_s` float DEFAULT NULL,
  `wr_avgkb` float DEFAULT NULL,
  `wr_m_s` float DEFAULT NULL,
  `wr_mrg_s` float DEFAULT NULL,
  `wr_cnc` float DEFAULT NULL,
  `wr_rt` float DEFAULT NULL,
  `busy` float DEFAULT NULL,
  `in_prg` float DEFAULT NULL,
  `io_s` float DEFAULT NULL,
  `qtime` float DEFAULT NULL,
  `stime` float DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26762 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for linux_io_stat_his
-- ----------------------------
DROP TABLE IF EXISTS `linux_io_stat_his`;
CREATE TABLE `linux_io_stat_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `disk` varchar(255) DEFAULT NULL,
  `rd_s` float DEFAULT NULL,
  `rd_avgkb` float DEFAULT NULL,
  `rd_m_s` float DEFAULT NULL,
  `rd_mrg_s` float DEFAULT NULL,
  `rd_cnc` float DEFAULT NULL,
  `rd_rt` float DEFAULT NULL,
  `wr_s` float DEFAULT NULL,
  `wr_avgkb` float DEFAULT NULL,
  `wr_m_s` float DEFAULT NULL,
  `wr_mrg_s` float DEFAULT NULL,
  `wr_cnc` float DEFAULT NULL,
  `wr_rt` float DEFAULT NULL,
  `busy` float DEFAULT NULL,
  `in_prg` float DEFAULT NULL,
  `io_s` float DEFAULT NULL,
  `qtime` float DEFAULT NULL,
  `stime` float DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26759 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for linux_net
-- ----------------------------
DROP TABLE IF EXISTS `linux_net`;
CREATE TABLE `linux_net` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `nic` varchar(255) DEFAULT NULL,
  `recv` float DEFAULT NULL,
  `send` float DEFAULT NULL,
  `check_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=187096 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for linux_net_his
-- ----------------------------
DROP TABLE IF EXISTS `linux_net_his`;
CREATE TABLE `linux_net_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `nic` varchar(255) DEFAULT NULL,
  `recv` float DEFAULT NULL,
  `send` float DEFAULT NULL,
  `check_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=187090 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for linux_rate
-- ----------------------------
DROP TABLE IF EXISTS `linux_rate`;
CREATE TABLE `linux_rate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `cpu_decute` int(11) DEFAULT NULL,
  `mem_decute` int(11) DEFAULT NULL,
  `linux_rate` int(11) DEFAULT NULL,
  `linux_rate_level` varchar(255) DEFAULT NULL,
  `linux_rate_color` varchar(255) DEFAULT NULL,
  `linux_rate_reason` varchar(255) DEFAULT NULL,
  `rate_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=911116 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for linux_rate_his
-- ----------------------------
DROP TABLE IF EXISTS `linux_rate_his`;
CREATE TABLE `linux_rate_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `cpu_decute` int(11) DEFAULT NULL,
  `mem_decute` int(11) DEFAULT NULL,
  `linux_rate` int(11) DEFAULT NULL,
  `linux_rate_level` varchar(255) DEFAULT NULL,
  `linux_rate_color` varchar(255) DEFAULT NULL,
  `linux_rate_reason` varchar(255) DEFAULT NULL,
  `rate_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for log_collect_conf
-- ----------------------------
DROP TABLE IF EXISTS `log_collect_conf`;
CREATE TABLE `log_collect_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `log_name` varchar(255) DEFAULT NULL,
  `log_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for many_logs
-- ----------------------------
DROP TABLE IF EXISTS `many_logs`;
CREATE TABLE `many_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `log_type` varchar(255) DEFAULT NULL,
  `log_info` text,
  `err_info` text,
  `log_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=149 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for my_task
-- ----------------------------
DROP TABLE IF EXISTS `my_task`;
CREATE TABLE `my_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` varchar(255) DEFAULT NULL,
  `server_type` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `oper_type` varchar(255) DEFAULT NULL,
  `task_name` varchar(255) DEFAULT NULL,
  `args` varchar(255) DEFAULT NULL,
  `result` varchar(255) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `runtime` float DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_big_table
-- ----------------------------
DROP TABLE IF EXISTS `mysql_big_table`;
CREATE TABLE `mysql_big_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `db` varchar(255) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `total` float DEFAULT NULL,
  `table_comment` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=58840 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_big_table_his
-- ----------------------------
DROP TABLE IF EXISTS `mysql_big_table_his`;
CREATE TABLE `mysql_big_table_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `db` varchar(255) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `total` float DEFAULT NULL,
  `table_comment` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=58834 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_db
-- ----------------------------
DROP TABLE IF EXISTS `mysql_db`;
CREATE TABLE `mysql_db` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `version` varchar(255) DEFAULT NULL,
  `uptime` int(11) DEFAULT NULL,
  `max_connections` varchar(255) DEFAULT NULL,
  `max_connect_errors` int(11) DEFAULT NULL,
  `threads_connected` int(11) DEFAULT NULL,
  `threads_running` int(11) DEFAULT NULL,
  `threads_created` int(11) DEFAULT NULL,
  `threads_cached` int(11) DEFAULT NULL,
  `threads_waited` int(11) DEFAULT NULL,
  `conn_rate` varchar(255) DEFAULT NULL,
  `conn_rate_level` varchar(255) DEFAULT NULL,
  `QPS` int(11) DEFAULT NULL,
  `TPS` int(11) DEFAULT NULL,
  `bytes_received` int(11) DEFAULT NULL,
  `bytes_send` int(11) DEFAULT NULL,
  `open_files_limit` int(11) DEFAULT NULL,
  `open_files` int(11) DEFAULT NULL,
  `table_open_cache` int(11) DEFAULT NULL,
  `open_tables` int(11) DEFAULT NULL,
  `key_buffer_size` float DEFAULT NULL,
  `sort_buffer_size` float DEFAULT NULL,
  `join_buffer_size` float DEFAULT NULL,
  `key_blocks_unused` int(11) DEFAULT NULL,
  `key_blocks_used` int(11) DEFAULT NULL,
  `key_blocks_not_flushed` int(11) DEFAULT NULL,
  `key_blocks_used_rate` float DEFAULT NULL,
  `key_buffer_read_rate` float DEFAULT NULL,
  `key_buffer_write_rate` float DEFAULT NULL,
  `innodb_buffer_pool_size` float DEFAULT NULL,
  `innodb_buffer_pool_pages_total` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_data` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_dirty` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_flushed` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_free` int(11) DEFAULT NULL,
  `innodb_io_capacity` int(11) DEFAULT NULL,
  `innodb_read_io_threads` int(11) DEFAULT NULL,
  `innodb_write_io_threads` int(11) DEFAULT NULL,
  `innodb_rows_deleted_persecond` int(11) DEFAULT NULL,
  `innodb_rows_inserted_persecond` int(11) DEFAULT NULL,
  `innodb_rows_read_persecond` int(11) DEFAULT NULL,
  `innodb_rows_updated_persecond` int(11) DEFAULT NULL,
  `mon_status` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=443923 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_db_his
-- ----------------------------
DROP TABLE IF EXISTS `mysql_db_his`;
CREATE TABLE `mysql_db_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `version` varchar(255) DEFAULT NULL,
  `uptime` int(11) DEFAULT NULL,
  `max_connections` varchar(255) DEFAULT NULL,
  `max_connect_errors` int(11) DEFAULT NULL,
  `threads_connected` int(11) DEFAULT NULL,
  `threads_running` int(11) DEFAULT NULL,
  `threads_created` int(11) DEFAULT NULL,
  `threads_cached` int(11) DEFAULT NULL,
  `threads_waited` int(11) DEFAULT NULL,
  `conn_rate` varchar(255) DEFAULT NULL,
  `conn_rate_level` varchar(255) DEFAULT NULL,
  `QPS` int(11) DEFAULT NULL,
  `TPS` int(11) DEFAULT NULL,
  `bytes_received` int(11) DEFAULT NULL,
  `bytes_send` int(11) DEFAULT NULL,
  `open_files_limit` int(11) DEFAULT NULL,
  `open_files` int(11) DEFAULT NULL,
  `table_open_cache` int(11) DEFAULT NULL,
  `open_tables` int(11) DEFAULT NULL,
  `key_buffer_size` float DEFAULT NULL,
  `sort_buffer_size` float DEFAULT NULL,
  `join_buffer_size` float DEFAULT NULL,
  `key_blocks_unused` int(11) DEFAULT NULL,
  `key_blocks_used` int(11) DEFAULT NULL,
  `key_blocks_not_flushed` int(11) DEFAULT NULL,
  `key_blocks_used_rate` float DEFAULT NULL,
  `key_buffer_read_rate` float DEFAULT NULL,
  `key_buffer_write_rate` float DEFAULT NULL,
  `innodb_buffer_pool_size` float DEFAULT NULL,
  `innodb_buffer_pool_pages_total` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_data` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_dirty` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_flushed` int(11) DEFAULT NULL,
  `innodb_buffer_pool_pages_free` int(11) DEFAULT NULL,
  `innodb_io_capacity` int(11) DEFAULT NULL,
  `innodb_read_io_threads` int(11) DEFAULT NULL,
  `innodb_write_io_threads` int(11) DEFAULT NULL,
  `innodb_rows_deleted_persecond` int(11) DEFAULT NULL,
  `innodb_rows_inserted_persecond` int(11) DEFAULT NULL,
  `innodb_rows_read_persecond` int(11) DEFAULT NULL,
  `innodb_rows_updated_persecond` int(11) DEFAULT NULL,
  `mon_status` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chk_time` (`chk_time`)
) ENGINE=InnoDB AUTO_INCREMENT=443919 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_db_rate
-- ----------------------------
DROP TABLE IF EXISTS `mysql_db_rate`;
CREATE TABLE `mysql_db_rate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `conn_decute` int(11) DEFAULT '0',
  `cpu_decute` int(11) DEFAULT '0',
  `mem_decute` int(11) DEFAULT '0',
  `disk_decute` int(11) DEFAULT '0',
  `db_rate` int(11) NOT NULL,
  `db_rate_level` varchar(255) NOT NULL,
  `db_rate_color` varchar(255) NOT NULL,
  `db_rate_reason` varchar(255) NOT NULL,
  `rate_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=443809 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_db_rate_his
-- ----------------------------
DROP TABLE IF EXISTS `mysql_db_rate_his`;
CREATE TABLE `mysql_db_rate_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `conn_decute` int(11) DEFAULT '0',
  `cpu_decute` int(11) DEFAULT '0',
  `mem_decute` int(11) DEFAULT '0',
  `disk_decute` int(11) DEFAULT '0',
  `db_rate` int(11) NOT NULL,
  `db_rate_level` varchar(255) NOT NULL,
  `db_rate_color` varchar(255) NOT NULL,
  `db_rate_reason` varchar(255) NOT NULL,
  `rate_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_repl
-- ----------------------------
DROP TABLE IF EXISTS `mysql_repl`;
CREATE TABLE `mysql_repl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `server_id` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `is_master` varchar(255) DEFAULT NULL,
  `is_slave` varchar(255) DEFAULT NULL,
  `mysql_role` varchar(255) DEFAULT NULL,
  `read_only` varchar(255) DEFAULT NULL,
  `master_server` varchar(255) DEFAULT NULL,
  `master_port` varchar(255) DEFAULT NULL,
  `slave_io_run` varchar(255) DEFAULT NULL,
  `slave_io_rate` varchar(255) DEFAULT NULL,
  `slave_sql_run` varchar(255) DEFAULT NULL,
  `slave_sql_rate` varchar(255) DEFAULT NULL,
  `delay` varchar(255) DEFAULT NULL,
  `delay_rate` varchar(255) DEFAULT NULL,
  `current_binlog_file` varchar(255) DEFAULT NULL,
  `current_binlog_pos` varchar(255) DEFAULT NULL,
  `master_binlog_file` varchar(255) DEFAULT NULL,
  `master_binlog_pos` varchar(255) DEFAULT NULL,
  `master_binlog_space` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=164004 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_repl_his
-- ----------------------------
DROP TABLE IF EXISTS `mysql_repl_his`;
CREATE TABLE `mysql_repl_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `server_id` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `is_master` varchar(255) DEFAULT NULL,
  `is_slave` varchar(255) DEFAULT NULL,
  `mysql_role` varchar(255) DEFAULT NULL,
  `read_only` varchar(255) DEFAULT NULL,
  `master_server` varchar(255) DEFAULT NULL,
  `master_port` varchar(255) DEFAULT NULL,
  `slave_io_run` varchar(255) DEFAULT NULL,
  `slave_io_rate` varchar(255) DEFAULT NULL,
  `slave_sql_run` varchar(255) DEFAULT NULL,
  `slave_sql_rate` varchar(255) DEFAULT NULL,
  `delay` varchar(255) DEFAULT NULL,
  `delay_rate` varchar(255) DEFAULT NULL,
  `current_binlog_file` varchar(255) DEFAULT NULL,
  `current_binlog_pos` varchar(255) DEFAULT NULL,
  `master_binlog_file` varchar(255) DEFAULT NULL,
  `master_binlog_pos` varchar(255) DEFAULT NULL,
  `master_binlog_space` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=164003 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for mysql_slowquery
-- ----------------------------
DROP TABLE IF EXISTS `mysql_slowquery`;
CREATE TABLE `mysql_slowquery` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL,
  `port` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `slow_log_file` varchar(255) DEFAULT NULL,
  `start_time` varchar(255) DEFAULT NULL,
  `client_host` varchar(255) DEFAULT NULL,
  `db_name` varchar(255) DEFAULT NULL,
  `sql_text` text,
  `query_time` float DEFAULT NULL,
  `lock_time` float DEFAULT NULL,
  `rows_examined` int(11) DEFAULT NULL,
  `rows_sent` int(11) DEFAULT NULL,
  `thread_id` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=66401 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_alert_log
-- ----------------------------
DROP TABLE IF EXISTS `oracle_alert_log`;
CREATE TABLE `oracle_alert_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `log_time` varchar(255) DEFAULT NULL,
  `log_level` varchar(255) DEFAULT NULL,
  `log_content` text,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_backup_info
-- ----------------------------
DROP TABLE IF EXISTS `oracle_backup_info`;
CREATE TABLE `oracle_backup_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `BS_KEY` int(11) DEFAULT NULL,
  `RECID` int(11) DEFAULT NULL,
  `STAMP` int(11) DEFAULT NULL,
  `START_TIME` varchar(255) DEFAULT NULL,
  `COMPLETE_TIME` varchar(255) DEFAULT NULL,
  `ESPLASED_SECONDS` int(11) DEFAULT NULL,
  `OUTPUT_BYTES` int(11) DEFAULT NULL,
  `BACKUP_TYPE` varchar(255) DEFAULT NULL,
  `STATUS` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3600 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_backup_piece
-- ----------------------------
DROP TABLE IF EXISTS `oracle_backup_piece`;
CREATE TABLE `oracle_backup_piece` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `BACKUP_SET` int(11) DEFAULT NULL,
  `SET_STAMP` int(11) DEFAULT NULL,
  `BACKUP_TYPE` varchar(255) DEFAULT NULL,
  `HAS_CTL` varchar(255) DEFAULT NULL,
  `STATUS` varchar(255) DEFAULT NULL,
  `DEVICE_TYPE` varchar(255) DEFAULT NULL,
  `START_TIME` varchar(255) DEFAULT NULL,
  `COMPLETION_TIME` varchar(255) DEFAULT NULL,
  `ELAPSED_TIME` int(11) DEFAULT NULL,
  `SIZE` float DEFAULT NULL,
  `COMPRESSED` varchar(255) DEFAULT NULL,
  `TAG` varchar(255) DEFAULT NULL,
  `PATH` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4205 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_bak_job
-- ----------------------------
DROP TABLE IF EXISTS `oracle_bak_job`;
CREATE TABLE `oracle_bak_job` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_no` varchar(255) DEFAULT NULL,
  `job_name` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `bak_conf_no` varchar(255) DEFAULT NULL,
  `bak_conf_name` varchar(255) DEFAULT NULL,
  `is_on` int(11) DEFAULT NULL,
  `next_bak_time` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_db
-- ----------------------------
DROP TABLE IF EXISTS `oracle_db`;
CREATE TABLE `oracle_db` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `dbid` int(11) DEFAULT NULL,
  `dbname` varchar(255) DEFAULT NULL,
  `version` varchar(255) DEFAULT NULL,
  `db_unique_name` varchar(255) DEFAULT NULL,
  `database_role` varchar(255) DEFAULT NULL,
  `uptime` int(11) DEFAULT NULL,
  `audit_trail` varchar(255) DEFAULT NULL,
  `open_mode` varchar(255) DEFAULT NULL,
  `log_mode` varchar(255) DEFAULT NULL,
  `archive_used` varchar(255) DEFAULT NULL,
  `archive_rate_level` varchar(255) DEFAULT NULL,
  `inst_id` int(11) DEFAULT NULL,
  `instance_name` varchar(255) DEFAULT NULL,
  `host_name` varchar(255) DEFAULT NULL,
  `max_process` int(11) DEFAULT NULL,
  `current_process` int(11) DEFAULT NULL,
  `percent_process` varchar(255) DEFAULT NULL,
  `conn_rate_level` varchar(255) DEFAULT NULL,
  `adg_transport_lag` varchar(255) DEFAULT NULL,
  `adg_apply_lag` varchar(255) DEFAULT NULL,
  `adg_transport_value` int(11) DEFAULT NULL,
  `adg_transport_rate_level` varchar(255) DEFAULT NULL,
  `adg_apply_value` int(11) DEFAULT NULL,
  `adg_apply_rate_level` varchar(255) DEFAULT NULL,
  `mon_status` varchar(255) NOT NULL DEFAULT '',
  `err_info` text CHARACTER SET utf8mb4,
  `sga_size` int(11) DEFAULT NULL,
  `pga_size` int(11) DEFAULT NULL,
  `mem_pct` float DEFAULT NULL,
  `qps` int(11) DEFAULT NULL,
  `tps` int(11) DEFAULT NULL,
  `exec_count` int(11) DEFAULT NULL,
  `user_commits` int(11) DEFAULT NULL,
  `gets` int(11) DEFAULT NULL,
  `logr` int(11) DEFAULT NULL,
  `phyr` int(11) DEFAULT NULL,
  `phyw` int(11) DEFAULT NULL,
  `blockchange` int(11) DEFAULT NULL,
  `redo` int(11) DEFAULT NULL,
  `parse` int(11) DEFAULT NULL,
  `hardparse` int(11) DEFAULT NULL,
  `netin` int(11) DEFAULT NULL,
  `netout` int(11) DEFAULT NULL,
  `io` float DEFAULT NULL,
  `total_sess` int(11) DEFAULT NULL,
  `act_sess` int(11) DEFAULT NULL,
  `act_trans` int(11) DEFAULT NULL,
  `blocked_sess` int(11) DEFAULT NULL,
  `dbtime` float DEFAULT NULL,
  `dbcpu` float DEFAULT NULL,
  `log_para_wait` float DEFAULT NULL,
  `log_sync_wait` float DEFAULT NULL,
  `log_sync_cnt` float DEFAULT NULL,
  `scat_wait` float DEFAULT NULL,
  `scat_read_cnt` float DEFAULT NULL,
  `seq_wait` float DEFAULT NULL,
  `seq_read_cnt` float DEFAULT NULL,
  `row_lock_cnt` float DEFAULT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=528457 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_db_event
-- ----------------------------
DROP TABLE IF EXISTS `oracle_db_event`;
CREATE TABLE `oracle_db_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `event_no` varchar(255) NOT NULL,
  `event_name` varchar(255) NOT NULL,
  `event_cnt` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2473887 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_db_event_his
-- ----------------------------
DROP TABLE IF EXISTS `oracle_db_event_his`;
CREATE TABLE `oracle_db_event_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `event_no` varchar(255) NOT NULL,
  `event_name` varchar(255) NOT NULL,
  `event_cnt` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2473876 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_db_his
-- ----------------------------
DROP TABLE IF EXISTS `oracle_db_his`;
CREATE TABLE `oracle_db_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `dbid` int(11) DEFAULT NULL,
  `dbname` varchar(255) DEFAULT NULL,
  `version` varchar(255) DEFAULT NULL,
  `db_unique_name` varchar(255) DEFAULT NULL,
  `database_role` varchar(255) DEFAULT NULL,
  `uptime` int(11) DEFAULT NULL,
  `audit_trail` varchar(255) DEFAULT NULL,
  `open_mode` varchar(255) DEFAULT NULL,
  `log_mode` varchar(255) DEFAULT NULL,
  `archive_used` varchar(255) DEFAULT NULL,
  `archive_rate_level` varchar(255) DEFAULT NULL,
  `inst_id` int(11) DEFAULT NULL,
  `instance_name` varchar(255) DEFAULT NULL,
  `host_name` varchar(255) DEFAULT NULL,
  `max_process` int(11) DEFAULT NULL,
  `current_process` int(11) DEFAULT NULL,
  `percent_process` varchar(255) DEFAULT NULL,
  `conn_rate_level` varchar(255) DEFAULT NULL,
  `adg_transport_lag` varchar(255) DEFAULT NULL,
  `adg_apply_lag` varchar(255) DEFAULT NULL,
  `adg_transport_value` int(11) DEFAULT NULL,
  `adg_transport_rate_level` varchar(255) DEFAULT NULL,
  `adg_apply_value` int(11) DEFAULT NULL,
  `adg_apply_rate_level` varchar(255) DEFAULT NULL,
  `mon_status` varchar(255) NOT NULL DEFAULT '',
  `err_info` text CHARACTER SET utf8mb4,
  `sga_size` int(11) DEFAULT NULL,
  `pga_size` int(11) DEFAULT NULL,
  `mem_pct` float DEFAULT NULL,
  `qps` int(11) DEFAULT NULL,
  `tps` int(11) DEFAULT NULL,
  `exec_count` int(11) DEFAULT NULL,
  `user_commits` int(11) DEFAULT NULL,
  `gets` int(11) DEFAULT NULL,
  `logr` int(11) DEFAULT NULL,
  `phyr` int(11) DEFAULT NULL,
  `phyw` int(11) DEFAULT NULL,
  `blockchange` int(11) DEFAULT NULL,
  `redo` int(11) DEFAULT NULL,
  `parse` int(11) DEFAULT NULL,
  `hardparse` int(11) DEFAULT NULL,
  `netin` int(11) DEFAULT NULL,
  `netout` int(11) DEFAULT NULL,
  `io` float DEFAULT NULL,
  `total_sess` int(11) DEFAULT NULL,
  `act_sess` int(11) DEFAULT NULL,
  `act_trans` int(11) DEFAULT NULL,
  `blocked_sess` int(11) DEFAULT NULL,
  `dbtime` float DEFAULT NULL,
  `dbcpu` float DEFAULT NULL,
  `log_para_wait` float DEFAULT NULL,
  `log_sync_wait` float DEFAULT NULL,
  `log_sync_cnt` float DEFAULT NULL,
  `scat_wait` float DEFAULT NULL,
  `scat_read_cnt` float DEFAULT NULL,
  `seq_wait` float DEFAULT NULL,
  `seq_read_cnt` float DEFAULT NULL,
  `row_lock_cnt` float DEFAULT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chk_time` (`chk_time`)
) ENGINE=InnoDB AUTO_INCREMENT=528455 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_db_rate
-- ----------------------------
DROP TABLE IF EXISTS `oracle_db_rate`;
CREATE TABLE `oracle_db_rate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `conn_decute` int(11) DEFAULT '0',
  `archive_decute` int(11) DEFAULT NULL,
  `event_decute` int(11) DEFAULT NULL,
  `tbs_decute` int(11) DEFAULT '0',
  `undo_decute` int(11) DEFAULT '0',
  `tmp_decute` int(11) DEFAULT '0',
  `cpu_decute` int(11) DEFAULT '0',
  `mem_decute` int(11) DEFAULT '0',
  `disk_decute` int(11) DEFAULT '0',
  `adg_decute` int(11) DEFAULT '0',
  `db_rate` int(11) NOT NULL DEFAULT '100',
  `db_rate_level` varchar(255) DEFAULT '',
  `db_rate_color` varchar(255) DEFAULT NULL,
  `db_rate_reason` varchar(255) DEFAULT NULL,
  `rate_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=529312 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_db_rate_his
-- ----------------------------
DROP TABLE IF EXISTS `oracle_db_rate_his`;
CREATE TABLE `oracle_db_rate_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `dbname_cn` varchar(255) NOT NULL,
  `conn_decute` int(11) DEFAULT '0',
  `tbs_decute` int(11) DEFAULT '0',
  `undo_decute` int(11) DEFAULT '0',
  `tmp_decute` int(11) DEFAULT '0',
  `cpu_decute` int(11) DEFAULT '0',
  `mem_decute` int(11) DEFAULT '0',
  `disk_decute` int(11) DEFAULT '0',
  `adg_decute` int(11) DEFAULT '0',
  `db_rate` int(11) NOT NULL DEFAULT '100',
  `db_rate_level` varchar(255) DEFAULT '',
  `db_rate_color` varchar(255) DEFAULT NULL,
  `db_rate_reason` varchar(255) DEFAULT NULL,
  `rate_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_expired_pwd
-- ----------------------------
DROP TABLE IF EXISTS `oracle_expired_pwd`;
CREATE TABLE `oracle_expired_pwd` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `port` varchar(255) DEFAULT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `result_number` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_invalid_index
-- ----------------------------
DROP TABLE IF EXISTS `oracle_invalid_index`;
CREATE TABLE `oracle_invalid_index` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `port` varchar(255) DEFAULT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `owner` varchar(255) DEFAULT NULL,
  `index_name` varchar(255) DEFAULT NULL,
  `partition_name` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=164981 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_lock
-- ----------------------------
DROP TABLE IF EXISTS `oracle_lock`;
CREATE TABLE `oracle_lock` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `session` varchar(255) NOT NULL,
  `session_id` varchar(255) DEFAULT NULL,
  `lmode` varchar(255) NOT NULL,
  `ctime` int(11) NOT NULL,
  `inst_id` varchar(255) NOT NULL,
  `lmode1` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_logmnr
-- ----------------------------
DROP TABLE IF EXISTS `oracle_logmnr`;
CREATE TABLE `oracle_logmnr` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_time` varchar(255) DEFAULT NULL,
  `next_time` varchar(255) DEFAULT NULL,
  `mb` float DEFAULT NULL,
  `logfile` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_report
-- ----------------------------
DROP TABLE IF EXISTS `oracle_report`;
CREATE TABLE `oracle_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) DEFAULT NULL,
  `report_begin_time` varchar(255) DEFAULT NULL,
  `report_end_time` varchar(255) DEFAULT NULL,
  `report_type` varchar(255) DEFAULT NULL,
  `report_path` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `generate_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_switchover
-- ----------------------------
DROP TABLE IF EXISTS `oracle_switchover`;
CREATE TABLE `oracle_switchover` (
  `id` int(11) NOT NULL,
  `switch_name` varchar(255) DEFAULT NULL,
  `switch_mode` varchar(255) DEFAULT NULL,
  `primary_tags` varchar(255) DEFAULT NULL,
  `primary_host` varchar(255) DEFAULT NULL,
  `primary_host_name` varchar(255) DEFAULT NULL,
  `primary_curr_role` varchar(255) DEFAULT NULL,
  `standby_tags` varchar(255) DEFAULT NULL,
  `standby_host` varchar(255) DEFAULT NULL,
  `standby_host_name` varchar(255) DEFAULT NULL,
  `standby_curr_role` varchar(255) DEFAULT NULL,
  `adg_trans_lag` varchar(255) DEFAULT NULL,
  `adg_apply_lag` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_tbs
-- ----------------------------
DROP TABLE IF EXISTS `oracle_tbs`;
CREATE TABLE `oracle_tbs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` int(11) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `tbs_name` varchar(255) NOT NULL,
  `datafile_count` int(11) NOT NULL,
  `size_gb` varchar(32) NOT NULL,
  `free_gb` varchar(32) NOT NULL,
  `used_gb` varchar(32) NOT NULL,
  `max_free` varchar(32) NOT NULL,
  `pct_used` float NOT NULL,
  `pct_free` varchar(32) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1177734 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_tbs_his
-- ----------------------------
DROP TABLE IF EXISTS `oracle_tbs_his`;
CREATE TABLE `oracle_tbs_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` int(11) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `tbs_name` varchar(255) NOT NULL,
  `datafile_count` int(11) NOT NULL,
  `size_gb` varchar(32) NOT NULL,
  `free_gb` varchar(32) NOT NULL,
  `used_gb` varchar(32) NOT NULL,
  `max_free` varchar(32) NOT NULL,
  `pct_used` float NOT NULL,
  `pct_free` varchar(32) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1177729 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_tmp_tbs
-- ----------------------------
DROP TABLE IF EXISTS `oracle_tmp_tbs`;
CREATE TABLE `oracle_tmp_tbs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `tmp_tbs_name` varchar(255) NOT NULL,
  `total_mb` varchar(255) NOT NULL,
  `used_mb` varchar(255) NOT NULL,
  `pct_used` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=167136 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_tmp_tbs_his
-- ----------------------------
DROP TABLE IF EXISTS `oracle_tmp_tbs_his`;
CREATE TABLE `oracle_tmp_tbs_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `tmp_tbs_name` varchar(255) NOT NULL,
  `total_mb` varchar(255) NOT NULL,
  `used_mb` varchar(255) NOT NULL,
  `pct_used` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=167135 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_undo_tbs
-- ----------------------------
DROP TABLE IF EXISTS `oracle_undo_tbs`;
CREATE TABLE `oracle_undo_tbs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `undo_tbs_name` varchar(255) NOT NULL,
  `total_mb` varchar(255) NOT NULL,
  `used_mb` varchar(255) NOT NULL,
  `pct_used` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=209552 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for oracle_undo_tbs_his
-- ----------------------------
DROP TABLE IF EXISTS `oracle_undo_tbs_his`;
CREATE TABLE `oracle_undo_tbs_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `undo_tbs_name` varchar(255) NOT NULL,
  `total_mb` varchar(255) NOT NULL,
  `used_mb` varchar(255) NOT NULL,
  `pct_used` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=209551 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for os_filesystem
-- ----------------------------
DROP TABLE IF EXISTS `os_filesystem`;
CREATE TABLE `os_filesystem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `host_name` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `size` varchar(255) NOT NULL,
  `avail` varchar(255) NOT NULL,
  `pct_used` float NOT NULL,
  `filesystem` varchar(255) DEFAULT NULL,
  `disk_rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=459662 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for os_filesystem_his
-- ----------------------------
DROP TABLE IF EXISTS `os_filesystem_his`;
CREATE TABLE `os_filesystem_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `host_name` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `size` varchar(255) NOT NULL,
  `avail` varchar(255) NOT NULL,
  `pct_used` float(11,0) NOT NULL,
  `filesystem` varchar(255) DEFAULT NULL,
  `disk_rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=459657 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for os_info
-- ----------------------------
DROP TABLE IF EXISTS `os_info`;
CREATE TABLE `os_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `host_name` varchar(255) NOT NULL,
  `updays` float DEFAULT NULL,
  `recv_kbps` float DEFAULT NULL,
  `send_kbps` float DEFAULT NULL,
  `load1` float DEFAULT NULL,
  `load5` float DEFAULT NULL,
  `load15` float DEFAULT NULL,
  `cpu_sys` float DEFAULT NULL,
  `cpu_iowait` float DEFAULT NULL,
  `cpu_user` float DEFAULT NULL,
  `cpu_used` float DEFAULT NULL,
  `cpu_rate_level` varchar(255) DEFAULT NULL,
  `mem_used` float DEFAULT NULL,
  `mem_cache` float DEFAULT NULL,
  `mem_buffer` float DEFAULT NULL,
  `mem_free` float DEFAULT NULL,
  `mem_used_mb` float DEFAULT NULL,
  `swap_used` float DEFAULT NULL,
  `swap_free` float DEFAULT NULL,
  `pgin` float DEFAULT NULL,
  `pgout` float DEFAULT NULL,
  `swapin` float DEFAULT NULL,
  `swapout` float DEFAULT NULL,
  `pgfault` float DEFAULT NULL,
  `pgmajfault` float DEFAULT NULL,
  `mem_rate_level` varchar(255) DEFAULT NULL,
  `tcp_close` float DEFAULT NULL,
  `tcp_timewait` float DEFAULT NULL,
  `tcp_connected` float DEFAULT NULL,
  `tcp_syn` float DEFAULT NULL,
  `tcp_listen` float DEFAULT NULL,
  `iops` float DEFAULT NULL,
  `read_mb` float DEFAULT NULL,
  `write_mb` float DEFAULT NULL,
  `proc_new` float DEFAULT NULL,
  `proc_running` float DEFAULT NULL,
  `proc_block` float DEFAULT NULL,
  `intr` float DEFAULT NULL,
  `ctx` float DEFAULT NULL,
  `softirq` float DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `ostype` varchar(255) DEFAULT NULL,
  `kernel` varchar(255) DEFAULT NULL,
  `frame` varchar(255) DEFAULT NULL,
  `linux_version` varchar(255) DEFAULT NULL,
  `cpu_mode` varchar(255) DEFAULT NULL,
  `cpu_cache` varchar(255) DEFAULT NULL,
  `processor` varchar(255) DEFAULT NULL,
  `virtual_cnt` int(255) DEFAULT NULL,
  `cpu_speed` varchar(255) DEFAULT NULL,
  `Memtotal` float(255,0) DEFAULT NULL,
  `ipinfo` varchar(255) DEFAULT NULL,
  `mon_status` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=697328 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for os_info_his
-- ----------------------------
DROP TABLE IF EXISTS `os_info_his`;
CREATE TABLE `os_info_his` (
  `id` int(11) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `host_name` varchar(255) NOT NULL,
  `updays` float DEFAULT NULL,
  `recv_kbps` float DEFAULT NULL,
  `send_kbps` float DEFAULT NULL,
  `load1` float DEFAULT NULL,
  `load5` float DEFAULT NULL,
  `load15` float DEFAULT NULL,
  `cpu_sys` float DEFAULT NULL,
  `cpu_iowait` float DEFAULT NULL,
  `cpu_user` float DEFAULT NULL,
  `cpu_used` float DEFAULT NULL,
  `cpu_rate_level` varchar(255) DEFAULT NULL,
  `mem_used` float DEFAULT NULL,
  `mem_cache` float DEFAULT NULL,
  `mem_buffer` float DEFAULT NULL,
  `mem_free` float DEFAULT NULL,
  `mem_used_mb` float DEFAULT NULL,
  `swap_used` float DEFAULT NULL,
  `swap_free` float DEFAULT NULL,
  `pgin` float DEFAULT NULL,
  `pgout` float DEFAULT NULL,
  `swapin` float DEFAULT NULL,
  `swapout` float DEFAULT NULL,
  `pgfault` float DEFAULT NULL,
  `pgmajfault` float DEFAULT NULL,
  `mem_rate_level` varchar(255) DEFAULT NULL,
  `tcp_close` float DEFAULT NULL,
  `tcp_timewait` float DEFAULT NULL,
  `tcp_connected` float DEFAULT NULL,
  `tcp_syn` float DEFAULT NULL,
  `tcp_listen` float DEFAULT NULL,
  `iops` float DEFAULT NULL,
  `read_mb` float DEFAULT NULL,
  `write_mb` float DEFAULT NULL,
  `proc_new` float DEFAULT NULL,
  `proc_running` float DEFAULT NULL,
  `proc_block` float DEFAULT NULL,
  `intr` float DEFAULT NULL,
  `ctx` float DEFAULT NULL,
  `softirq` float DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `ostype` varchar(255) DEFAULT NULL,
  `kernel` varchar(255) DEFAULT NULL,
  `frame` varchar(255) DEFAULT NULL,
  `linux_version` varchar(255) DEFAULT NULL,
  `cpu_mode` varchar(255) DEFAULT NULL,
  `cpu_cache` varchar(255) DEFAULT NULL,
  `processor` varchar(255) DEFAULT NULL,
  `virtual_cnt` int(255) DEFAULT NULL,
  `cpu_speed` varchar(255) DEFAULT NULL,
  `Memtotal` float(255,0) DEFAULT NULL,
  `ipinfo` varchar(255) DEFAULT NULL,
  `mon_status` varchar(255) NOT NULL,
  `rate_level` varchar(255) NOT NULL,
  `chk_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_osinfo_his_chktime` (`chk_time`),
  KEY `chk_time` (`chk_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for sql_list
-- ----------------------------
DROP TABLE IF EXISTS `sql_list`;
CREATE TABLE `sql_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sql_no` varchar(255) DEFAULT NULL,
  `sql_info` text,
  `sql_name` varchar(255) DEFAULT NULL,
  `db_name` varchar(255) DEFAULT NULL,
  `result` varchar(255) DEFAULT NULL,
  `result_color` varchar(255) DEFAULT NULL,
  `exec_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tab_alarm_conf
-- ----------------------------
DROP TABLE IF EXISTS `tab_alarm_conf`;
CREATE TABLE `tab_alarm_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_type` varchar(255) DEFAULT NULL,
  `alarm_name` varchar(255) DEFAULT NULL,
  `judge` varchar(255) DEFAULT NULL,
  `jdg_value` float DEFAULT NULL,
  `jdg_des` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tab_alarm_email_info
-- ----------------------------
DROP TABLE IF EXISTS `tab_alarm_email_info`;
CREATE TABLE `tab_alarm_email_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `alarm_type` varchar(255) NOT NULL,
  `email_header` varchar(255) NOT NULL,
  `email_content` text NOT NULL,
  `alarm_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tab_alarm_info
-- ----------------------------
DROP TABLE IF EXISTS `tab_alarm_info`;
CREATE TABLE `tab_alarm_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `alarm_type` varchar(255) NOT NULL,
  `alarm_header` varchar(255) NOT NULL,
  `alarm_content` text NOT NULL,
  `alarm_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1856867 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tab_linux_servers
-- ----------------------------
DROP TABLE IF EXISTS `tab_linux_servers`;
CREATE TABLE `tab_linux_servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `host_name` varchar(255) NOT NULL,
  `user` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `connect` varchar(255) NOT NULL DEFAULT '1',
  `cpu` varchar(255) NOT NULL DEFAULT '1',
  `mem` varchar(255) NOT NULL DEFAULT '1',
  `swap` varchar(255) DEFAULT NULL,
  `disk` varchar(255) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tab_mysql_servers
-- ----------------------------
DROP TABLE IF EXISTS `tab_mysql_servers`;
CREATE TABLE `tab_mysql_servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `user` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_os` varchar(255) NOT NULL,
  `password_os` varchar(255) NOT NULL,
  `connect` varchar(255) DEFAULT NULL,
  `repl` varchar(255) DEFAULT NULL,
  `conn` varchar(255) DEFAULT NULL,
  `err_info` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for tab_oracle_servers
-- ----------------------------
DROP TABLE IF EXISTS `tab_oracle_servers`;
CREATE TABLE `tab_oracle_servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tags` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `user` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_os` varchar(255) NOT NULL,
  `password_os` varchar(255) NOT NULL,
  `connect` varchar(255) NOT NULL DEFAULT '1',
  `tbs` varchar(255) NOT NULL DEFAULT '1',
  `adg` varchar(255) NOT NULL DEFAULT '1',
  `temp_tbs` varchar(255) NOT NULL DEFAULT '1',
  `undo_tbs` varchar(255) NOT NULL DEFAULT '1',
  `conn` varchar(255) NOT NULL DEFAULT '1',
  `err_info` varchar(255) NOT NULL,
  `invalid_index` varchar(255) DEFAULT NULL,
  `oracle_lock` varchar(255) DEFAULT NULL,
  `oracle_pwd` varchar(255) DEFAULT NULL,
  `oracle_event` varchar(255) DEFAULT NULL,
  `pga` varchar(255) DEFAULT NULL,
  `archive` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
