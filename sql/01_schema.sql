DROP TABLE IF EXISTS calls CASCADE;
DROP TABLE IF EXISTS operators CASCADE;

CREATE TABLE operators (
    operator_id INT PRIMARY KEY,
    name        TEXT NOT NULL,
    team_id     TEXT NOT NULL,
    hire_date   DATE NOT NULL
);

CREATE TABLE calls (
    call_id       INT PRIMARY KEY,
    operator_id   INT NOT NULL REFERENCES operators(operator_id),
    client_id     INT NOT NULL,
    start_time    TIMESTAMP NOT NULL,
    duration_sec  INT NOT NULL,
    wait_time_sec INT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('completed', 'dropped')),
    rating        INT CHECK (rating BETWEEN 1 AND 5)
);

CREATE INDEX idx_calls_operator ON calls(operator_id);
CREATE INDEX idx_calls_start    ON calls(start_time);