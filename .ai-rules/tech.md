---
title: Technology Stack
description: "Comprehensive overview of the technical architecture, dependencies, and toolchain."
inclusion: always
---

# Technology Stack

## Architecture Overview

AgentSociety follows a layered architecture with clear separation of concerns across multiple components:

- **Model Layer**: Centralized agent configuration and execution management
- **Agent Layer**: Multi-head workflow management with memory and decision-making systems
- **Message Layer**: Inter-agent communication infrastructure
- **Environment Layer**: Urban simulation environment and interaction handling
- **LLM Layer**: Large Language Model integration and API management
- **Tool Layer**: Supporting utilities for data processing and analysis

## Core Technologies

### Backend Framework
- **Python 3.11+**: Primary programming language with modern async/await support
- **FastAPI**: High-performance web framework for REST APIs and web interface
- **Uvicorn**: ASGI server for serving the FastAPI application
- **Ray**: Distributed computing framework for large-scale agent simulation
- **Pydantic**: Data validation and serialization using Python type hints

### Frontend Stack
- **React 18.3+**: Modern UI framework with hooks and functional components
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Ant Design**: Enterprise-class UI design language and components
- **MobX**: State management for reactive programming

### Database & Storage
- **SQLAlchemy**: ORM with async support for database operations
- **AsyncPG**: Async PostgreSQL adapter for production databases
- **AIOSqlite**: Async SQLite adapter for development and testing
- **Qdrant**: Vector database for embedding storage and similarity search
- **Boto3**: AWS S3 integration for file storage

### Geospatial & Simulation
- **PyProj**: Coordinate transformation and projection handling
- **Shapely**: Geometric operations and spatial analysis
- **GeoJSON**: Geographic data interchange format support
- **gRPC**: High-performance RPC framework for simulation services
- **Protocol Buffers**: Efficient data serialization

### LLM Integration
- **OpenAI**: API client for OpenAI models
- **Multiple Providers**: Support for DeepSeek, Qwen, ZhipuAI, SiliconFlow, VolcEngine
- **vLLM**: Self-hosted model inference with OpenAI-compatible API
- **JSON Repair**: Robust JSON parsing for LLM responses

### Visualization & UI Components
- **Monaco Editor**: VS Code editor component for code editing
- **Deck.gl**: WebGL-powered visualization for large datasets
- **Mapbox GL**: Interactive maps and geospatial visualization
- **Plotly.js**: Scientific charting and visualization
- **React Map GL**: React wrapper for Mapbox GL

### Development & Build Tools
- **UV**: Modern Python dependency management and virtual environment tool
- **Hatchling**: Python build backend for packaging
- **ESLint**: JavaScript/TypeScript linting
- **Ruff**: Fast Python linter and formatter
- **Docker**: Containerization for deployment

## Development Workflow

### Package Management
- **UV Workspace**: Monorepo structure with multiple Python packages
- **uv.lock**: Lockfile for reproducible dependency resolution
- **NPM**: Frontend dependency management with package-lock.json

### Testing & Quality
- **pytest**: Python testing framework (inferred from development patterns)
- **TypeScript Compiler**: Type checking for frontend code
- **ESLint**: Code quality and style enforcement for frontend

### Build & Deployment
- **Docker**: Multi-stage builds for containerized deployment
- **Sphinx**: Documentation generation with API docs
- **GitHub Actions**: CI/CD pipeline (inferred from repository structure)

## Key Dependencies

### Python Backend
```yaml
Core Framework:
  - fastapi>=0.103.1
  - uvicorn>=0.23.2
  - pydantic>=2.10.4
  - sqlalchemy[asyncio]>=2.0.20

Agent System:
  - ray[default]>=2.40.0
  - openai>=1.58.1
  - numpy>=1.20.0,<2.0.0

Geospatial:
  - shapely>=2.0.6
  - pyproj>=3.6.0
  - geojson>=3.1.0

Infrastructure:
  - grpcio>=1.71.0,<2.0.0
  - protobuf<=4.24.0,<5.0.0
  - kubernetes-asyncio>=32.3.0
```

### Frontend
```yaml
Core Framework:
  - react: ^18.3.1
  - typescript: ~5.6.2
  - vite: ^6.0.1

UI Components:
  - antd: ^5.22.5
  - @ant-design/pro-components: ^2.8.3
  - @monaco-editor/react: ^4.7.0

Visualization:
  - deck.gl: ^9.0.38
  - mapbox-gl: ^3.9.0
  - plotly.js: ^3.0.1

State Management:
  - mobx: ^6.13.5
  - mobx-react-lite: ^4.1.0
```

## Configuration Management

### Environment Configuration
- **YAML-based**: Primary configuration format for experiments and agents
- **Python Dotenv**: Environment variable management
- **Multi-environment**: Support for development, testing, and production configs

### Agent Configuration
- **Modular Blocks**: Configurable behavior blocks (cognition, economy, mobility, social)
- **Profile System**: JSON-based agent personality and behavior profiles
- **Workflow Definition**: YAML-based experiment workflow specification

## Performance Considerations

### Scalability
- **Distributed Processing**: Ray framework for multi-node agent simulation
- **Async Operations**: Full async/await support for I/O operations
- **Connection Pooling**: Database connection management for high concurrency
- **Semaphore Control**: LLM request rate limiting and concurrency management

### Memory Management
- **Agent Memory System**: Structured memory with static profiles and working memory
- **Vector Storage**: Efficient embedding storage and retrieval
- **Database Optimization**: Proper indexing and query optimization

## Security & Authentication

### API Security
- **Casdoor Integration**: OAuth-based authentication system
- **JWT Tokens**: Token-based authentication for API access
- **API Key Management**: Secure LLM API key handling

### Data Protection
- **Environment Variables**: Sensitive configuration externalization
- **Database Security**: Secure database connection strings
- **File System Access**: Controlled file system operations

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint and database testing
- **Agent Behavior Tests**: Simulation accuracy and reproducibility

### Frontend Testing
- **Component Tests**: React component unit testing
- **E2E Tests**: Full workflow testing through UI
- **TypeScript Validation**: Compile-time type checking

## Development Commands

```bash
# Backend Development
uv sync                    # Install dependencies
uv run agentsociety       # Run CLI commands
make html                 # Build documentation

# Frontend Development
npm install               # Install dependencies
npm run dev              # Start development server
npm run build            # Build for production
npm run lint             # Run linting

# Docker Operations
docker build -t agentsociety .
docker run -p 8000:8000 agentsociety
```