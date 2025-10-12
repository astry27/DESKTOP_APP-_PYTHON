ALTER TABLE admin ADD COLUMN peran ENUM('Admin', 'Operator', 'User') DEFAULT 'User' AFTER email;
UPDATE admin SET peran = 'Admin' WHERE username = 'admin';
UPDATE admin SET peran = 'Operator' WHERE username = 'operator';
UPDATE admin SET peran = 'User' WHERE username NOT IN ('admin', 'operator');