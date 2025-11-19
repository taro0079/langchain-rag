# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain-based RAG (Retrieval-Augmented Generation) application built with FastAPI. The project uses a clean layered architecture with domain, infrastructure, and presentation layers.

## Architecture

The codebase follows a **layered architecture** with clear separation of concerns:

- **Domain Layer** (`src/domain/`): Contains business models and abstractions
  - `models.py`: Core data models (`UserQuery`, `AiAnswer`)
  - `interfaces.py`: Abstract interfaces that define service contracts (e.g., `IRagService`)

- **Infrastructure Layer** (`src/infrastructure/`): Implements domain interfaces
  - `rag_service.py`: Implements `IRagService` using LangChain components (e.g., `LangChainRagService`)
  - Handles integration with external services like OpenAI and Chroma vector store

- **Presentation Layer** (`src/presentation/`): HTTP API endpoints
  - `router.py`: FastAPI router with endpoints for chat functionality
  - Defines request/response models using Pydantic

- **Entry Point**: `main.py` initializes and runs the FastAPI application

## Development Commands

**Setup and Installation:**
```bash
# Install dependencies using uv (fast Python package installer)
uv sync
```

**Running the Application:**
```bash
# Start the FastAPI development server
python main.py

# Or using uvicorn directly with auto-reload
uvicorn main:app --reload
```

**Code Quality:**
```bash
# Linting (using ruff, if configured)
ruff check src/

# Type checking (using pyright or mypy)
pyright src/

# Format code (using ruff format)
ruff format src/
```

## Key Dependencies

- **FastAPI**: Web framework for building REST APIs
- **LangChain**: Framework for building applications with LLMs
- **langchain-chroma**: Chroma integration for vector storage and retrieval
- **langchain-openai**: OpenAI integration for using GPT models
- **python-dotenv**: Environment variable management
- **uvicorn**: ASGI server for running FastAPI

## Important Implementation Notes

1. **Dependency Injection**: Services implement abstract interfaces defined in the domain layer. Instantiate infrastructure implementations where needed.

2. **Vector Store**: The application uses Chroma with a persistent directory at `chroma_db/`. This stores embeddings for document retrieval.

3. **Environment Configuration**: Use `.env` files with `python-dotenv` for API keys and configuration (e.g., OpenAI API key).

4. **API Response Models**: Always use Pydantic models for request/response validation (see `ChatRequest`/`ChatResponse`).

5. **Work in Progress**: The `LangChainRagService.generate_answer()` method and related integration work are not yet fully implemented. Focus on integrating LangChain's RAG pipeline properly.

## Import Paths

When working with domain models and interfaces, use relative imports within the src directory structure (e.g., `from domain.models import UserQuery` in infrastructure files). Ensure the Python path includes the `src` directory when running the application.
