-- Migration 50: Drop Tim Pembina tables
-- Created: 2025-11-21
-- Description: Remove Tim Pembina functionality - drop tim_pembina and tim_pembina_peserta tables
-- Reason: Tim Pembina feature is no longer needed

USE entf7819_db-client-server;

-- Drop tim_pembina_peserta table first (has foreign key to tim_pembina)
DROP TABLE IF EXISTS tim_pembina_peserta;

-- Drop tim_pembina table
DROP TABLE IF EXISTS tim_pembina;

-- Migration success message
SELECT 'Migration 50 COMPLETED SUCCESSFULLY!' AS 'Status',
       'tim_pembina_peserta table dropped' AS 'tim_pembina_peserta',
       'tim_pembina table dropped' AS 'tim_pembina',
       'Tim Pembina functionality completely removed' AS 'Result';
