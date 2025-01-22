# Multi-Physics Simulation Topology Schema

## Overview

This JSON schema provides a flexible and robust configuration mechanism for defining multi-physics simulation topologies, specifically designed for complex coupling scenarios in scientific computing and engineering simulations.

## Key Features

### 1. Flexible Configuration Structures
The schema supports two primary configuration structures:
- Modern `coupling-scheme` based configuration
- Legacy `simulation` based configuration

This ensures backward compatibility and allows for evolving project requirements.

### 2. Comprehensive Simulation Parameters

#### Simulation Configuration
- `steady-state`: Boolean to indicate steady-state simulation
- `timesteps`: Number of time steps
- `time-window-size`: Configurable time window with scientific notation support
- `accuracy`: Simulation accuracy levels (low/medium/high)
- `sync-mode`: Synchronization control
- `mode`: Simulation mode (fundamental/advanced)

#### Coupling Scheme Configuration
- Advanced coupling parameters
- Maximum time and relative accuracy settings
- Iteration and extrapolation controls
- Explicit and implicit coupling support

### 3. Participant Configuration

Each participant can be extensively configured:
- Solver name and type
- Interface specifications
- Solver domain (fluid/structure/heat)
- Dimensionality
- Solver nature (stationary/transient)
- Boundary code specifications

### 4. Detailed Coupling Mechanisms

#### Coupling Types
Supports multiple coupling types:
- Fluid-Structure Interaction (FSI)
- Conjugate Heat Transfer (CHT)
- Fluid-to-Structure (F2S)

#### Exchange Mechanisms
Configurable data exchanges between participants:
- Source and target participants
- Interface patches
- Exchanged data types (Force, Displacement, Temperature, etc.)
- Quantity mapping (conservative/consistent)
- Read and write quantity specifications

## Validation Features

- Strict type checking
- Range and enumeration constraints
- Scientific notation support
- Flexible structure validation
- Prevents unexpected configurations

## Example Use Cases

1. **Fluid-Structure Interaction**
   - Simulate fluid flow around a deformable structure
   - Exchange force and displacement data
   - Control coupling precision

2. **Conjugate Heat Transfer**
   - Model heat transfer between fluid and solid domains
   - Configure temperature and heat transfer exchanges
   - Define synchronization and accuracy parameters

## Schema Validation Rules

- Supports both modern and legacy YAML structures
- Requires either:
  - `coupling-scheme`, `participants`, `exchanges`
  - `simulation`, `participants`, `couplings`
- No additional properties allowed
- Comprehensive error prevention

## Recommended Workflow

1. Define participants
2. Configure simulation parameters
3. Specify coupling mechanisms
4. Detail data exchanges
5. Validate against schema

## Compatibility

- Supports complex multi-physics simulations
- Adaptable to various scientific computing frameworks
- Designed for preCICE coupling framework

## Best Practices

- Use scientific notation for precise time and accuracy settings
- Clearly define solver domains
- Specify mapping types for data exchanges
- Leverage synchronization and mode settings

## Limitations

- Maximum of 10 participants
- Maximum of 10 couplings/exchanges
- Predefined data types and solver domains

## Future Extensions

- Support for more solver domains
- Additional data exchange types
- Enhanced validation rules

## Contributing

Contributions to expand and improve the schema are welcome. Please follow the project's contribution guidelines.