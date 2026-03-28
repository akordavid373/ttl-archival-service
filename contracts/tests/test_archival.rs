#![cfg(test)]

use soroban_sdk::testutils::Addresses;
use soroban_sdk::{Address, BytesN, Env, Symbol, Vec};

mod contract {
    soroban_sdk::contractimport!(
        file = "../target/wasm32-unknown-unknown/release/archival_contract.wasm"
    );
}

use contract::{ArchivalContract, ArchivalContractClient};

fn create_archive_id() -> BytesN<32> {
    let env = Env::default();
    let mut data = Vec::new(&env);
    data.push_back(1u64.into());
    data.push_back(1000u64.into());
    env.crypto().sha256(&data)
}

#[test]
fn test_initialize() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let stored_admin = client.get_admin();
    assert_eq!(stored_admin, admin);
}

#[test]
fn test_create_policy() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    assert!(policy_id > 0);

    let policy = client.get_policy(&policy_id);
    assert_eq!(policy.id, policy_id);
    assert_eq!(policy.ttl_days, 30);
    assert_eq!(policy.compression_enabled, true);
}

#[test]
fn test_create_archive_record() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "test_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    assert!(archive_id.is_valid());

    let record = client.get_archive_record(&archive_id);
    assert_eq!(record.policy_id, policy_id);
    assert_eq!(record.file_size, 1024);
}

#[test]
fn test_verify_archive() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "test_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    let result = client.verify_archive(&archive_id, &checksum);
    assert!(result.is_valid);
    assert!(result.checksum_valid);
}

#[test]
fn test_transfer_ownership() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let new_owner = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "test_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    let ownership = client.transfer_ownership(&archive_id, &new_owner, &creator);
    assert_eq!(ownership.current_owner, new_owner);
    assert!(ownership.transfer_count >= 1);
}

#[test]
fn test_update_metadata() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "original_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    let new_metadata = Symbol::new(&env, "updated_metadata");
    let record = client.update_metadata(&archive_id, &new_metadata, &creator);
    assert_eq!(record.metadata, new_metadata);
}

#[test]
fn test_get_archive_info() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "test_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    let info = client.get_archive_info(&archive_id);
    assert_eq!(info.id, archive_id);
    assert_eq!(info.policy_id, policy_id);
    assert_eq!(info.file_size, 1024);
    assert_eq!(info.status, Symbol::new(&env, "archived"));
}

#[test]
fn test_is_expired() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "test_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    let is_expired = client.is_expired(&archive_id);
    assert!(!is_expired);
}

#[test]
fn test_delete_archive_record() {
    let env = Env::default();
    let contract_id = env.register_contract(None, ArchivalContract);
    let client = ArchivalContractClient::new(&env, &contract_id);

    let admin = Address::random(&env);
    client.initialize(&admin);

    let creator = Address::random(&env);
    let name = Symbol::new(&env, "Test Policy");
    let description = Symbol::new(&env, "Test Description");

    let policy_id = client.create_policy(&name, &description, &30, &true, &false, &true, &creator);

    let data_hash: BytesN<32> = create_archive_id();
    let checksum: BytesN<32> = create_archive_id();
    let data_type = Symbol::new(&env, "test_data");
    let metadata = Symbol::new(&env, "test_metadata");

    let archive_id = client.create_archive_record(
        &policy_id, &data_hash, &data_type, &1024, &checksum, &metadata, &creator,
    );

    client.delete_archive_record(&archive_id, &creator);

    let record = client.get_archive_record(&archive_id);
    assert_eq!(record.status, Symbol::new(&env, "deleted"));
}
