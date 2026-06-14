-- 给现有 news 表新增 status 字段（草稿/已发布/已下架）
-- 现有数据默认设为 published，保证移动端可见性不变。
-- 在 MySQL 客户端中对项目数据库（默认 news_app）执行：

ALTER TABLE `news`
    ADD COLUMN `status` ENUM('draft', 'published', 'offline')
    NOT NULL DEFAULT 'published'
    COMMENT '状态：草稿/已发布/已下架'
    AFTER `views`;

-- 可选：为按状态筛选建立索引
ALTER TABLE `news` ADD INDEX `idx_news_status` (`status`);
