/*
Navicat MySQL Data Transfer

Source Server         : 锐捷-周口
Source Server Version : 50728
Source Host           : 36.99.42.60:3306
Source Database       : epidemic_situation_information

Target Server Type    : MYSQL
Target Server Version : 50728
File Encoding         : 65001

Date: 2020-02-13 12:08:48
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for s_area_code
-- ----------------------------
DROP TABLE IF EXISTS `s_area_code`;
CREATE TABLE `s_area_code` (
  `ID` int(11) NOT NULL,
  `areaCode` int(11) NOT NULL,
  `province` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `district` varchar(50) NOT NULL,
  `detail` varchar(100) NOT NULL,
  PRIMARY KEY (`ID`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for userInfo_yh_rj
-- ----------------------------
DROP TABLE IF EXISTS `userInfo_yh_rj`;
CREATE TABLE `userInfo_yh_rj` (
  `id` varchar(50) NOT NULL,
  `xm` varchar(255) DEFAULT NULL,
  `sflbdm` varchar(255) DEFAULT NULL,
  `zzmc` varchar(255) DEFAULT NULL,
  `dqmc` varchar(255) DEFAULT NULL,
  `bjmc` varchar(255) DEFAULT NULL,
  `sfzjh` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for zhoukou
-- ----------------------------
DROP TABLE IF EXISTS `zhoukou`;
CREATE TABLE `zhoukou` (
  `ID` int(10) unsigned NOT NULL,
  `学生姓名` varchar(45) NOT NULL,
  `学号` varchar(45) NOT NULL,
  `学校` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for 假期人员去向统计
-- ----------------------------
DROP TABLE IF EXISTS `假期人员去向统计`;
CREATE TABLE `假期人员去向统计` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `是否武汉及周边` varchar(255) DEFAULT NULL,
  `是否途径中转武汉` varchar(255) DEFAULT NULL,
  `是否去过医院` varchar(255) DEFAULT NULL,
  `咳嗽` varchar(255) DEFAULT NULL,
  `发热` varchar(255) DEFAULT NULL,
  `乏力` varchar(255) DEFAULT NULL,
  `呼吸困难` varchar(255) DEFAULT NULL,
  `假期去向` varchar(255) DEFAULT NULL,
  `其他情况说明` varchar(255) DEFAULT NULL,
  `姓名` varchar(255) DEFAULT NULL,
  `联系方式` varchar(255) DEFAULT NULL,
  `所在地信息` varchar(255) DEFAULT NULL,
  `经度` double(255,0) DEFAULT NULL,
  `维度` double(255,0) DEFAULT NULL,
  `紧急联系人姓名` varchar(255) DEFAULT NULL,
  `紧急联系人手机号码` varchar(255) DEFAULT NULL,
  `学籍号` varchar(255) DEFAULT NULL,
  `备用字段2` varchar(255) DEFAULT NULL,
  `备用字段3` varchar(255) DEFAULT NULL,
  `备用字段4` double(255,0) DEFAULT NULL,
  `备用字段5` double(255,0) DEFAULT NULL,
  `是否乘坐飞机火车` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for 节后返回学校所在地统计表
-- ----------------------------
DROP TABLE IF EXISTS `节后返回学校所在地统计表`;
CREATE TABLE `节后返回学校所在地统计表` (
  `姓名` varchar(255) DEFAULT NULL,
  `学籍号` varchar(255) DEFAULT NULL,
  `联系电话` varchar(255) DEFAULT NULL,
  `学校校区` varchar(255) DEFAULT NULL,
  `学院` varchar(255) DEFAULT NULL,
  `专业班级` varchar(255) DEFAULT NULL,
  `学校统一返校日期` varchar(255) DEFAULT NULL,
  `个人预计返校日期` date DEFAULT NULL,
  `请假天数` int(255) DEFAULT NULL,
  `省份` varchar(255) DEFAULT NULL,
  `城市` varchar(255) DEFAULT NULL,
  `区县` varchar(255) DEFAULT NULL,
  `返校行程` varchar(255) DEFAULT NULL,
  `ID` int(255) NOT NULL AUTO_INCREMENT,
  `是否离开本市` varchar(255) DEFAULT NULL,
  `备用字段3` varchar(255) DEFAULT NULL,
  `备用字段4` double(255,0) DEFAULT NULL,
  `备用字段5` double(255,0) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
-- Table structure for 每日健康上报表
-- ----------------------------
DROP TABLE IF EXISTS `每日健康上报表`;
CREATE TABLE `每日健康上报表` (
  `姓名` varchar(255) DEFAULT NULL,
  `学籍号` varchar(255) DEFAULT NULL,
  `联系电话` varchar(255) DEFAULT NULL,
  `班级` varchar(255) DEFAULT NULL,
  `当前位置` varchar(255) DEFAULT NULL,
  `经度` double(255,0) DEFAULT NULL,
  `维度` double(255,0) DEFAULT NULL,
  `是否接触武汉及周边` varchar(255) DEFAULT NULL,
  `是否途径中转武汉` varchar(255) DEFAULT NULL,
  `是否乘坐飞机、火车` varchar(255) DEFAULT NULL,
  `咳嗽` varchar(255) DEFAULT NULL,
  `发热` varchar(255) DEFAULT NULL,
  `乏力` varchar(255) DEFAULT NULL,
  `呼吸困难` varchar(255) DEFAULT NULL,
  `其他健康状况` varchar(255) DEFAULT NULL,
  `体温` double(255,0) DEFAULT NULL,
  `填写日期` date DEFAULT NULL,
  `其他情况说明` varchar(255) DEFAULT NULL,
  `ID` int(255) NOT NULL AUTO_INCREMENT,
  `备用字段2` varchar(255) DEFAULT NULL,
  `备用字段3` varchar(255) DEFAULT NULL,
  `备用字段4` double(255,0) DEFAULT NULL,
  `备用字段5` double(255,0) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

DROP TABLE IF EXISTS `sid_user_info`;
CREATE TABLE `sid_user_info` (
  `id` VARCHAR(32) NOT NULL,
  `xm` VARCHAR(32) NOT NULL,
  `sflbdm` INT NOT NULL,
  `zzmc` VARCHAR(256) NOT NULL,
  `xzqhm` VARCHAR(6) NOT NULL,
  `dqmc` VARCHAR(32) NOT NULL,
  `bjmc` VARCHAR(16) NULL,
  `xd` INT NULL,
  `nj` INT NULL,
  `szdw` VARCHAR(256) NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
