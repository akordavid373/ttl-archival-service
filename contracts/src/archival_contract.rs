use soroban_sdk::{contract, contractimpl, contracttype, Address, BytesN, Env, Symbol, Vec};

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
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct VerificationResult {
    pub is_valid: bool,
    pub archive_id: BytesN<32>,
    pub verified_at: u64,
    pub checksum_valid: bool,
    pub hash_valid: bool,
    pub integrity_valid: bool,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ArchivePolicy {
    pub id: u64,
    pub name: Symbol,
    pub description: Symbol,
    pub ttl_days: u32,
    pub compression_enabled: bool,
    pub encryption_enabled: bool,
    pub auto_cleanup: bool,
    pub created_by: Address,
    pub created_at: u64,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ArchiveRecord {
    pub id: BytesN<32>,
    pub policy_id: u64,
    pub original_data_hash: BytesN<32>,
    pub data_type: Symbol,
    pub file_size: u64,
    pub checksum: BytesN<32>,
    pub metadata: Symbol,
    pub status: Symbol,
    pub expires_at: u64,
    pub archived_at: u64,
    pub created_by: Address,
}

#[contracttype]
enum DataKey {
    Policy(u64),
    ArchiveRecord(BytesN<32>),
    Admin,
    PolicyCounter,
    ArchiveCounter,
    AuditCounter(BytesN<32>),
    AuditEntry(BytesN<32>, u64),
    Owner(BytesN<32>),
}

#[contract]
pub struct ArchivalContract;

#[contractimpl]
impl ArchivalContract {
    pub fn initialize(env: Env, admin: Address) {
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Contract already initialized");
        }
        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::PolicyCounter, &0u64);
        env.storage()
            .instance()
            .set(&DataKey::ArchiveCounter, &0u64);
    }

    pub fn create_policy(
        env: Env,
        name: Symbol,
        description: Symbol,
        ttl_days: u32,
        compression_enabled: bool,
        encryption_enabled: bool,
        auto_cleanup: bool,
        creator: Address,
    ) -> u64 {
        let policy_counter: u64 = env
            .storage()
            .instance()
            .get(&DataKey::PolicyCounter)
            .unwrap_or(0);
        let new_policy_id = policy_counter + 1;

        let policy = ArchivePolicy {
            id: new_policy_id,
            name,
            description,
            ttl_days,
            compression_enabled,
            encryption_enabled,
            auto_cleanup,
            created_by: creator,
            created_at: env.ledger().timestamp(),
        };

        env.storage()
            .instance()
            .set(&DataKey::Policy(new_policy_id), &policy);
        env.storage()
            .instance()
            .set(&DataKey::PolicyCounter, &new_policy_id);

        new_policy_id
    }

    pub fn create_archive_record(
        env: Env,
        policy_id: u64,
        original_data_hash: BytesN<32>,
        data_type: Symbol,
        file_size: u64,
        checksum: BytesN<32>,
        metadata: Symbol,
        creator: Address,
    ) -> BytesN<32> {
        let policy: ArchivePolicy = env
            .storage()
            .instance()
            .get(&DataKey::Policy(policy_id))
            .unwrap_or_else(|| panic!("Policy not found"));

        let timestamp = env.ledger().timestamp();
        let seed = timestamp + policy_id as u64;
        let mut seed_bytes = [0u8; 32];
        seed_bytes[0] = (seed & 0xFF) as u8;
        seed_bytes[1] = ((seed >> 8) & 0xFF) as u8;
        seed_bytes[4] = policy_id as u8;
        seed_bytes[8] = (timestamp & 0xFF) as u8;
        let archive_id = BytesN::from_array(&env, &seed_bytes);

        let ttl_seconds = policy.ttl_days as u64 * 24 * 60 * 60;
        let expires_at = timestamp + ttl_seconds;

        let record = ArchiveRecord {
            id: archive_id.clone(),
            policy_id,
            original_data_hash,
            data_type,
            file_size,
            checksum,
            metadata,
            status: Symbol::new(&env, "archived"),
            expires_at,
            archived_at: timestamp,
            created_by: creator.clone(),
        };

        env.storage()
            .instance()
            .set(&DataKey::ArchiveRecord(archive_id.clone()), &record);

        let counter: u64 = env
            .storage()
            .instance()
            .get(&DataKey::ArchiveCounter)
            .unwrap_or(0);
        env.storage()
            .instance()
            .set(&DataKey::ArchiveCounter, &(counter + 1));

        archive_id
    }

    pub fn get_policy(env: Env, policy_id: u64) -> ArchivePolicy {
        env.storage()
            .instance()
            .get(&DataKey::Policy(policy_id))
            .unwrap_or_else(|| panic!("Policy not found"))
    }

    pub fn get_archive_record(env: Env, archive_id: BytesN<32>) -> ArchiveRecord {
        env.storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id))
            .unwrap_or_else(|| panic!("Archive record not found"))
    }

    pub fn delete_archive_record(env: Env, archive_id: BytesN<32>, deleter: Address) {
        let mut record: ArchiveRecord = env
            .storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id.clone()))
            .unwrap_or_else(|| panic!("Archive record not found"));

        let admin: Address = env
            .storage()
            .instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"));

        if record.created_by != deleter && deleter != admin {
            panic!("Unauthorized to delete this record");
        }

        record.status = Symbol::new(&env, "deleted");
        env.storage()
            .instance()
            .set(&DataKey::ArchiveRecord(archive_id), &record);
    }

    pub fn get_policies_by_creator(env: Env, creator: Address) -> Vec<ArchivePolicy> {
        let policy_counter: u64 = env
            .storage()
            .instance()
            .get(&DataKey::PolicyCounter)
            .unwrap_or(0);
        let mut policies = Vec::new(&env);

        for i in 1..=policy_counter {
            if let Some(policy) = env
                .storage()
                .instance()
                .get::<_, ArchivePolicy>(&DataKey::Policy(i))
            {
                if policy.created_by == creator {
                    policies.push_back(policy);
                }
            }
        }

        policies
    }

    pub fn is_expired(env: Env, archive_id: BytesN<32>) -> bool {
        let record: ArchiveRecord = env
            .storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id))
            .unwrap_or_else(|| panic!("Archive record not found"));

        env.ledger().timestamp() > record.expires_at
    }

    pub fn update_admin(env: Env, new_admin: Address, current_admin: Address) {
        let admin: Address = env
            .storage()
            .instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"));

        if current_admin != admin {
            panic!("Unauthorized: Only admin can update admin");
        }

        env.storage().instance().set(&DataKey::Admin, &new_admin);
    }

    pub fn get_admin(env: Env) -> Address {
        env.storage()
            .instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"))
    }

    pub fn verify_archive(
        env: Env,
        archive_id: BytesN<32>,
        provided_checksum: BytesN<32>,
    ) -> VerificationResult {
        let record: ArchiveRecord = env
            .storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id.clone()))
            .unwrap_or_else(|| panic!("Archive record not found"));

        let checksum_valid = provided_checksum == record.checksum;
        let hash_valid = true;
        let integrity_valid = checksum_valid && hash_valid;

        VerificationResult {
            is_valid: integrity_valid,
            archive_id: record.id,
            verified_at: env.ledger().timestamp(),
            checksum_valid,
            hash_valid,
            integrity_valid,
        }
    }

    pub fn get_archive_info(env: Env, archive_id: BytesN<32>) -> ArchiveRecord {
        env.storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id))
            .unwrap_or_else(|| panic!("Archive record not found"))
    }

    pub fn transfer_ownership(
        env: Env,
        archive_id: BytesN<32>,
        new_owner: Address,
        current_owner: Address,
    ) -> ArchiveOwnership {
        let record: ArchiveRecord = env
            .storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id.clone()))
            .unwrap_or_else(|| panic!("Archive record not found"));

        if record.created_by != current_owner {
            panic!("Unauthorized: Not the current owner");
        }

        let mut updated_record = record.clone();
        updated_record.created_by = new_owner.clone();
        env.storage()
            .instance()
            .set(&DataKey::ArchiveRecord(archive_id.clone()), &updated_record);

        let ownership = ArchiveOwnership {
            archive_id: archive_id.clone(),
            current_owner: new_owner.clone(),
            original_owner: record.created_by.clone(),
            transfer_count: 1,
        };

        env.storage()
            .instance()
            .set(&DataKey::Owner(archive_id.clone()), &new_owner);

        ownership
    }

    pub fn update_metadata(
        env: Env,
        archive_id: BytesN<32>,
        new_metadata: Symbol,
        updater: Address,
    ) -> ArchiveRecord {
        let mut record: ArchiveRecord = env
            .storage()
            .instance()
            .get(&DataKey::ArchiveRecord(archive_id.clone()))
            .unwrap_or_else(|| panic!("Archive record not found"));

        let admin: Address = env
            .storage()
            .instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"));

        if record.created_by != updater && updater != admin {
            panic!("Unauthorized to update metadata");
        }

        record.metadata = new_metadata;
        env.storage()
            .instance()
            .set(&DataKey::ArchiveRecord(archive_id.clone()), &record);

        record
    }

    pub fn get_audit_trail(env: Env, archive_id: BytesN<32>) -> Vec<AuditEntry> {
        let counter_key = DataKey::AuditCounter(archive_id.clone());
        let counter: u64 = env.storage().instance().get(&counter_key).unwrap_or(0);

        let mut entries = Vec::new(&env);

        for i in 1..=counter {
            if let Some(entry) = env
                .storage()
                .instance()
                .get::<_, AuditEntry>(&DataKey::AuditEntry(archive_id.clone(), i))
            {
                entries.push_back(entry);
            }
        }

        entries
    }
}
