/*
Navicat MySQL Data Transfer

Source Server         : dbmon
Source Server Version : 50717
Source Host           : 192.168.48.50:3306
Source Database       : db_monitor

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2019-01-17 17:23:38
*/
-- ----------------------------
-- Records of tab_alarm_conf
-- ----------------------------
INSERT INTO `tab_alarm_conf` VALUES ('1', 'Oracle', 'Oracle数据库通断告警', '>=', '1', '连续中断次数');
INSERT INTO `tab_alarm_conf` VALUES ('2', 'Oracle', 'Oracle数据库表空间使用率告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('3', 'Oracle', 'Oracle数据库表空间使用率告警', '<=', '0.5', '单位：GB');
INSERT INTO `tab_alarm_conf` VALUES ('4', 'Oracle', 'Oracle数据库临时表空间告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('5', 'Oracle', 'Oracle数据库临时表空间告警', '<=', '0.5', '单位：GB');
INSERT INTO `tab_alarm_conf` VALUES ('6', 'Oracle', 'Oracle数据库Undo表空间告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('7', 'Oracle', 'Oracle数据库Undo表空间告警', '<=', '0.5', '单位：GB');
INSERT INTO `tab_alarm_conf` VALUES ('8', 'Oracle', 'Oracle数据库连接数告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('9', 'Oracle', 'Oracle数据库adg延迟告警', '>=', '300', '单位：秒');
INSERT INTO `tab_alarm_conf` VALUES ('10', 'Oracle', 'Oracle数据库后台日志告警', '', null, '检测后台日志异常');
INSERT INTO `tab_alarm_conf` VALUES ('11', 'Oracle', 'Oracle数据库综合性能告警', '>=', '200', '');
INSERT INTO `tab_alarm_conf` VALUES ('12', 'Oracle', 'Oracle数据库pga使用率告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('13', 'Oracle', 'Oracle数据库归档使用率告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('14', 'Oracle', 'Oracle数据库锁异常告警', '>=', '100', '锁定时间，单位：秒');
INSERT INTO `tab_alarm_conf` VALUES ('15', 'Oracle', 'Oracle数据库密码过期告警', '<=', '7', '密码过期剩余时间，单位：天');
INSERT INTO `tab_alarm_conf` VALUES ('16', 'Oracle', 'Oracle失效索引告警', null, null, '检测失效索引');
INSERT INTO `tab_alarm_conf` VALUES ('17', 'Linux', 'Linux主机通断告警', '>=', '1', '连续中断次数');
INSERT INTO `tab_alarm_conf` VALUES ('18', 'Linux', 'Linux主机CPU使用率告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('19', 'Linux', 'Linux主机内存使用率告警', '>=', '90', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('20', 'Linux', 'Linux主机文件系统使用率告警', '>=', '95', '使用百分比');
INSERT INTO `tab_alarm_conf` VALUES ('21', 'MySQL', 'MySQL数据库通断告警', '>=', '1', '连续中断次数');
INSERT INTO `tab_alarm_conf` VALUES ('22', 'Linux', 'Linux主机文件系统使用率告警', '<=', '1', '单位：GB');
INSERT INTO `tab_alarm_conf` VALUES ('23', 'Linux', 'Linux主机swap使用率告警', '>=', '10', '使用百分比');
