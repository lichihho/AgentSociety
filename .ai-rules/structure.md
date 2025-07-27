---
title: Project Structure
description: "Detailed overview of the codebase organization, file structure, and naming conventions."
inclusion: always
---

# Project Structure

## Repository Layout

AgentSociety follows a monorepo structure with clear separation between core packages, examples, documentation, and frontend components.

```
AgentSociety-CP/
├── .ai-rules/              # AI assistant steering files
├── packages/               # Core Python packages (workspace)
│   ├── agentsociety/       # Main framework package
│   ├── agentsociety-community/  # Community-contributed agents
│   └── agentsociety-benchmark/  # Benchmarking and evaluation tools
├── frontend/               # React-based web interface
├── docs/                   # Sphinx documentation
├── examples/               # Example simulations and configurations
├── dev-docs/              # Developer documentation
├── scripts/               # Build and deployment scripts
└── static/                # Static assets and images
```

## Core Package Structure

### Main Framework (`packages/agentsociety/`)

```
agentsociety/
├── agent/                  # Core agent system
│   ├── agent.py           # Main agent implementation
│   ├── agent_base.py      # Base agent class
│   ├── block.py           # Behavior block system
│   ├── context.py         # Agent context management
│   ├── memory_config_generator.py  # Memory system configuration
│   └── toolbox.py         # Agent tools and utilities
├── cityagent/             # Urban simulation agents
│   ├── blocks/            # Specialized behavior blocks
│   │   ├── cognition_block.py    # Decision-making logic
│   │   ├── economy_block.py      # Economic behaviors
│   │   ├── mobility_block.py     # Movement and transportation
│   │   ├── needs_block.py        # Maslow's hierarchy implementation
│   │   ├── social_block.py       # Social interactions
│   │   └── vision_block.py       # Visual perception
│   ├── societyagent.py    # Main city agent implementation
│   └── sharing_params.py  # Shared parameters and constants
├── environment/           # Simulation environment
│   ├── sim/              # City simulation services
│   ├── economy/          # Economic simulation client
│   └── utils/            # Environment utilities
├── llm/                  # LLM integration layer
├── message/              # Inter-agent messaging system
├── webapi/               # FastAPI web interface
│   ├── api/              # API endpoints
│   └── models/           # Pydantic data models
└── commercial/           # Enterprise features
    ├── auth/             # Authentication system
    ├── billing/          # Usage tracking and billing
    └── executor/         # Kubernetes deployment
```

### Community Extensions (`packages/agentsociety-community/`)

```
agentsociety-community/
├── agents/               # Community-contributed agent implementations
│   ├── citizens/         # Citizen agent variants
│   │   ├── cityagent/    # Basic city agent
│   │   ├── polarization/ # Polarization study agents
│   │   └── bdsc2025_*/   # Competition-specific agents
│   └── supervisors/      # Supervisor and orchestrator agents
├── blocks/               # Extended behavior blocks
└── workflows/            # Custom workflow implementations
```

### Benchmarking (`packages/agentsociety-benchmark/`)

```
agentsociety-benchmark/
├── benchmarks/           # Standardized benchmark tasks
│   ├── BehaviorModeling/ # Behavior replication benchmarks
│   ├── DailyMobility/    # Daily movement pattern benchmarks
│   └── HurricaneMobility/ # Crisis response benchmarks
├── cli/                  # Command-line interface for benchmarks
└── storage/              # Result storage and analysis
```

## Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   │   ├── Auth.tsx      # Authentication components
│   │   ├── MonacoPromptEditor.tsx  # Code editor integration
│   │   └── util.ts       # Frontend utilities
│   ├── pages/            # Page-level components
│   │   ├── Agent/        # Agent management interface
│   │   ├── Experiment/   # Experiment creation and monitoring
│   │   ├── Replay/       # Simulation replay and visualization
│   │   └── Survey/       # Survey management interface
│   ├── i18n/             # Internationalization
│   │   └── locales/      # Translation files (en, zh)
│   ├── types/            # TypeScript type definitions
│   └── utils/            # Frontend utility functions
├── public/               # Static assets
│   ├── icon/             # UI icons and avatars
│   └── monaco-editor/    # Monaco editor assets
└── package.json          # Frontend dependencies
```

## Documentation Structure (`docs/`)

```
docs/
├── 01-quick-start/       # Getting started guides
├── 02-version-1.5/       # Version-specific documentation
├── 03-configurations/    # Configuration guides
├── 04-experiment-design/ # Experiment design patterns
├── 05-custom-agents/     # Agent customization guides
├── 06-webui/             # Web interface documentation
├── 07-use-case/          # Research use case examples
├── 08-advanced-usage/    # Advanced topics
├── _static/              # Documentation assets
└── apidocs/              # Auto-generated API documentation
```

## Examples Organization (`examples/`)

```
examples/
├── config_templates/     # Example configuration files
├── polarization/         # Social polarization studies
│   ├── profiles/         # Agent personality profiles
│   └── *.py              # Study implementation scripts
├── hurricane_impact/     # Crisis response modeling
├── inflammatory_message/ # Information spread analysis
├── prospect_theory/      # Economic behavior studies
├── rumor_spreader/       # Misinformation propagation
└── UBI/                  # Universal Basic Income studies
```

## Naming Conventions

### Python Files
- **Snake Case**: All Python files use `snake_case.py`
- **Class Files**: Named after the main class they contain (e.g., `societyagent.py` contains `SocietyAgent`)
- **Module Files**: Descriptive names for functionality (e.g., `memory_config.py`, `sharing_params.py`)
- **Block Files**: Behavior blocks suffixed with `_block.py` (e.g., `cognition_block.py`)

### TypeScript Files
- **PascalCase Components**: React components use `PascalCase.tsx` (e.g., `AgentTemplate.tsx`)
- **CamelCase Utilities**: Utility files use `camelCase.ts` (e.g., `agentTemplateStore.ts`)
- **Lowercase Configs**: Configuration files use lowercase (e.g., `vite.config.ts`)

### Directories
- **Lowercase with Hyphens**: Package directories use `lowercase-with-hyphens`
- **CamelCase for Features**: Feature directories use `camelCase` or `PascalCase`
- **Descriptive Names**: Clear, descriptive directory names indicating purpose

### Configuration Files
- **YAML Extensions**: Configuration files use `.yaml` extension
- **Profile Files**: Agent profiles stored as `.json` files
- **Environment Files**: Use `.env` for environment variables

## Package Dependencies

### Workspace Configuration
- **UV Workspace**: Managed through `uv.lock` in root directory
- **Local Dependencies**: Packages reference each other through workspace configuration
- **Version Synchronization**: Shared version management across packages

### Import Patterns
- **Absolute Imports**: Use full package paths for clarity
- **Relative Imports**: Only for same-module imports
- **Namespace Packages**: Clear separation between core and community packages

## File Placement Guidelines

### New Agent Types
- **Core Agents**: Place in `packages/agentsociety/cityagent/`
- **Community Agents**: Place in `packages/agentsociety-community/agents/`
- **Specialized Agents**: Create subdirectories by domain (e.g., `citizens/`, `supervisors/`)

### New Behavior Blocks
- **Core Blocks**: Place in `packages/agentsociety/cityagent/blocks/`
- **Community Blocks**: Place in `packages/agentsociety-community/blocks/`
- **Utility Functions**: Shared utilities in `blocks/utils.py`

### New Examples
- **Research Examples**: Create domain-specific directories in `examples/`
- **Configuration Templates**: Place in `examples/config_templates/`
- **Profile Data**: Store in `examples/{domain}/profiles/`

### Frontend Components
- **Reusable Components**: Place in `frontend/src/components/`
- **Page Components**: Place in `frontend/src/pages/{FeatureName}/`
- **Utility Functions**: Place in `frontend/src/utils/`
- **Type Definitions**: Place in `frontend/src/types/`

### Documentation
- **User Guides**: Organized by user journey in numbered directories
- **API Documentation**: Auto-generated in `docs/apidocs/`
- **Developer Docs**: Place in `dev-docs/` for implementation details
- **Assets**: Store images and diagrams in `docs/_static/`

## Build Artifacts

### Generated Files
- **Python Builds**: Built wheels stored in `dist/` (gitignored)
- **Frontend Builds**: Built assets in `frontend/dist/` (gitignored)
- **Documentation**: Built docs in `build/` (gitignored)
- **Lock Files**: `uv.lock` and `package-lock.json` committed to repository

### Temporary Files
- **Python Cache**: `__pycache__/` directories (gitignored)
- **Virtual Environments**: `.venv/` directories (gitignored)
- **IDE Files**: Editor-specific files (gitignored)
- **Log Files**: Runtime logs (gitignored)