# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python data stack project for downloading and managing datasets, primarily from Kaggle. The project uses Python 3.12 and uv for dependency management.

## Architecture

### Core Modules
- `src/ingestion/kaggle.py` - KaggleDatasetDownloader class for downloading Kaggle datasets
- `src/cleanup/dataset.py` - DatasetCleaner class for managing downloaded datasets  
- `main.py` - Interactive CLI menu for dataset operations

### Data Structure
- `data/raw/datasets/` - Raw downloaded datasets are stored here

## Development Setup

1. **Python Version**: 3.12 (specified in `.python-version`)
2. **Dependencies**: Managed via `pyproject.toml` with uv
3. **Environment**: Copy `.env.example` to `.env` for configuration

## Testing

- Test files are in `tests/` directory
- Run tests with: `pytest`
- Coverage reports available via `pytest-cov`

## Common Commands

### Running the Application
```bash
python main.py
```

### Testing
```bash
pytest                    # Run all tests
pytest --cov             # Run tests with coverage
```

### Dependencies
```bash
uv sync                   # Install dependencies
uv add <package>         # Add new dependency
```

## Features

1. **Kaggle Dataset Download** - Download datasets by name
2. **Dataset Management** - List, delete specific, or delete all datasets
3. **Interactive CLI** - Menu-driven interface for all operations