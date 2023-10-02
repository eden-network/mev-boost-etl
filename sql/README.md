## Staging

To remove (if already exists) and create the staging tables, use the following commands:

```bash
bq rm --table --force ethereum_mev_boost.mev_boost_staging && bq mk --table ethereum_mev_boost.mev_boost_staging ./schema/mev_boost_staging.json
```

## Production

To remove (if already exists) and create the production tables, use the following commands:

```bash
bq rm --table --force ethereum_mev_boost.mev_boost && bq mk --table --time_partitioning_field block_timestamp --time_partitioning_type DAY ethereum_mev_boost.mev_boost ./schema/mev_boost.json
```
