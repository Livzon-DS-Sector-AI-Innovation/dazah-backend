-- 添加投入数量字段到批次表
-- 用于存储从生产记录投料操作汇总的实际投入数量

ALTER TABLE production.batches
ADD COLUMN IF NOT EXISTS input_qty DOUBLE PRECISION;

COMMENT ON COLUMN production.batches.input_qty IS '实际投入数量';