create table flashbots.mev_boost_staging_archive (    
    relay string not null options(description='the relay that claimed the slot'),
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
    reorged boolean not null options(description='whether a block was reorged)'
);