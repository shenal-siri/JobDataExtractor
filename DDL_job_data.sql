/* Run these DDL statements inside an empty Postgres database */

CREATE TABLE job (
    id serial PRIMARY KEY,
    url varchar NOT NULL,
    title varchar NOT NULL,
    company varchar NOT NULL,
    location varchar NOT NULL,
    seniority varchar,
    employment_type varchar,
    time_add timestamptz DEFAULT now(),
    posting_text text NOT NULL,
    rejected boolean DEFAULT false,
    time_reject timestamptz
);

CREATE TABLE industry (
    id serial PRIMARY KEY,
    name varchar UNIQUE
);

CREATE TABLE function (
    id serial PRIMARY KEY,
    name varchar UNIQUE
);

CREATE TABLE job_industry(
    job_id int REFERENCES job(id) ON UPDATE CASCADE ON DELETE CASCADE,
    industry_id int REFERENCES industry(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT job_industry_pkey PRIMARY KEY (job_id, industry_id)
);

CREATE TABLE job_function(
    job_id int REFERENCES job(id) ON UPDATE CASCADE ON DELETE CASCADE,
    function_id int REFERENCES function(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT job_function_pkey PRIMARY KEY (job_id, function_id)
);


/* Initialize NULL rows in 'industry' and 'function tables */
INSERT INTO industry (name)
VALUES (NULL);

INSERT INTO function (name)
VALUES (NULL);


/* Create trigger function to update 'time_reject' for the 'job' table when updated */

CREATE FUNCTION trigger_set_reject_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.time_reject = NOW();
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_reject_timestamp
BEFORE UPDATE OF rejected ON job 
FOR EACH ROW EXECUTE FUNCTION trigger_set_reject_timestamp();
