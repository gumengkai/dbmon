/*
Navicat MySQL Data Transfer

Source Server         : dbmon
Source Server Version : 50717
Source Host           : 192.168.48.50:3306
Source Database       : db_monitor

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2018-12-22 14:37:38
*/

SET FOREIGN_KEY_CHECKS=0;

-- ---------------------------

-- ----------------------------
-- Records of tab_alarm_conf
-- ----------------------------
INSERT INTO `tab_alarm_conf` VALUES ('1', 'oracle', 'Oracle数据库通断告警', '0', '0', '1', '0');
INSERT INTO `tab_alarm_conf` VALUES ('2', 'oracle', 'Oracle数据库表空间使用率告警', '80', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('3', 'oracle', 'Oracle数据库adg延迟告警', '0', '0', '300', '0');
INSERT INTO `tab_alarm_conf` VALUES ('4', 'oracle', 'Oracle数据库临时表空间告警', '90', '0.1', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('5', 'oracle', 'Oracle数据库undo表空间告警', '90', '0.1', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('6', 'oracle', 'Oracle数据库连接数告警', '90', '20', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('7', 'os', 'Linux主机通断告警', '0', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('8', 'os', 'Linux主机CPU使用率告警', '90', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('9', 'os', 'Linux主机内存使用率告警', '90', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('10', 'os', 'Linux主机文件系统使用率告警', '90', '0.1', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('11', 'oracle', 'Oracle数据库后台日志告警', '0', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('12', 'oracle', 'Oracle数据库综合性能告警', '0', '0', '0', '100');
INSERT INTO `tab_alarm_conf` VALUES ('13', 'oracle', 'Oracle数据库pga使用率告警', '90', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('14', 'oracle', 'Oracle数据库归档使用率告警', '90', '0', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('15', 'oracle', 'Oracle数据库锁异常告警', '0', '0', '100', '0');
INSERT INTO `tab_alarm_conf` VALUES ('16', 'oracle', 'Oracle数据库密码过期告警', '0', '10', '0', '0');
INSERT INTO `tab_alarm_conf` VALUES ('17', 'oracle', 'Oracle失效索引告警', '0', '0', '0', '0');
