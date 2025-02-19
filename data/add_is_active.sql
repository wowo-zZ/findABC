ALTER TABLE employees ADD COLUMN is_active BOOLEAN DEFAULT 1;

-- 为现有记录设置is_active值
UPDATE employees SET is_active = 1 WHERE is_active IS NULL;