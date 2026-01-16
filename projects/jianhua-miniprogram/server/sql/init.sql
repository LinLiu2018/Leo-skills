-- 建华观园小程序数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS jianhua_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jianhua_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  phone VARCHAR(20) NOT NULL UNIQUE,
  nickname VARCHAR(50) DEFAULT '微信用户',
  avatar VARCHAR(255),
  invite_code VARCHAR(10) NOT NULL UNIQUE,
  inviter_id INT,
  invite_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_invite_code (invite_code),
  INDEX idx_inviter_id (inviter_id)
);

-- 礼品表
CREATE TABLE IF NOT EXISTS gifts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  description VARCHAR(255),
  required_invites INT DEFAULT 0,
  stock INT DEFAULT 999,
  sort_order INT DEFAULT 0,
  status TINYINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户礼品表
CREATE TABLE IF NOT EXISTS user_gifts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  gift_id INT NOT NULL,
  status ENUM('pending', 'claimed') DEFAULT 'pending',
  expire_at DATETIME,
  claimed_at DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_status (status)
);

-- 预约表
CREATE TABLE IF NOT EXISTS appointments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  appointment_date DATE NOT NULL,
  time_slot VARCHAR(20) NOT NULL,
  contact_name VARCHAR(50) NOT NULL,
  code VARCHAR(20) NOT NULL UNIQUE,
  gift_id INT,
  status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_code (code),
  INDEX idx_status (status)
);

-- 初始化礼品数据
INSERT INTO gifts (id, name, description, required_invites, sort_order) VALUES
(1, '抽纸1包', '优质抽纸一包', 0, 1),
(2, '洗衣液1瓶', '品牌洗衣液一瓶', 3, 2),
(3, '大米5斤', '优质大米5斤', 10, 3),
(4, '食用油1桶', '品牌食用油一桶', 20, 4),
(5, '神秘大奖', '惊喜大奖等你来拿', 50, 5);
