-- 数据库初始化脚本
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS aiagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE aiagent;

-- 设置时区
SET time_zone = '+08:00';

-- 创建用户（如果不存在）
-- CREATE USER IF NOT EXISTS 'aiagent'@'%' IDENTIFIED BY 'aiagent_password';
-- GRANT ALL PRIVILEGES ON aiagent.* TO 'aiagent'@'%';
-- FLUSH PRIVILEGES;
