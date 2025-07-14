**Key CockroachDB Use Cases**
Use case - Why CockroachDB is a good fit

1.  User Accounts - geo-partitioning for optimized writes/reads for global customer base
2. Identity and Access Management (IAM) - high availability and immediate consistency are critical for secure authentication
3. Payments - strong consistency, high availability, minimal RTO, and zero RPO
4. Orders and Inventory for eCommerce apps - high availability, elastic scalability, data locality, and strong consistency


**CockroachDB Self-Hosted**
- you can create locality flags in self-hosted
```
cockroach start \
--join=<network address> \
--listen-addr=localhost:26257 \
--locality=rack=rack1
```

**When a node goes down**
- Cluster waits for the node to remain offline for 5 minutes before considering it dead and this time interval is configurable

Command to get Replication Factor:
`SHOW ZONE CONFIGURATION FROM RANGE default;`


**Garbage Collection**
- Default value is 4 hours
- code: `gc.ttlseconds`

**5 Layers of CockroachDB Architecture**
1. SQL - Translate SQL queries to KV operations. Understands SQL and plans request
2. Transactional - Allow atomic changes to multiple KV entries. Ensures safe and ordered changes to a record
3. Distribution - Present replicated KV ranges as a single entity. Routes request to the right place
4. Replication - Consistently and synchronoulsly replicate KV ranges across many nodes. Makes data safe and durable
5. Storage - Read write KV data on disk. Reads / Writes to disk


**Primary Key is Required**
- CockroachDB requires a primary key because it's a key value store underneath the hood. The Key requires a primary key

**MVCC**
- Multi-version Concurrency Control
- any update is appended as another KV record with a timestamp so you keep both records pre-update and post-update
- Pro: minimizes read-write contention and it allows multiple transactions to operate on different version of data simultaneously without blocking i.e. reads don't block writes and writes don't block reads
- Con: extra storage, but there is garbage collection
- the garbage collection default is 4 hours
- you can sitll get contention with two transactsion write to the same database. this is a write conflict so one transactions must be restarted to preserve consistency

**Hotspot**
- when one node or range is getting a lot of reads / writes
- there's not enough distribution
- recommendation is to have uuid as a PK

**Artificial Keys**
- if Primary Key is not defined, then CockroachDB will generate an artificial Primary Key that is unique row id (int8)

**Solving PK with Sequence / AutoIncrement**
- caching records upstream
- hash sharding the rowid to avoid hotspots

**SQL Order of Operations**
1. FROM / JOIN
2. WHERE
3. GROUP BY
4. HAVING
5. SELECT
6. DISTINCT
7. ORDER BY
8. LIMIT / OFFSET

**Optimizing Query Performance**
1. Measure query performance
2. Analyze most expensive queries
- Look into query clauses (`WHERE`, `ORDER BY`) to determine most popular columns
3. Create 1 or more indexes based on analysis
4. Important to not over-index because it slows down write performance
5. If you frequently request certain fields together, store that field in the index with a covered index
6. Use composite indexes to store columns used to sort or filter in your queries
7. Use covering indexes to store columns that are frequently returned but not part of a where clause


**Composite Index**
- a multi-column index
- good for read queries that include `WHERE` and `ORDER BY`

**Covered Indexes**
- `INDEX author_idx (author, publish_date) STORING title`
- STORING makes it a covered index


**Partial Indexes**
- not indexing every record
- filtering out a large subset in the index
```
CREATE INDEX recent_book_idx ON book (author, title)
WHERE publish_date > '1990-01-01'
```

**SQL Tuning**
- identify bottleneck SQL statements that do not meet an execution time
- Identifying bottlenecks: queries per second, execution time, latency, CPU percent usage, and contention
- use DB Console and EXPLAIN ANALYZE


**SQL Tuning Methodology**
1. Load Test - simulate real-world load
2. Bottleneck ID - use DB Console to identify problematic SQL statements
3. Statement Optimization - use EXPLAIN ANALYZE to understand plan and update. Reduce query response times and improve throughput
4. Repeat

