# Installation Guide

## Core Installation

Install the core package with essential dependencies:
```bash
pip install -e .
```

## Optional Dependencies

### For visualization tools (matplotlib, pyvista):
```bash
pip install -e ".[viz]"
```

### For advanced geometry operations (shapely):
```bash
pip install -e ".[geometry]"
```

### For all features:
```bash
pip install -e ".[all]"
```

## Development Setup

For development with testing:
```bash
pip install -e ".[all,test]"
```

## Dependency Groups

- **Core**: numpy, scipy, pytest, pytest-cov
- **Visualization**: matplotlib, pyvista  
- **Geometry**: shapely
- **All**: Core + Visualization + Geometry
