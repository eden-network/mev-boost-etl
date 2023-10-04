create table flashbots.mev_boost_config (
    relay string not null options(description='the relay name/id'),
    url string not null options(description='the relay url'),
    batch_size integer not null options(description='the number of slots the relay api supports'),
    active boolean not null options(description='whether we should extract data from this relay'),
    back_fill boolean not null options(description='whether we should backfill data for this relay')
);