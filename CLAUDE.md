# Project Context

This is a forked repository from the official IsaacLab for robotics research and development.

## Project Goals
- Leverage IsaacLab's existing development environment and tutorials with minimal modifications
- Research and develop reinforcement learning and imitation learning for custom robot systems
- Use Docker for local development and prototyping
- Deploy to SLURM cluster for large-scale training after local validation

## Development Philosophy
- **Minimal Code Generation**: Only create files and code that are absolutely necessary
- **Follow Original Design**: Use the framework as intended by the original developers to minimize errors
- **No Temporary Solutions**: Avoid quick fixes or workarounds; implement proper solutions
- **Code Reuse Over Duplication**: When interfaces change, modify existing code rather than creating parallel implementations. Fix root causes, not symptoms
- **Single Source of Truth**: Avoid creating multiple versions of similar functionality. Improve and adapt existing code instead
- **Language Preference**: All responses, comments, and documentation (except CLAUDE.md) should be in Korean

## Workflow
1. Local Development: Use Docker environment for tutorial exploration and initial testing
2. Prototype Validation: Verify feasibility of learning algorithms with custom robot configurations
3. Cluster Deployment: Transfer Docker-developed code to SLURM cluster for extended training runs

## Branch Strategy
- `main`: Synced with upstream repository
- `devel`: Primary development branch for all custom work
- Feature branches: Created as needed for specific experiments or robot implementations

## Important Notes
- Preserve original repository structure and conventions
- Docker is the primary development environment for consistency
- Cluster deployment uses SLURM (reference: https://isaac-sim.github.io/IsaacLab/main/source/deployment/cluster.html)
- Focus on research objectives rather than repository contribution