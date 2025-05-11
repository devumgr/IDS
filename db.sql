CREATE DATABASE captured_packets;
\c captured_packets;          -- psql shortcut to connect to the database

CREATE TABLE packets (
    id          BIGSERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    src_ip      inet        NOT NULL,
    dst_ip      inet        NOT NULL,
    protocol    varchar(10),
    src_port    smallint,
    dst_port    smallint,
    length      integer,
    flags       jsonb,
    payload     bytea
);

CREATE INDEX idx_packets_ts      ON packets (ts);
CREATE INDEX idx_packets_src_ip  ON packets (src_ip);
CREATE INDEX idx_packets_dst_ip  ON packets (dst_ip);
