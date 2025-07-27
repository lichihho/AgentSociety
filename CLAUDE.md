# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentSociety is an advanced framework for building and simulating LLM-driven agents in urban environments. The framework uses a layered architecture with agents that have memory, reasoning capabilities, and can interact with simulated environments.

## Development Commands

### Python Package Management
- **Install dependencies**: `uv sync` (uses UV workspace with multiple packages)
- **Install dev dependencies**: `uv sync --group dev`
- **Linting**: `ruff check` and `ruff format`

### Frontend Development
```bash
cd frontend/
npm run dev      # Start development server
npm run build    # Build for production  
npm run lint     # Run ESLint
```

### Documentation
- **Build docs**: `./scripts/gen_docs.sh` (installs Sphinx dependencies and builds HTML docs)
- **Preview docs**: `make html` (from project root)

### Docker
- **Build container**: `./scripts/build_docker.sh` (builds agentsociety-runner:latest)
- **Custom tag**: `./scripts/build_docker.sh -t custom-tag`

## Architecture

### Workspace Structure
- **Root**: UV workspace with monorepo structure
- **packages/agentsociety/**: Core framework package
- **packages/agentsociety-community/**: Community agents and blocks
- **packages/agentsociety-benchmark/**: Benchmarking tools
- **frontend/**: React/TypeScript web UI (Vite + Ant Design)

### Core Components

#### Agent Layer (`agentsociety/agent/`)
- **Agent Base**: `agent_base.py` - Core agent interface
- **Context**: Memory management and agent state
- **Blocks**: Modular reasoning components (cognition, mobility, social, etc.)
- **Dispatcher**: Agent workflow orchestration

#### Environment Layer (`agentsociety/environment/`)
- **Simulation**: Urban environment simulation via GRPC services
- **Map Data**: Geospatial data handling with Shapely/pyproj
- **Economy**: Economic simulation client

#### Message Layer (`agentsociety/message/`)
- **Messager**: P2P, P2G, and group communication
- **Interceptors**: Message filtering and processing

#### Storage (`agentsociety/storage/`)
- **Database**: SQLAlchemy async models
- **Vector Store**: Qdrant integration for embeddings

### Agent Blocks System
Agents use a modular block architecture in `cityagent/blocks/`:
- **cognition_block.py**: Decision-making and reasoning
- **mobility_block.py**: Movement and spatial behavior  
- **social_block.py**: Social interactions and messaging
- **economy_block.py**: Economic behaviors and transactions
- **needs_block.py**: Maslow's hierarchy-based needs modeling
- **plan_block.py**: Planning and goal management

## Key Technologies
- **Python 3.11+** with async/await patterns
- **UV** for package management and workspace
- **Ray** for distributed execution  
- **FastAPI** for web API
- **SQLAlchemy** for database ORM
- **GRPC/Protobuf** for simulation services
- **Qdrant** for vector storage
- **React/TypeScript** for frontend UI

## Configuration
- Environment configs in `agentsociety/configs/`
- Agent profiles as JSON files in `examples/`
- Experiment configurations via YAML

## CLI Usage
Main CLI entry point: `agentsociety` command (installed via pip)
CLI implementation in `agentsociety/cli/cli.py`