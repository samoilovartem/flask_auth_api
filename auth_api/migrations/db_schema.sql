CREATE SCHEMA IF NOT EXISTS movies_auth;

CREATE TYPE movies_auth.auth_event_type AS ENUM (
    'login',
    'logout'
);

CREATE TABLE IF NOT EXISTS movies_auth.users (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    username                text        NOT NULL,
    password                text        NOT NULL,
    email                   text        NOT NULL,
    roles                   text        NULL,
    social_accounts         text        NULL,
    is_totp_enabled         boolean     DEFAULT false,
    two_factor_secret       text        DEFAULT false,
    created_at              timestamp with time zone DEFAULT (now()),
    updated_at              timestamp with time zone DEFAULT (now())
);


CREATE TABLE IF NOT EXISTS movies_auth.auth_history (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 uuid        NOT NULL,
    ip_address              text        NOT NULL,
    is_successful           boolean     DEFAULT false,
    device                  text        NULL,
    auth_event_type         movies_auth.auth_event_type,
    auth_event_time         timestamp with time zone DEFAULT (now()),
    auth_event_fingerprint  text        NOT NULL,
    FOREIGN KEY (user_id)
            REFERENCES movies_auth.users (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS movies_auth.tokens (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    token_owner_id          uuid        NOT NULL,
    token_value             text        NOT NULL,
    token_used              boolean     DEFAULT false,
    created_at              timestamp with time zone DEFAULT (now()),
    expires_at              timestamp with time zone DEFAULT (now()::DATE + 24),
    UNIQUE (token_owner_id, token_value),
    FOREIGN KEY (token_owner_id)
            REFERENCES movies_auth.users(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS movies_auth.roles (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name               text        NOT NULL,
    UNIQUE (role_name)
);

CREATE TABLE IF NOT EXISTS movies_auth.user_roles (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 uuid        NOT NULL,
    role_id                 uuid        NOT NULL,
    UNIQUE (user_id, role_id),
    FOREIGN KEY (user_id)
            REFERENCES movies_auth.users(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
    FOREIGN KEY (role_id)
            REFERENCES movies_auth.roles
            ON DELETE CASCADE
            ON UPDATE CASCADE
);
