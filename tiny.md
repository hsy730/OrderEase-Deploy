# 2C2G Server Resource Optimization Plan

## Overview
Optimize OrderEase deployment for 2CPU/2GB RAM server by adding resource limits to Docker containers and creating MySQL configuration tuned for low memory usage.

## Memory Allocation Strategy
- **Total Available**: 2GB RAM
- **OS + Docker Overhead**: ~400MB
- **Available for Containers**: ~1.6GB

| Container | Memory Limit | Memory Reservation | CPU Limit |
|-----------|--------------|-------------------|-----------|
| orderease-app | 700MB | 256MB | 1.5 cores |
| mysql | 800MB | 512MB | 0.5 cores |

## Files to Modify

### 1. Update `deploy/docker-compose.yml`
Add resource limits and mount my.cnf configuration file:

```yaml
services:
  orderease-app:
    # ... existing configuration ...
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 700M
        reservations:
          cpus: '0.25'
          memory: 256M

  mysql:
    # ... existing configuration ...
    volumes:
      - ./data/mysql:/var/lib/mysql
      - ./config/my.cnf:/etc/mysql/conf.d/custom.cnf:ro  # NEW
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 800M
        reservations:
          cpus: '0.1'
          memory: 512M
```

### 2. Create `deploy/config/my.cnf` (NEW FILE)
MySQL 8.0 configuration optimized for 2GB RAM:

```ini
[mysqld]
# Character Set
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
init-connect='SET NAMES utf8mb4'

# Connection Settings
max_connections=50
max_user_connections=40
wait_timeout=600
interactive_timeout=600

# InnoDB Settings (400MB buffer pool = 50% of MySQL container memory)
innodb_buffer_pool_size=400M
innodb_buffer_pool_instances=1
innodb_log_file_size=16M
innodb_log_buffer_size=16M
innodb_flush_log_at_trx_commit=2
innodb_flush_method=O_DIRECT
innodb_read_io_threads=4
innodb_write_io_threads=4
innodb_file_per_table=1
innodb_lock_wait_timeout=50

# MyISAM Settings
key_buffer_size=16M

# Thread Settings
thread_cache_size=8
thread_stack=256K

# Table & Cache Settings
table_definition_cache=400
table_open_cache=400
table_open_cache_instances=1
sort_buffer_size=256K
join_buffer_size=256K
read_buffer_size=128K
read_rnd_buffer_size=256K

# Query Execution
log_bin=0
slow_query_log=1
slow_query_log_file=/var/lib/mysql/slow-query.log
long_query_time=2
general_log=0

# Performance Schema (disabled to save ~50-100MB)
performance_schema=0

# Network Settings
max_allowed_packet=16M
connect_timeout=10

# Safety
symbolic_links=0
local_infile=0

# Temporary Table Settings
tmp_table_size=32M
max_heap_table_size=32M

# SQL Mode
sql_mode=STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION

[client]
default-character-set=utf8mb4

[mysql]
default-character-set=utf8mb4
```

## Key Trade-offs

| Setting | Trade-off | Impact |
|---------|-----------|--------|
| `innodb_flush_log_at_trx_commit=2` | Flush to OS cache, not disk every commit | Up to 1 second data loss on power failure (acceptable as payment gateway confirms orders) |
| `max_connections=50` | Fewer concurrent connections | May need connection pooling in Go app |
| `performance_schema=0` | No performance metrics | Saves ~50-100MB memory |
| `innodb_buffer_pool_size=400M` | Smaller buffer pool | More disk I/O for data not cached |

## Implementation Steps

1. Create `deploy/config/my.cnf` with the configuration above
2. Update `deploy/docker-compose.yml` with resource limits and my.cnf mount
3. Restart containers: `cd deploy && docker-compose down && docker-compose up -d`
4. Verify resource usage: `docker stats --no-stream`

## Critical Files

- `D:\local_code_repo\OrderEase\OrderEase-Deploy\deploy\docker-compose.yml`
- `D:\local_code_repo\OrderEase\OrderEase-Deploy\deploy\config\my.cnf` (NEW)
