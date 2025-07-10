
Isolation levels of different DBs
- Postgres uses Read Committed isolation
- MySQL uses Repeatable Read isolation
- CockroachDB uses Serializable isolation

Contention more common with serializable isolation so you need to add app code retry logic
- try / catch. add retry logic in the catch
- max number of retries
- sleep timer with exponential backoff
