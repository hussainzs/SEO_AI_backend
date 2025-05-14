# Multi Agent AI SEO Assistant for News Media Organizations

(⚠️🔨In-progress) Multi-agent AI-powered SEO assistant tailored for journalists and news media organizations. 

## Features (more to come)

- Data driven keyword for article draft
- SEO optimized URL slugs
- Article suggestions to increasing Click-through rates (CTR)

## Getting Started

Follow these steps to set up the project on your local machine.

### 1. Prerequisites

- **Python**: Ensure you have Python 3.13 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).
- **Poetry**: This project uses Poetry for dependency management. There are multiple ways to install it. Click here for the [official installation instructions](https://python-poetry.org/docs/).

  - **Using pipx** (recommended): this requires `pipx` to be installed. Follow the [instructions here](https://pipx.pypa.io/stable/installation/) to install pipx. This is preferred as it will handle updating and uninstalling Poetry for you. Once `pipx` is installed, **run**:

    ```bash
    pipx install poetry
    ```
    In the future, If you want to upgrade Poetry using pipx, you can run:

    ```bash
    pipx upgrade poetry
    ```

---

#### **Observability & Tracing**
  Opik by Comet ([Learn more](https://www.comet.com/site/products/opik/))  
  - **Cloud-hosted, free tier:** No credit card required.  
  - **Limits:** 25,000 traces/month, 60-day data retention.  
  - **Setup:**  
    - Sign up for a free account on [Comet Opik](https://www.comet.com/site/products/opik/).
    - Obtain your Opik API credentials.
    - Add the following variables to your `.env` file (see `.env.example` for details):  
      - `OPIK_API_KEY`
      - `OPIK_WORKSPACE`
      - `OPIK_PROJECT_NAME`
    - Note the `OPIK_PROJECT_NAME` is the name of the project you want to create in Opik. If you don't create a project it will go into Default project.
    - Also note that `OPIK_WORKSPACE` can be found in the quickstart guide for langgraph in Opik once you sign up for the free account.
---

#### **Web Search Providers**

- **Tavily** ([tavily.com](https://tavily.com)):  
  - **Free tier:** 1,000 searches/month, no credit card required.  
  - **Setup:**  
    - Sign up and create an API key on [Tavily](https://tavily.com).
    - Add your API key to the `.env` file as `TAVILY_API_KEY` (see `.env.example`).
- **Exa** ([exa.ai](https://exa.ai/)):  
  - *Coming soon*

---

#### **LLMs (Large Language Models)**

- **Google Generative AI**  
  - **Get a free API key:** [Google Gemini API](https://ai.google.dev/gemini-api/docs/api-key)  
  - **Pricing:** [See pricing](https://ai.google.dev/gemini-api/docs/pricing)  
  - **Model names:** [Model variations](https://ai.google.dev/gemini-api/docs/models#model-variations)  
  - **Setup:**  
    - Obtain your API key and add it to `.env` as `GEMINI_API_KEY` (see `.env.example`).
- **OpenAI:**  
  - *Coming soon*
- **Groq:**  
  - *Coming soon*

---

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

To be updated

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

