# Contributing to Safe Kit

Thank you for your interest in contributing to Safe Kit! We welcome contributions from the community to help make this project better.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/safe-kit.git
    cd safe-kit
    ```
3.  **Install dependencies** using Poetry:
    ```bash
    poetry install
    ```

## Development Workflow

1.  **Create a new branch** for your feature or bugfix:
    ```bash
    git checkout -b feature/my-new-feature
    ```
2.  **Make your changes**.
3.  **Run tests** to ensure everything is working:
    ```bash
    make test
    ```
4.  **Lint and format** your code:
    ```bash
    make lint
    make format
    ```

## Pull Requests

1.  Push your branch to your fork on GitHub.
2.  Open a Pull Request (PR) against the `main` branch of the `safe-kit` repository.
3.  Provide a clear description of your changes and link to any relevant issues.
4.  Ensure all CI checks pass.

## Code Style

- We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.
- We use [MyPy](https://mypy-lang.org/) for static type checking.
- Please ensure your code is fully typed.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on the [GitHub Issues](https://github.com/smallyunet/safe-kit/issues) page.
