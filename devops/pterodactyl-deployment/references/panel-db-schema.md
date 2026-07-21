# Pterodactyl Panel Database Schema Reference

Discovered from Panel latest (Docker, July 2026). Schema may vary by version.

## api_keys

| Column | Type | Notes |
|--------|------|-------|
| id | int unsigned PK | auto_increment |
| user_id | int unsigned FK | references users.id |
| key_type | tinyint unsigned | 0=none, 1=account, 2=application, 3=daemon_user, 4=daemon_application |
| identifier | char(16) | UNIQUE, prefix determines type: `ptla`=application, `ptdl`=daemon |
| token | text | **Encrypted** with APP_KEY via `encrypt()`, NOT a hash |
| allowed_ips | text nullable | JSON array |
| memo | text nullable | descriptive label |
| r_servers | tinyint unsigned | bitwise: 0=none, 1=read, 2=write, 3=read\|write |
| r_nodes | tinyint unsigned | same bitmask |
| r_allocations | tinyint unsigned | same bitmask |
| r_users | tinyint unsigned | same bitmask |
| r_locations | tinyint unsigned | same bitmask |
| r_nests | tinyint unsigned | same bitmask |
| r_eggs | tinyint unsigned | same bitmask |
| r_database_hosts | tinyint unsigned | same bitmask |
| r_server_databases | tinyint unsigned | same bitmask |

**Token verification:** `ApiKey::findToken($fullKey)` extracts identifier (first 16 chars), looks up by identifier, calls `decrypt($model->token)` and compares with remainder.

**Key type generation:** `ApiKey::generateTokenIdentifier($type)` generates the correct prefix.

## nodes

| Column | Type | Notes |
|--------|------|-------|
| id | int unsigned PK | |
| uuid | char(36) UNIQUE | |
| public | smallint unsigned | 1=visible |
| name | varchar(191) | |
| description | text nullable | |
| location_id | int unsigned FK | references locations.id |
| fqdn | varchar(191) | IP or domain |
| scheme | varchar(191) | default "https" |
| behind_proxy | tinyint | **NOT** `behind_proxied` |
| maintenance_mode | tinyint | |
| memory | int unsigned | in MB |
| memory_overallocate | int | |
| disk | int unsigned | in MB |
| disk_overallocate | int | |
| upload_size | int unsigned | default 100 |
| daemon_token_id | char(16) UNIQUE | FK to api_keys.identifier |
| daemon_token | text | encrypted with APP_KEY |
| daemonListen | smallint unsigned | default 8080 — **camelCase** |
| daemonSFTP | smallint unsigned | default 2022 — **camelCase** |
| daemonBase | varchar(191) | default /home/daemon-files — **camelCase** |

## allocations

| Column | Type | Notes |
|--------|------|-------|
| id | int unsigned PK | |
| node_id | int unsigned FK | references nodes.id |
| ip | varchar(191) | |
| ip_alias | text nullable | |
| port | mediumint unsigned | |
| server_id | int unsigned nullable | FK to servers.id (NULL = unassigned) |
| notes | varchar(191) nullable | **NOT** `note` |

## locations

| Column | Type | Notes |
|--------|------|-------|
| id | int unsigned PK | |
| short | varchar UNIQUE | e.g. "default" |
| long | varchar | display name |
