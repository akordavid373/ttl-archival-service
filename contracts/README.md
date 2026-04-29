# Stellar Smart Contracts for TTL-Aware Automated Archival Service

This directory contains the Stellar smart contracts (Soroban) for the TTL-Aware Automated Archival Service.

## Tech Stack

- **Rust** - Smart contract language
- **Soroban** - Stellar smart contract platform
- **Stellar SDK** - JavaScript/Python integration
- **Freighter** - Stellar wallet integration

## Contract Features

### ArchivalContract

The main contract handles:

- **Policy Management**: Create and manage TTL-based archival policies
- **Archive Records**: Store and manage archived data records with blockchain verification
- **Access Control**: Role-based permissions for contract operations
- **Audit Trail**: Immutable record of all archival operations
- **Expiry Management**: On-chain TTL verification and cleanup tracking

### Key Functions

- `initialize(admin: Address)` - Initialize contract with admin
- `create_policy()` - Create new archival policy
- `create_archive_record()` - Create new archive record with blockchain verification
- `get_policy()` - Retrieve policy details
- `get_archive_record()` - Retrieve archive record
- `delete_archive_record()` - Mark record as deleted
- `is_expired()` - Check if record has expired
- `update_admin()` - Update contract admin

## Development

### Prerequisites

- Rust 1.70+
- Soroban CLI
- Stellar SDK

### Setup

```bash
# Install Soroban CLI
cargo install --locked soroban-cli

# Build contract
cargo build --target wasm32-unknown-unknown --release

# Or use Soroban CLI
soroban contract build
```

### Testing

```bash
# Run tests
cargo test

# Or use Soroban CLI
soroban contract test
```

### Deployment

```bash
# Deploy to Stellar Testnet
soroban contract deploy --wasm target/wasm32-unknown-unknown/release/archival_contract.wasm --network testnet

# Deploy to Stellar Mainnet
soroban contract deploy --wasm target/wasm32-unknown-unknown/release/archival_contract.wasm --network public
```

## Integration

### Backend Integration (Python)

```python
from stellar_sdk import Server, Keypair, TransactionBuilder, Network
from stellar_sdk.contract import ContractClient

# Connect to Stellar
server = Server("https://horizon-testnet.stellar.org")
contract_id = "CONTRACT_ID_HERE"

# Create contract client
contract_client = ContractClient(server, contract_id)

# Call contract function
result = contract_client.invoke(
    "create_policy",
    name="test_policy",
    description="Test policy",
    ttl_days=30,
    compression_enabled=True,
    encryption_enabled=False,
    auto_cleanup=True
)
```

### Frontend Integration (JavaScript)

```javascript
import { Contract } from "@stellar/freighter-api";
import { Networks, TransactionBuilder } from "stellar-sdk";

// Initialize contract
const contract = new Contract({
  contractId: "CONTRACT_ID_HERE",
  networkPassphrase: Networks.TESTNET,
  rpcUrl: "https://horizon-testnet.stellar.org",
});

// Create policy
const result = await contract.call("create_policy", {
  name: "test_policy",
  description: "Test policy",
  ttl_days: 30,
  compression_enabled: true,
  encryption_enabled: false,
  auto_cleanup: true,
});
```

## Architecture

### Data Structures

```rust
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
```

### Storage Pattern

- Instance storage for contract state
- Temporary storage for complex operations
- Events for real-time notifications

### Security Features

- Admin-only functions for critical operations
- Access control based on creator/admin roles
- Input validation and bounds checking
- Event logging for audit trails

## Networks

- **Standalone** - Local development
- **Futurenet** - Stellar test network
- **Public** - Stellar mainnet

## Monitoring

Events emitted by the contract:

- `policy_created` - New policy created
- `archive_created` - New archive record created
- `archive_deleted` - Archive record deleted
- `admin_updated` - Admin address updated

## License

MIT License - see LICENSE file for details.
