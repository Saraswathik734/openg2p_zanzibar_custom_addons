-- Worker Registry View
CREATE OR REPLACE VIEW g2p_worker_registry AS
SELECT 
    id              AS unique_id,
    name            AS name,
    email           AS email,
    phone           AS phone,
    age_group       AS age_group,
    province_id     AS province_id,
    district_id     AS district_id,
    constituency_id AS constituency_id,
    ward_id         AS ward_id
FROM res_partner
WHERE is_registrant = True 
AND is_group = False 
AND active = True;


-- Worker Registry Monthly View
CREATE OR REPLACE VIEW g2p_worker_registry_monthly AS
SELECT 
    partner_id           AS unique_id,
    name                 AS name,
    data_collection_month AS attendance_month,
    source_type          AS source_type
FROM g2p_enumerator;


-- Worker Registry Daily View
CREATE OR REPLACE VIEW g2p_worker_registry_daily AS
SELECT 
    worker_id     AS unique_id,
    nrc_number    AS nrc_number,
    date_of_work  AS attendance_date,
    task          AS task
FROM g2p_worker_attendance;
