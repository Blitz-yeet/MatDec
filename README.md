
# Material Decision Support for Sustainable Structures (MatDec)

## Project Overview

MatDec is an evolving project that explores how *structural engineering, **software design, and **data-driven methods* can be combined to support *more sustainable material and design decisions* in the built environment.

The project is intentionally developed *version by version*, with each version introducing new ideas, tools, or levels of abstraction.  
This repository is designed to grow over time, and *new versions, experiments, and future directions may be added as the project evolves*.

This README reflects the *current vision and planned direction*, and will be updated as that vision develops.

---

## Core Idea

Early-stage structural decisions have a disproportionate impact on:
- material use,
- embodied CO₂,
- cost,
- and overall design efficiency.

MatDec aims to investigate how computational tools can help engineers:
- reason about multiple design options,
- quantify environmental impact early,
- and make transparent, explainable trade-offs between performance and sustainability.

Rather than starting with black-box optimization or AI, the project begins with *first principles* and builds upward.

---

## Development Philosophy

The project follows a *layered and incremental approach*:

1. *Deterministic engineering models*
   - Classical structural mechanics
   - Closed-form solutions
   - Fully traceable assumptions

2. *Data-driven comparisons*
   - Structured material and section databases
   - Repeatable evaluation across alternatives
   - Explicit performance and CO₂ metrics

3. *Algorithms and optimization*
   - Filtering, ranking, and search strategies
   - Trade-off analysis between constraints and objectives

4. *Advanced methods (future)*
   - Statistical analysis across many design cases
   - Machine learning as a design assistant
   - Computer vision for interpreting conceptual inputs

Each layer is introduced only when the previous one is well understood.

---

## Repository Structure

MatDec/
├─ Version1/        # Deterministic beam selection with CO₂ optimization
├─ Version2/        # (Planned) Parametric inputs and expanded checks
├─ Version3/        # (Planned) Data analysis and algorithmic optimization
├─ Version4/        # (Planned) Machine learning–assisted design exploration
└─ README.md        # Project vision, roadmap, and context

The exact number of versions is *not fixed*.  
Additional versions, branches, or experimental folders may be added as new ideas are explored.

---

## Current Status

### Version 1 — Baseline

Version 1 establishes a *clear and verifiable baseline*:

- Simply supported steel beam
- Predefined loads and span
- Bending and deflection checks
- Embodied CO₂ calculation
- Selection of the lowest-CO₂ feasible section

This version is fully deterministic and intentionally simple.  
It serves as a reference point against which all future versions can be compared.

---

## Planned Future Directions

Future versions may include (non-exhaustive):

- Parametric problem definitions (span, loads, boundary conditions)
- Additional structural checks and constraints
- Integration of data structures and algorithms for efficient searching
- SQL-backed material and project databases
- Large-scale data analysis across many design scenarios
- Machine learning models to:
  - approximate structural response,
  - recommend materials or sections,
  - guide early-stage design decisions
- Computer vision approaches to extract information from images or drawings
- Cost, CO₂, and performance trade-off visualization tools

These ideas represent *intentions, not guarantees*, and may change as the project evolves.

---

## Learning and Exploration Goals

This project also serves as a learning framework for developing skills in:

- Engineering-focused software architecture
- Translating theory into maintainable code
- Data modeling and version control
- Algorithms and optimization techniques
- Responsible use of machine learning in engineering contexts
- Building explainable and trustworthy technical tools

---

## Disclaimer

This project is experimental and educational in nature.

It is *not intended for direct use in real-world structural design* without further validation, code compliance checks, and professional review.

---

## Living Document

This README is a *living document*.

As new versions are added or project goals evolve, this file will be updated to reflect:
- what has been implemented,
- what is currently planned,
- and what ideas are being explored.

The repository is intended to document not just results, but the *evolution of engineering thinking over time*.
