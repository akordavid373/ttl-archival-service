# TTL-Aware Automated Archival Service

A comprehensive full-stack TTL-aware automated archival service with Stellar blockchain integration, featuring React frontend, FastAPI backend, and Soroban smart contracts for decentralized data management.

## 🚀 Project Status: **Scaffolded & Ready for Contributions**

This project is now **fully scaffolded** and ready for community contributions! We've set up the complete project structure with frontend, backend, smart contracts, and all necessary tooling.

**🎯 Next Step**: Create GitHub Issues to start community-driven development!

## 🏗️ Architecture Overview

### 📦 Monorepo Structure

```
ttl-archival-service/
├── frontend/          # React + TypeScript + Tailwind CSS
├── backend/           # FastAPI + SQLAlchemy + Stellar SDK
├── contracts/         # Stellar Smart Contracts (Rust/Soroban)
├── shared/            # Shared TypeScript types and utilities
├── scripts/           # Development and deployment scripts
└── docs/             # Comprehensive documentation
```

### 🌟 Tech Stack

**Frontend:**

- ⚛️ React 18 + TypeScript
- 🎨 Tailwind CSS + Radix UI
- 🔄 React Query for state management
- 🔗 Stellar SDK + Freighter wallet integration
- 🧪 Vitest + React Testing Library

**Backend:**

- 🐍 FastAPI + SQLAlchemy ORM
- 🗄️ PostgreSQL (SQLite for development)
- ⭐ Stellar SDK for blockchain integration
- 📋 Celery + Redis for background tasks
- 🧪 pytest with async support

**Smart Contracts:**

- 🦀 Rust + Soroban SDK
- ⭐ Stellar blockchain platform
- 🔧 Soroban CLI for development
- 🧪 Built-in testing framework

## 🎯 Key Features

### 🔄 TTL-Based Archival

- Automated data retention with configurable TTL policies
- Scheduled cleanup of expired records
- File compression and storage management
- Policy-based archival rules

### ⭐ Blockchain Integration

- Immutable audit trails on Stellar
- Cryptographic proof of archival
- Smart contract-based policy enforcement
- Real-time blockchain verification

### 🌐 Full-Stack Application

- Modern React frontend with responsive design
- RESTful API with comprehensive endpoints
- Real-time updates and notifications
- Comprehensive monitoring and analytics

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- Rust 1.70+
- Docker (optional)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/akordavid373/ttl-archival-service.git
cd ttl-archival-service

# Run setup script (installs all dependencies)
./scripts/setup.sh --dev

# Start development servers
npm run dev
```

### Individual Components

```bash
# Frontend development
cd frontend && npm run dev

# Backend development
cd backend && python -m uvicorn app.main:app --reload

# Smart contract development
cd contracts && cargo build
```

## 📋 How to Contribute

We're ready for community contributions! Here's how to get started:

### 1. 🎯 Pick an Issue

- Check [GitHub Issues](https://github.com/akordavid373/ttl-archival-service/issues)
- Look for `good first issue` labels
- Start with simple tasks to get familiar

### 2. 🔧 Set Up Environment

```bash
git clone https://github.com/YOUR_USERNAME/ttl-archival-service.git
cd ttl-archival-service
./scripts/setup.sh --dev
```

### 3. 🚀 Make Your Contribution

- Create a feature branch
- Make your changes
- Add tests
- Submit a Pull Request

### 4. 📚 Read the Guidelines

- [CONTRIBUTING.md](./CONTRIBUTING.md) - Detailed contribution guide
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) - Community guidelines
- [ROADMAP.md](./ROADMAP.md) - Project development plan

## 🎯 Priority Areas for Contributions

### 🔥 High Priority

1. **Backend API Implementation** - Core functionality
2. **Frontend UI Development** - User interface components
3. **Stellar Integration** - Blockchain features
4. **Testing Infrastructure** - Quality assurance

### 📋 Good First Issues

- UI components (buttons, forms, layouts)
- API endpoint implementations
- Documentation improvements
- Test case additions

### 🏗️ Current Project Status

#### ✅ Completed (Scaffolded)

- [x] Project structure and monorepo setup
- [x] Frontend scaffold (React + TypeScript)
- [x] Backend scaffold (FastAPI + SQLAlchemy)
- [x] Smart contract scaffold (Stellar/Soroban)
- [x] Development environment and scripts
- [x] Documentation and contribution guidelines
- [x] CI/CD configuration
- [x] Docker containerization

#### 🚧 Ready for Development

- [ ] Backend API implementation
- [ ] Frontend component development
- [ ] Smart contract logic
- [ ] Testing infrastructure
- [ ] Documentation enhancement

## 📚 Documentation

- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Smart Contract Docs](./contracts/README.md)** - Stellar contract details
- **[Development Guide](./CONTRIBUTING.md)** - Contribution guidelines
- **[Project Roadmap](./ROADMAP.md)** - Development phases

## 🧪 Testing

```bash
# Run all tests
npm run test

# Frontend tests
npm run test:frontend

# Backend tests
npm run test:backend

# Contract tests
npm run test:contracts
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker
npm run docker:build
npm run docker:up

# View logs
npm run docker:logs

# Stop services
npm run docker:down
```

## 🌐 Network Configuration

### Stellar Networks

- **Standalone** - Local development
- **Futurenet** - Stellar testnet
- **Public** - Stellar mainnet

### Environment Variables

```bash
# Copy and configure
cp .env.example .env

# Key variables
DATABASE_URL=postgresql://...
STELLAR_NETWORK=testnet
CONTRACT_ID=your_contract_id
```

## 📊 Project Metrics

- **Languages**: TypeScript, Python, Rust
- **Frameworks**: React, FastAPI, Soroban
- **Blockchain**: Stellar
- **Testing**: Vitest, pytest, Soroban test framework
- **Deployment**: Docker, Kubernetes

## 🤝 Community

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions
- **Contributors**: Welcome from all skill levels
- **Maintainers**: @akordavid373

## 🎯 Next Steps

1. **Create Issues** - Define specific tasks for contributors
2. **Set Up Labels** - Organize issues by difficulty and type
3. **Welcome Contributors** - Provide guidance and support
4. **Review PRs** - Ensure quality and consistency
5. **Release MVP** - Deploy first working version

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Ready to Build?

The project is fully scaffolded and waiting for contributors like you!

**🚀 [Check out open issues](https://github.com/akordavid373/ttl-archival-service/issues) and start contributing today!**

Whether you're interested in frontend development, backend APIs, smart contracts, or documentation - there's a place for you in this project.

**Let's build something amazing together!** ⭐
