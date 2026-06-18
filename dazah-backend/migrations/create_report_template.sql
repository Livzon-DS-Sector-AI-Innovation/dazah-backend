-- 报告模板表
CREATE TABLE IF NOT EXISTS quality.report_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '模板名称',
    description TEXT COMMENT '模板描述',
    file_path VARCHAR(512) COMMENT '模板文件存储路径',
    is_active SMALLINT NOT NULL DEFAULT 1 COMMENT '启用状态：1=启用 0=停用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
);

-- 添加注释
COMMENT ON TABLE quality.report_template IS '报告模板表';
COMMENT ON COLUMN quality.report_template.id IS '主键ID';
COMMENT ON COLUMN quality.report_template.name IS '模板名称';
COMMENT ON COLUMN quality.report_template.description IS '模板描述';
COMMENT ON COLUMN quality.report_template.file_path IS '模板文件存储路径';
COMMENT ON COLUMN quality.report_template.is_active IS '启用状态：1=启用 0=停用';
COMMENT ON COLUMN quality.report_template.create_time IS '创建时间';
COMMENT ON COLUMN quality.report_template.update_time IS '更新时间';

-- 插入默认模板（可选）
-- INSERT INTO quality.report_template (name, description, is_active)
-- VALUES ('标准偏差报告模板', '用于生成标准格式的偏差报告', 1);
