# Multi Agent AI SEO Assistant for News Media Organizations

Multi-agent AI-powered SEO assistant tailored for journalists and news media organizations. 

## Features (more to come)

- Data driven keyword for article draft
- SEO optimized URL slugs
- Article suggestions to increasing Click-through rates (CTR)

## Getting Started

Follow these steps to set up the project on your local machine.

### 1. Prerequisites

- **Python**: Ensure you have Python 3.13 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).
- **Poetry**: This project uses Poetry for dependency management. There are multiple ways to install it. Click here for the [official installation instructions](https://python-poetry.org/docs/).

  - **Using pipx** (recommended): this requires `pipx` to be installed. Follow the [instructions here](https://pipx.pypa.io/stable/installation/) to install pipx. This is preferred as it will handle updating and uninstalling Poetry for you. Once `pipx` is installed, run:

    ```bash
    pipx install poetry
    ```
    If you want to upgrade Poetry using pipx, you can run:

    ```bash
    pipx upgrade poetry
    ```

  - **Using the official installer**: Click here for the [official installation instructions](https://python-poetry.org/docs/#installing-with-the-official-installer).

### 2. Clone the Repository

You can use VS Code or any other IDE to clone the repository. If you are using VS Code, follow these steps (assuming you have your GitHub account linked to VS Code):
1. Open VS Code empty workspace.
2. Open the Command Palette (_Windows_: Ctrl + Shift + P or _MacOS_: Cmd + Shift + P).
3. Type `Git: Clone` and select it.
4. Paste the repository https://github.com/hussainzs/SEO_AI_backend.git when prompted.
5. Choose a local directory/folder in your computer to clone the repository into.
6. Open the folder in VS Code (vs code will prompt you to do this most likely).
7. Move on to the next step [Install Dependencies](#3-install-dependencies).


--> If you prefer using the **command line**, follow these steps:
Clone this repository to your local machine:

```bash
git clone https://github.com/hussainzs/SEO_AI_backend.git
cd SEO_AI_backend
```

### 3. Install Dependencies

Run the following command and Poetry will automatically create a virtual environment and install all dependencies listed in `pyproject.toml`:

```bash
poetry install
```

### 4. Activate the Virtual Environment

If you are using VS Code, you can manually set the virtual environment by following these steps:
1. Open the Command Palette (_Windows_: Ctrl + Shift + P or _MacOS_: Cmd + Shift + P).

2. Type `Python: Select Interpreter` and select the interpreter that corresponds to the Poetry virtual environment folder.
3. You can find the path to the virtual environment by running:

```bash
poetry env info --path
```
### 5. Running the Project

will be updated in future releases.

### 6. Managing Dependencies

To add a new dependency:

```bash
poetry add package-name
```

To remove a dependency:

```bash
poetry remove package-name
```

### 7. Useful Poetry Commands

- Check your environment: `poetry env info`
- List installed packages: `poetry show`

## Contributing Guidelines

check out the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute to this project.

