-- Топ-10 операторов по количеству ошибок
WITH error_flags AS (
    SELECT
        c.call_id, c.operator_id,
        CASE
            WHEN c.status = 'dropped'                               THEN 1
            WHEN c.wait_time_sec > 120                              THEN 1
            WHEN c.rating IS NOT NULL AND c.rating < 3              THEN 1
            ELSE 0
        END AS is_error
    FROM calls c
)
SELECT
    o.operator_id,
    o.name,
    o.team_id,
    COUNT(*)                              AS total_calls,
    SUM(ef.is_error)                      AS errors,
    ROUND(100.0 * SUM(ef.is_error) / COUNT(*), 2) AS error_rate_pct,
    RANK() OVER (ORDER BY SUM(ef.is_error) DESC) AS error_rank   -- оконная
FROM error_flags ef
JOIN operators o USING (operator_id)
GROUP BY o.operator_id, o.name, o.team_id
ORDER BY errors DESC
LIMIT 10;

-- Накопительные долгие паузы по дням
WITH daily AS (
    SELECT
        DATE(start_time) AS call_date,
        COUNT(*)         AS calls,
        SUM(CASE WHEN wait_time_sec > 120 THEN 1 ELSE 0 END) AS long_pauses
    FROM calls
    GROUP BY DATE(start_time)
)
SELECT
    call_date,
    calls,
    long_pauses,
    SUM(long_pauses) OVER (ORDER BY call_date) AS cum_long_pauses   -- окно
FROM daily
ORDER BY call_date;

-- Статистика по каждому оператору — выносим в TEMP
CREATE TEMP TABLE operator_stats AS
SELECT
    operator_id,
    COUNT(*)                                       AS total_calls,
    AVG(duration_sec)                              AS avg_duration,
    SUM(CASE WHEN status = 'dropped' THEN 1 ELSE 0 END) AS dropped,
    AVG(rating)                                    AS avg_rating
FROM calls
GROUP BY operator_id;

-- Операторы, у которых ошибок больше среднего
SELECT o.name, o.team_id, s.dropped, s.avg_rating
FROM operator_stats s
JOIN operators o USING (operator_id)
WHERE s.dropped > (SELECT AVG(dropped) FROM operator_stats)
ORDER BY s.dropped DESC;

-- Проверяем план: до/после индекса разница будет видна
EXPLAIN ANALYZE
SELECT operator_id, COUNT(*)
FROM calls
WHERE start_time >= '2026-10-15'
GROUP BY operator_id;