use soroban_sdk::{contracttype, Address, BytesN, Env, Symbol};

#[contracttype]
pub enum StorageKey {
    ArchiveRecord(BytesN<32>),
    Owner(BytesN<32>),
    AuditTrail(BytesN<32>, u64),
    AuditCounter(BytesN<32>),
    DataHash(BytesN<32>),
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ArchiveOwnership {
    pub archive_id: BytesN<32>,
    pub current_owner: Address,
    pub original_owner: Address,
    pub transfer_count: u32,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AuditEntry {
    pub id: u64,
    pub archive_id: BytesN<32>,
    pub action: Symbol,
    pub actor: Address,
    pub timestamp: u64,
    pub details: Symbol,
    pub previous_owner: Option<Address>,
    pub new_owner: Option<Address>,
}
