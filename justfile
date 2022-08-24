alias b := build
alias bd := build

# Sets up the pre-commit hooks
configure: && build
    pre-commit install
    pre-commit run --all-files

# Builds the project
build:
    cargo build

# Runs the project
run *ARGS:
    cargo run {{ ARGS }}
