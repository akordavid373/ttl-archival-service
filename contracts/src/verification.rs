use soroban_sdk::{contracttype, BytesN, Env, Symbol};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct VerificationResult {
    pub is_valid: bool,
    pub archive_id: BytesN<32>,
    pub verified_at: u64,
    pub checksum_valid: bool,
    pub hash_valid: bool,
    pub integrity_valid: bool,
    pub message: Symbol,
}
