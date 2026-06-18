-- 添加 sop_file_path 字段到 sop_rule 表
ALTER TABLE quality.sop_rule
ADD COLUMN IF NOT EXISTS sop_file_path VARCHAR(512);

COMMENT ON COLUMN quality.sop_rule.sop_file_path IS 'SOP文件路径';
