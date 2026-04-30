# Contributing to TTL-Aware Automated Archival Service

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/ttl-archival-service.git`
3. **Navigate to project**: `cd ttl-archival-service`
4. **Setup the development environment**: `./scripts/setup.sh --dev`
5. **Create a feature branch**: `git checkout -b feature/your-feature-name`
6. **Make your changes and test**: `npm run test`
7. **Commit your changes**: `git commit -m "feat: add your feature"`
8. **Push to your fork**: `git push origin feature/your-feature-name`
9. **Create a Pull Request**

## 📁 Project Structure

```
ttl-archival-service/
├── frontend/          # React + TypeScript frontend application
├── backend/           # FastAPI Python backend service
├── contracts/         # Stellar smart contracts (Rust/Soroban)
├── shared/            # Shared TypeScript types and utilities
├── scripts/           # Setup and development scripts
├── docs/             # Additional documentation
└── tests/            # Integration and end-to-end tests
```

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+
- Python 3.8+
- Rust 1.70+ (for smart contracts)
- Docker (optional, for containerized development)

### Environment Setup

1. **Clone and setup**:

   ```bash
   git clone https://github.com/YOUR_USERNAME/ttl-archival-service.git
   cd ttl-archival-service
   ./scripts/setup.sh --dev
   ```

2. **Environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development servers**:

   ```bash
   # Start both frontend and backend
   npm run dev

   # Or start individually
   npm run dev:frontend
   npm run dev:backend
   ```

## 🏗️ Architecture

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with Radix UI components
- **State Management**: React Query for server state
- **Blockchain**: Stellar SDK with Freighter wallet integration
- **Testing**: Vitest with React Testing Library

### Backend (FastAPI + Python)

- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL (with SQLite for development)
- **Blockchain**: Stellar SDK for Python
- **Task Queue**: Celery with Redis
- **Testing**: pytest with async support

### Smart Contracts (Rust + Soroban)

- **Language**: Rust with Soroban SDK
- **Platform**: Stellar blockchain
- **Testing**: Built-in Soroban test framework
- **Deployment**: Soroban CLI

## 📋 How to Contribute

### 🐛 Reporting Bugs

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with the "bug" label
3. **Include**:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, browser, etc.)
   - Screenshots if applicable

### ✨ Requesting Features

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with the "enhancement" label
3. **Include**:
   - Clear description of the feature
   - Use case and motivation
   - Proposed implementation (if you have ideas)
   - Acceptance criteria

### 🔧 Code Contributions

#### Frontend Contributions

1. **Component Development**:
   - Create components in `frontend/src/components/`
   - Follow existing naming conventions
   - Include TypeScript types
   - Add tests for new components

2. **Pages/Routes**:
   - Add pages in `frontend/src/pages/`
   - Update routing in `frontend/src/App.tsx`
   - Follow existing layout patterns

3. **Styling**:
   - Use Tailwind CSS classes
   - Follow component library patterns
   - Ensure responsive design

#### Backend Contributions

1. **API Endpoints**:
   - Add endpoints in `backend/app/main.py`
   - Create schemas in `backend/app/schemas.py`
   - Implement business logic in `backend/app/services/`
   - Add tests in `backend/tests/`

2. **Database Models**:
   - Define models in `backend/app/models.py`
   - Create Alembic migrations
   - Update service layer accordingly

3. **Blockchain Integration**:
   - Extend Stellar contract interactions
   - Add new contract functions
   - Update shared types

#### Smart Contract Contributions

1. **Contract Logic**:
   - Implement functions in `contracts/src/archival_contract.rs`
   - Add tests in `contracts/src/tests/`
   - Update contract documentation

2. **Deployment**:
   - Update deployment scripts
   - Add network configurations
   - Document deployment procedures

### 📝 Documentation

- **API Documentation**: Update OpenAPI specs in backend
- **Smart Contract Docs**: Update `contracts/README.md`
- **User Guides**: Update `docs/` directory
- **Code Comments**: Add inline documentation for complex logic

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm run test

# Run frontend tests
npm run test:frontend

# Run backend tests
npm run test:backend

# Run contract tests
npm run test:contracts

# Run with coverage
npm run test:coverage
```

### Testing Guidelines

1. **Frontend**: Use React Testing Library and Vitest
2. **Backend**: Use pytest with async support
3. **Contracts**: Use Soroban built-in testing
4. **Integration**: Add end-to-end tests for critical workflows
5. **Coverage**: Maintain >80% test coverage

## 🎯 Good First Issues

Look for issues labeled with:

- `good first issue` - Simple changes to get started
- `help wanted` - Issues needing community help
- `documentation` - Documentation improvements

## 📏 Code Style

### General Guidelines

- **Consistent formatting**: Use configured linters and formatters
- **Clear naming**: Use descriptive variable and function names
- **Comments**: Document complex logic and business rules
- **Types**: Use TypeScript for frontend, type hints for Python
- **Error handling**: Implement proper error handling and logging

### Specific Standards

- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + isort + mypy configuration
- **Contracts**: rustfmt configuration
- **Commits**: Conventional commit messages

## 🔄 Pull Request Process

1. **Update documentation** for any changes
2. **Add tests** for new functionality
3. **Ensure all tests pass**: `npm run test`
4. **Update CHANGELOG.md** if applicable
5. **Submit PR** with clear description
6. **Address review feedback** promptly

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Added tests for new functionality
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🏷️ Issue Labels

- `bug` - Bug reports
- `enhancement` - Feature requests
- `good first issue` - Good for newcomers
- `help wanted` - Community help needed
- `documentation` - Documentation issues
- `priority/high` - High priority issues
- `priority/medium` - Medium priority issues
- `priority/low` - Low priority issues

## 🤝 Community Guidelines

- **Be respectful** and inclusive
- **Welcome newcomers** and help them get started
- **Focus on constructive feedback**
- **Follow the code of conduct**
- **Ask questions** if anything is unclear

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For general questions and ideas
- **Documentation**: Check existing docs first
- **Maintainers**: Tag maintainainers for urgent issues

## 🎉 Recognition

Contributors will be recognized in:

- `README.md` contributors section
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to the TTL-Aware Automated Archival Service! 🚀
