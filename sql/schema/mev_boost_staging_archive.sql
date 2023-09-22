create table flashbots.mev_boost_staging_archive (    
    relay string not null comment 'the relay that claimed the slot',
    slot integer not null comment 'slot number',
    parent_hash string not null comment 'hash of the parent block',
    block_hash string not null comment 'hash of the block',
    builder_pubkey string not null comment 'public key of builder',
    proposer_pubkey string not null comment 'public key of proposer',
    proposer_fee_recipient string not null comment 'fee recipient of proposer',
    gas_limit integer not null comment 'the maximum gas allowed in this block',
    gas_used integer not null comment 'the total used gas by all transactions in this block',
    value numeric not null comment 'mev block reward',
    num_tx integer not null comment 'the number of transactions in the block',
    block_number integer not null comment 'the block number',
    reorged boolean not null comment 'whether a block was reorged'
);