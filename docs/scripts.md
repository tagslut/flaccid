# Shell Scripts Documentation

This document provides an overview of all shell scripts in the FLACCID project, their purpose, and usage instructions.

## Active Scripts

### setup.sh

**Purpose**: Sets up the development environment with Poetry or pip  
**Usage**: `./setup.sh`  
**Description**: This script installs all dependencies required for FLACCID development. It attempts to use Poetry first, with a fallback to pip if Poetry installation fails or times out. The script includes error handling, timeouts, and fallback mechanisms.

### git_commands.sh

**Purpose**: Performs git operations and updates the timestamp in README.md  
**Usage**: `./git_commands.sh`  
**Description**: This script performs git operations including adding changes, committing, and pushing to the remote repository. It also updates the timestamp in README.md, replacing any existing timestamp line rather than appending a new one.

### deploy.sh

**Purpose**: Deploys the FLACCID job to Google Cloud Run  
**Usage**: `./deploy.sh`  
**Description**: This script deploys the FLACCID application to Google Cloud Run. It configures the deployment with appropriate settings including project ID, region, job name, and service account.

## Maintenance Scripts

### fix_python_path.sh

**Purpose**: Fixes Python interpreter path in fla CLI executable  
**Usage**: `./fix_python_path.sh`  
**Description**: This script fixes the shebang line in the fla CLI executable to point to the correct Python interpreter. It's typically used when the Python path is incorrect or when moving between different environments.

### fix_pyproject_toml.sh

**Purpose**: One-time fix for pyproject.toml file  
**Usage**: `./fix_pyproject_toml.sh`  
**Description**: This script fixes issues with the pyproject.toml file by removing duplicate sections. It's a one-time fix that should only be needed if the pyproject.toml file becomes corrupted.

## Archived Scripts

These scripts are kept for reference but are no longer actively used:

### bootstrap.sh, bootstrap_flaccid.sh, init_flaccid.sh

**Purpose**: Initial project setup scripts  
**Status**: Obsolete (project is already set up)  
**Description**: These scripts were used for initial project setup and contain significant duplication. They are kept for reference but should not be used.

### install_deps.sh

**Purpose**: Installs Poetry and project dependencies  
**Status**: Obsolete (superseded by setup.sh)  
**Description**: This script was used to install Poetry and project dependencies. It has been replaced by the more comprehensive setup.sh script.

## Best Practices

When creating or modifying shell scripts in this project:

1. Add a standardized header with description, usage, and last updated date
2. Use `set -euo pipefail` for safer script execution
3. Include appropriate error handling and user feedback
4. Document the script in this file

## Script Header Template

```bash
#!/bin/bash
#
# Description: Brief description of what the script does
# Usage: ./script_name.sh [arguments]
# Last updated: YYYY-MM-DD
#
set -euo pipefail

# Script content here
```
