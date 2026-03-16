use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, Symbol, Vec, Map, BytesN};

// Contract state storage
#[contracttype]
pub enum DataKey {
    Policy(u64),
    ArchiveRecord(BytesN<32>),
    Admin,
    PolicyCounter,
    ArchiveCounter,
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

#[contract]
pub struct ArchivalContract;

#[contractimpl]
impl ArchivalContract {
    /// Initialize the contract with admin address
    pub fn initialize(env: Env, admin: Address) {
        // Check if already initialized
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Contract already initialized");
        }

        // Set admin
        env.storage().instance().set(&DataKey::Admin, &admin);
        
        // Initialize counters
        env.storage().instance().set(&DataKey::PolicyCounter, &0u64);
        env.storage().instance().set(&DataKey::ArchiveCounter, &0u64);
    }

    /// Create a new archival policy
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
        // Check if creator is admin (for now, allow anyone)
        let policy_counter: u64 = env.storage().instance().get(&DataKey::PolicyCounter).unwrap_or(0);
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

        // Store policy
        env.storage().instance().set(&DataKey::Policy(new_policy_id), &policy);
        
        // Update counter
        env.storage().instance().set(&DataKey::PolicyCounter, &new_policy_id);

        // Emit event
        env.events().publish(
            (Symbol::new(&env, "policy_created"), new_policy_id),
            (name, creator),
        );

        new_policy_id
    }

    /// Create a new archive record
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
        // Verify policy exists
        let policy: ArchivePolicy = env.storage().instance()
            .get(&DataKey::Policy(policy_id))
            .unwrap_or_else(|| panic!("Policy not found"));

        // Generate archive record ID (hash of policy_id + timestamp + creator)
        let timestamp = env.ledger().timestamp();
        let mut id_data = Vec::new(&env);
        id_data.push_back(policy_id.into());
        id_data.push_back(timestamp.into());
        id_data.push_back(creator.clone().into());
        let archive_id: BytesN<32> = env.crypto().sha256(&id_data);

        // Calculate expiry time
        let ttl_seconds = policy.ttl_days as u64 * 24 * 60 * 60;
        let expires_at = timestamp + ttl_seconds;

        let record = ArchiveRecord {
            id: archive_id,
            policy_id,
            original_data_hash,
            data_type,
            file_size,
            checksum,
            metadata,
            status: Symbol::new(&env, "archived"),
            expires_at,
            archived_at: timestamp,
            created_by: creator,
        };

        // Store archive record
        env.storage().instance().set(&DataKey::ArchiveRecord(archive_id), &record);

        // Emit event
        env.events().publish(
            (Symbol::new(&env, "archive_created"), archive_id),
            (policy_id, creator, expires_at),
        );

        archive_id
    }

    /// Get policy by ID
    pub fn get_policy(env: Env, policy_id: u64) -> ArchivePolicy {
        env.storage().instance()
            .get(&DataKey::Policy(policy_id))
            .unwrap_or_else(|| panic!("Policy not found"))
    }

    /// Get archive record by ID
    pub fn get_archive_record(env: Env, archive_id: BytesN<32>) -> ArchiveRecord {
        env.storage().instance()
            .get(&DataKey::ArchiveRecord(archive_id))
            .unwrap_or_else(|| panic!("Archive record not found"))
    }

    /// Mark archive record as deleted
    pub fn delete_archive_record(env: Env, archive_id: BytesN<32>, deleter: Address) {
        let mut record: ArchiveRecord = env.storage().instance()
            .get(&DataKey::ArchiveRecord(archive_id))
            .unwrap_or_else(|| panic!("Archive record not found"));

        // Check if deleter is the creator or admin
        let admin: Address = env.storage().instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"));

        if record.created_by != deleter && deleter != admin {
            panic!("Unauthorized to delete this record");
        }

        // Update status
        record.status = Symbol::new(&env, "deleted");
        
        // Store updated record
        env.storage().instance().set(&DataKey::ArchiveRecord(archive_id), &record);

        // Emit event
        env.events().publish(
            (Symbol::new(&env, "archive_deleted"), archive_id),
            deleter,
        );
    }

    /// Get all policies for a creator
    pub fn get_policies_by_creator(env: Env, creator: Address) -> Vec<ArchivePolicy> {
        let policy_counter: u64 = env.storage().instance().get(&DataKey::PolicyCounter).unwrap_or(0);
        let mut policies = Vec::new(&env);

        for i in 1..=policy_counter {
            if let Some(policy) = env.storage().instance().get(&DataKey::Policy(i)) {
                if policy.created_by == creator {
                    policies.push_back(policy);
                }
            }
        }

        policies
    }

    /// Get all archive records for a creator
    pub fn get_archives_by_creator(env: Env, creator: Address) -> Vec<ArchiveRecord> {
        let archive_counter: u64 = env.storage().instance().get(&DataKey::ArchiveCounter).unwrap_or(0);
        let mut records = Vec::new(&env);

        // Note: In a real implementation, you'd want a more efficient way to query
        // This is a simplified approach for demonstration
        for i in 1..=archive_counter {
            // This is a placeholder - you'd need to implement proper indexing
        }

        records
    }

    /// Check if archive record has expired
    pub fn is_expired(env: Env, archive_id: BytesN<32>) -> bool {
        let record: ArchiveRecord = env.storage().instance()
            .get(&DataKey::ArchiveRecord(archive_id))
            .unwrap_or_else(|| panic!("Archive record not found"));

        env.ledger().timestamp() > record.expires_at
    }

    /// Update admin address
    pub fn update_admin(env: Env, new_admin: Address, current_admin: Address) {
        let admin: Address = env.storage().instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"));

        if current_admin != admin {
            panic!("Unauthorized: Only admin can update admin");
        }

        env.storage().instance().set(&DataKey::Admin, &new_admin);

        // Emit event
        env.events().publish(
            Symbol::new(&env, "admin_updated"),
            (current_admin, new_admin),
        );
    }

    /// Get contract admin
    pub fn get_admin(env: Env) -> Address {
        env.storage().instance()
            .get(&DataKey::Admin)
            .unwrap_or_else(|| panic!("Admin not set"))
    }
}