**Best Practice for CPU Utilization**
- Each node should have 33% CPU head room

**Cost-Based Optimizer**
- CockroachDB uses cost-based optimizer
- most optimal plan based on performance and execution cost
- since it's a distributed database, the optimizer considers data locality and network cost
- cost-based optimizer does not take into consideration frequency of queries

**EXPLAIN**
- use `EXPLAIN` to anaylze queries. does not execute query and uses estimates
- shows execution plan and offers estimated row counts and costs
- it'll tell you if you're using an index or if the query is doing a full table scan which is something you want to avoid for popular queries
- read from the bottom and go up
- good to use when there's resource-intensive queries since it doesn’t execute statement. Safe to use with UPDATE, INSERT and DELETE since queries do not mutate production data


**EXPLAIN ANALYZE**
- use `EXPLAIN ANALYZE` to anaylze queries. executes query and returns actual results
- shows execution plan and offers actual row counts, execution time, and costs
- it'll tell you if you're using an index or if the query is doing a full table scan which is something you want to avoid for popular queries
- read from the bottom and go up
- use cautiously in production for resource-intensive queries and when using UPDATE, INSERT, and DELETE since queries mutate production data


**Types of spans when executing queries**
- FULL SCAN - scan all rows
- FULL SCAN (SOFT LIMIT) - full table scan can be performed, but will stop one enough rows have been scanned to meet statement
- LIMITED SCAN - table will be scanned on a subset because of index
- [/1 - /1] - this is a point lookup, indicates that a single row key is read


**SQL Performance Optimization Rules**
1. Get performance goal
2. Record bottleneck metrics
3. EXPLAIN or EXPLAIN ANALYZE
4. Optimize to scan as few rows as possible. Create indexes or update joins. Buffered-writes. Read Committed. Table locality.
5. Look at statement time in CockroachDB
6. Record notes - create excel sheet with query, execution time, and changes
7. Repeat
8. Stop when performance goal is met


**If there is no defined primary key**
- If no primary key is specified, CockroachDB will assign one
- variable: rowid
- data type: INT8 e.g. 9223372036854775807
- recommended primary key - DEFAULT gen_random_uuid()

**Primary Key Recommendations**
- even distribution
- immutable
- can be created without having to go to another nodes i.e. locally generatable


**Solution to Primary Key with Sequences/AutoIncrement**
1. use caching where each node maintains a separate cache for each connection
- cache expires when connection is terminated
- eliminates inefficient network call for every insert because sequences will make 2 network hops to geet the sequence to increment and gets the value
- the problem with cache is that insert order is not incremental. so the first insert can have id of 1 and the second insert that happens in another session can have id of 26
2. use hash sharding
- has sharded indexes are ideal for tables with sequential keys e.g. autoincrement or timestamps
- this can improve write performance but there's a slight trade-off in read performance

**Scatter**
- `ALTER TABLE bookly.uuid_pk SCATTER;`
- scatter command is used for distributing data ranges across the cluster
- usually for initial data loading or when encountering hotspots


**DB Isolation Levels**
1. Serializable
2. Snapshot
3. Repeatable Read
4. Read Committed
5. Read Uncommitted


**Transactions in CockroachDB**
- Transaction means you commit all or none to ensure consistency
- Commit = success with all changes applied
- Rollback = failure with all changes undone
- Transactions must be isolated - essential for distributed systems with multiple clients
- when migrating from `READ COMMITTED` database like Postgres to CockroachDB. Update isolation level in CockroachDB to `READ COMMMITTED`


**Pros of Serializable Isolation**
- ensures consistency
- eliminates need for pre or post transaction validation
- a failed serializable transaction will succeed when you retry


**Cons of Serializable Isolation**
- data anomalies turn into errors
- code must handle the exectpions with try/catch and the catch has a retry
- increase in exceptions leads to reduction in db efficiency
- less throughput
- increases conetention which is difficult to predict

