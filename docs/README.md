# TangoSim Documentation

Welcome to the TangoSim documentation! This directory contains comprehensive guides and API references for the Tango game simulator.

## Documentation Structure

### API Reference (`api/`)

Complete API documentation for all modules:

- **[models.md](api/models.md)** - Core game models (Tile, GameState) and utility functions
- **[gameengine.md](api/gameengine.md)** - Game loop and rule enforcement
- **[strategy.md](api/strategy.md)** - AI strategy interfaces and implementations

### Guides (`guides/`)

Step-by-step tutorials and conceptual guides:

- **[quickstart.md](guides/quickstart.md)** - Get up and running in minutes
- **[coordinates.md](guides/coordinates.md)** - Understanding the hexagonal coordinate system
- **[custom_strategies.md](guides/custom_strategies.md)** - Building your own AI strategies

### Images (`images/`)

Diagrams and visual aids for documentation (currently empty - add visualizations here).

## Quick Links

### Getting Started
- [Installation & First Game](guides/quickstart.md)
- [Project README](../README_future.md)

### Core Concepts
- [Hexagonal Grids](guides/coordinates.md)
- [Game Mechanics](api/gameengine.md)

### Development
- [Creating Strategies](guides/custom_strategies.md)
- [API Reference](api/)

## Documentation Goals

This documentation aims to:

1. **Enable Quick Start** - Get developers running simulations quickly
2. **Explain Core Concepts** - Clarify hexagonal coordinates, tile mechanics, and game rules
3. **Guide Development** - Show how to create custom strategies and extend the engine
4. **Provide Reference** - Complete API documentation for all public interfaces
5. **Share Examples** - Practical code examples throughout

## Contributing to Documentation

We welcome documentation improvements! When contributing:

1. **Accuracy**: Ensure technical accuracy by testing all code examples
2. **Clarity**: Write for developers new to hex grids and tile games
3. **Examples**: Include working code examples wherever possible
4. **Consistency**: Follow the existing structure and style
5. **Completeness**: Update related docs when changing APIs

### Documentation Standards

- Use Markdown format
- Include code examples with syntax highlighting
- Link to related documentation
- Keep language clear and concise
- Test all code snippets

## Building HTML Documentation (Future)

The project may add Sphinx or MkDocs in the future for generating HTML documentation. For now, all documentation is in Markdown format and can be read directly in GitHub or any Markdown viewer.

Potential future tools:
- **Sphinx** for Python API documentation
- **MkDocs** for general documentation site
- **Read the Docs** for hosting

## Documentation TODO

Future documentation improvements:

- [ ] Add game rules detailed guide
- [ ] Create tile mechanics deep dive
- [ ] Add scoring system explanation
- [ ] Include board state visualization guide
- [ ] Create strategy comparison analysis
- [ ] Add performance optimization guide
- [ ] Include diagrams in `images/`
- [ ] Add troubleshooting guide
- [ ] Create contributing guidelines
- [ ] Add examples directory with runnable scripts

## Questions or Issues?

- Open an issue on GitHub
- Check the [main README](../README_future.md)
- Review the [Quick Start guide](guides/quickstart.md)

## Version

Documentation version corresponds to TangoSim version 0.1.0
