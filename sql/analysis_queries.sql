
-- ==========================================
-- QUERY 1: OVERALL DATABASE SUMMARY
-- ==========================================

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT failure_event) AS event_categories,
    MIN(timestamp) AS first_record,
    MAX(timestamp) AS last_record
FROM sensor_readings;


-- ==========================================
-- QUERY 2: FAILURE EVENT DISTRIBUTION
-- ==========================================

SELECT
    failure_event,
    COUNT(*) AS total_records,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM sensor_readings),
        2
    ) AS percentage
FROM sensor_readings
GROUP BY failure_event
ORDER BY total_records DESC;


-- ==========================================
-- QUERY 3: SENSOR COMPARISON BY EVENT
-- LOADED OPERATION ONLY
-- ==========================================

SELECT
    failure_event,
    COUNT(*) AS record_count,
    ROUND(AVG(TP2), 3) AS avg_TP2,
    ROUND(AVG(TP3), 3) AS avg_TP3,
    ROUND(AVG(H1), 3) AS avg_H1,
    ROUND(AVG(Reservoirs), 3) AS avg_reservoirs,
    ROUND(AVG(Oil_temperature), 3) AS avg_oil_temperature,
    ROUND(AVG(Motor_current), 3) AS avg_motor_current
FROM sensor_readings
WHERE DV_eletric = 1
GROUP BY failure_event
ORDER BY failure_event;


-- ==========================================
-- QUERY 4: OPERATING STATE ANALYSIS
-- ==========================================

SELECT
    failure_event,
    COUNT(*) AS total_records,

    ROUND(
        AVG(COMP) * 100, 2
    ) AS COMP_active_percentage,

    ROUND(
        AVG(DV_eletric) * 100, 2
    ) AS DV_electric_percentage,

    ROUND(
        AVG(Towers) * 100, 2
    ) AS Towers_active_percentage,

    ROUND(
        AVG(MPG) * 100, 2
    ) AS MPG_active_percentage

FROM sensor_readings
GROUP BY failure_event
ORDER BY failure_event;


-- ==========================================
-- QUERY 5: OIL TEMPERATURE BY DAY
-- ==========================================

SELECT
    DATE(timestamp) AS reading_date,
    failure_event,
    ROUND(AVG(Oil_temperature), 2) AS avg_oil_temperature,
    ROUND(MAX(Oil_temperature), 2) AS max_oil_temperature,
    COUNT(*) AS total_readings

FROM sensor_readings

GROUP BY
    DATE(timestamp),
    failure_event

ORDER BY reading_date
LIMIT 30;


-- ==========================================
-- QUERY 6: PRESSURE ANALYSIS
-- ==========================================

SELECT
    failure_event,
    ROUND(AVG(TP2), 3) AS avg_TP2,
    ROUND(AVG(TP3), 3) AS avg_TP3,
    ROUND(AVG(H1), 3) AS avg_H1,
    ROUND(AVG(DV_pressure), 3) AS avg_DV_pressure,
    ROUND(AVG(Reservoirs), 3) AS avg_reservoirs

FROM sensor_readings

GROUP BY failure_event

ORDER BY failure_event;