**Contention**
- Contention occurs when multiple transactions (and one transaction writes) try to access the same rows at the same time, leading to performance degradation
- Contention is challenging to debug because it is difficult to predict
- Contention can cause row level locking so it's important that a retry is in transaction code
- Mitigating Contention:
1. locking - contending transactions are blocked and will wait after the first transaction commits
2. blocking - delay a response to application. The more blocking, the more significant the impact
3. aborting - aborted transaction throw a retry error. All previous work gets discarded and must be redone


**Dealing with Conention**
- `SELECT FOR UPDATE` this will lock the row and queue or block other transactions

**Order and type of Queries matter with Contention**
- If 2 UPDATE queries are contentious, it will be one after the other

Query 1
```
BEGIN;
UPDATE table SET value = 'A' WHERE key = 2;
COMMIT;
```
Query 2
```
BEGIN;
UPDATE table SET value = 'B' WHERE key = 2;
COMMIT;
```

<br>

- If 1 query is a SELECT, then this could introduce non-repeatable reads i.e. incorrect value. Serializable isolation prevents this
Query 1
```
BEGIN;
SELECT value FROM table WHERE key = 2;
UPDATE table SET value = 'A' WHERE key = 2;
COMMIT;
```

Query 2 begins after Query 1's SELECT statement is executed
```
BEGIN;
UPDATE table SET value = 'B'
WHERE key = 2;
COMMIT;
```


**Transaction Retry Best Pratices**
- retry logic helps ensure transaction consistency and minimizes database contention
- try-catch
- loop the try-catch block
- retry if you receive a retry error
- limit the loop with a max e.g. 3 retries
- include an exponential backoff
- avoid changing global state until transaction commits


**Optimizing Transactions**
- best practice is to minimize transaction # of rows and duration
- transaction breadth - # of rows a transaction touches
- transaction duration - how long a transactions lasts
- CTE (Common Table Expression) can limit transaction breadth
- CTEs are like a named subqeruy. It functions as a virtual table that only its main query can access

- Example of updating too many rows
```
BEGIN;
UPDATE book SET paperback_quantity = 0;
COMMIT;
```

- Example of updating a subset of relevant rows - optimized for transaction breadth
```
BEGIN;

WITH paperback_books AS (
  SELECT * FROM books
  WHERE paperback_quantity > 0
)

UPDATE books SET paperback_quantity = 0
FROM paperback_books
WHERE id IN (SELECT id FROM paperback_books);

COMMIT;
```

- Example of making small transactions - optimized for transaction duration
```
BEGIN;
UPDATE books SET paperback_quantity_status = 'unavailable'
WHERE paperback_quantity_status = 'available'
COMMIT;
```

<br>

```
BEGIN;
UPDATE book SET paperback_quantity = 0;
COMMIT;
```


**Implicit Transactions**
- Implicit transactions do not include `BEGIN` and `COMMIT`
- implicit transactions can be automatically retried by the database engine
- implicit transactions can lead to better efficency by avoid unnecessary round trips between the app and CockroachDB


**JDBC**
- Java Database Connectivity (JDBC) allows Java applications to interact with databases
- Things JDBC does:
1. Open connection
2. Create cursor
3. Submit query
4. Iterate over results
5. Close cursor
6. Close connection

**Auto Commit in JDBC**
- Default in plain JDBC
- Auto commit automatically commits changes to the database after each SQL statement so you don't need `BEGIN` and `COMMIT`
- automatically committing changes minimizes duration and reduces contention. only use for single SQL statements
- if you need multiple operations in a single transaction, consider switching back to explicit transactions

**Connection Pools**
- reusing connections instead of opening and closing new connections
- opening and closing thousands of new connections is resource intensive
- a potential drawback, if all connections are in use new requests will have to wait
- max number of connections = cores (or vCPU) x 4
- max connection lifetime = 300,000 ms or 5 minutes


