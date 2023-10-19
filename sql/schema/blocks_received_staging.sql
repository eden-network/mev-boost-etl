create table flashbots.blocks_received_staging (    
    relay string not null options(description='the relay that receveived the block'),
    slot integer not null options(description='slot number'),
    parent_hash string not null options(description='hash of the parent block'),
    block_hash string not null options(description='hash of the block'),
    builder_pubkey string not null options(description='public key of builder'),
    proposer_pubkey string not null options(description='public key of proposer'),
    proposer_fee_recipient string not null options(description='fee recipient of proposer'),
    gas_limit integer not null options(description='the maximum gas allowed in this block'),
    gas_used integer not null options(description='the total used gas by all transactions in this block'),
    value numeric not null options(description='mev block reward'),
    num_tx integer not null options(description='the number of transactions in the block'),
    block_number integer not null options(description='the block number'),
    timestamp timestamp not null options(description='timestamp block received'),
    timestamp_s integer not null options(description='timestamp in seconds when block received'),
    timestamp_ms integer not null options(description='timestamp in ms when block received'),
    optimistic_submission boolean not null options(description='whether block submitted was configured as optimistic')
);