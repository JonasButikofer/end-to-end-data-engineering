# Project Notes for Claude

## Environment

- **OS**: Windows 11
- **Shell**: PowerShell — always give terminal commands in PowerShell syntax, not bash/Unix syntax.
  - Use `$env:VAR` not `export VAR=`
  - Use `;` not `&&` for chaining commands (or use separate commands)
  - Use backslashes for paths only when required; forward slashes work in most PowerShell contexts
  - Do NOT use `set -e`, `#!/usr/bin/env bash`, or other bash-isms in instructions to the user
