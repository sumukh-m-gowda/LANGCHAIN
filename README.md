# 🦜🔗 LangChain Learning Journey

A hands-on, module-by-module deep dive into **LangChain** — from the fundamentals (models, prompts, output parsing) all the way up to **RAG pipelines, tools, and fully functional AI agents**.

This repo is structured as a progressive curriculum. Each folder builds on the concepts from the one before it, so you can follow along in order or jump straight to the topic you need.

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Learning Path](#-learning-path)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Tech Stack](#-tech-stack)
- [Project Highlights](#-project-highlights)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

[LangChain](https://www.langchain.com/) is a framework for building applications powered by large language models (LLMs). This repository documents a structured learning path through its core building blocks — chat models, prompt templates, runnables, chains, document loaders, vector stores, retrievers, tools, and agents — culminating in complete mini-projects that tie everything together.

Whether you're learning LangChain from scratch or looking for a quick reference implementation of a specific concept, each folder is self-contained and focused on one topic.

---

## 🗺️ Learning Path

| # | Module | What You'll Learn |
|---|--------|--------------------|
| 1 | [`1_LANGCHAIN_MODELS`](./1_LANGCHAIN_MODELS) | Initializing and interacting with chat/LLM models |
| 2 | [`2_LANGCHAIN_PROMPTS`](./2_LANGCHAIN_PROMPTS) | Prompt templates and working with runnables |
| 3 | [`3_LANGCHAIN_STRUCTURED_OUTPUT`](./3_LANGCHAIN_STRUCTURED_OUTPUT) | Getting structured, schema-validated responses from LLMs |
| 4 | [`4_LANGCHAIN_OUTPUT_PARSERS`](./4_LANGCHAIN_OUTPUT_PARSERS) | Parsing raw LLM output into usable formats |
| 5 | [`5_mini_project`](./5_mini_project) | Applying models, prompts & chains in a small project |
| 6 | [`6_LANGCHAIN_CHAINS`](./6_LANGCHAIN_CHAINS) | Building sequential and composable chains |
| 7 | [`7_LANGCHAIN_RUNNABLES`](./7_LANGCHAIN_RUNNABLES) | The Runnable interface & LCEL (LangChain Expression Language) |
| 8 | [`8_LANGCHAIN_DOCUMENT_LOADER`](./8_LANGCHAIN_DOCUMENT_LOADER) | Loading documents from various sources |
| 9 | [`9_LANGCHAIN_TEXT_SPLITTER`](./9_LANGCHAIN_TEXT_SPLITTER) | Chunking text for retrieval and embeddings |
| 10 | [`A10_LANGCHAIN_VECTOR_STORES`](./A10_LANGCHAIN_VECTOR_STORES) | Storing and querying embeddings |
| 11 | [`A11_LANGCHAIN_RETRIEVERS`](./A11_LANGCHAIN_RETRIEVERS) | Retrieval strategies over vector stores |
| 12 | [`A12__RAG__`](./A12__RAG__) | Building a full Retrieval-Augmented Generation pipeline |
| 13 | [`A13__LANGCHAIN_TOOLS`](./A13__LANGCHAIN_TOOLS) | Defining and using tools with LLMs |
| 14 | [`A14_REVISION`](./A14_REVISION) | Consolidated revision of core concepts |
| 15 | [`A15_COMPLETE_AGENT`](./A15_COMPLETE_AGENT) | Assembling a complete, tool-using agent |
| — | [`MINI_AGENT_FINAL`](./MINI_AGENT_FINAL) | Final capstone mini-agent project |
| — | [`langchain.ipynb`](./langchain.ipynb) | Exploratory notebook covering core concepts |

> 💡 **Tip:** Folders are numbered in the intended learning order — start at `1_LANGCHAIN_MODELS` and work your way down to `A15_COMPLETE_AGENT`.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sumukh-m-gowda/LANGCHAIN.git
cd LANGCHAIN
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If a `requirements.txt` isn't present yet, install the core packages directly:
> ```bash
> pip install langchain langchain-openai langchain-community python-dotenv jupyter
> ```

### 4. Run a module

Each folder can generally be run independently:

```bash
cd 1_LANGCHAIN_MODELS
python main.py
```

Or explore interactively via the notebook:

```bash
jupyter notebook langchain.ipynb
```

---

## 🔑 Environment Variables

Most modules rely on API keys for LLM providers. Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
# Add other provider keys as needed, e.g.
# GOOGLE_API_KEY=your_google_api_key_here
# HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
```

> ⚠️ Never commit your `.env` file — it's already excluded via `.gitignore`.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Core Framework:** [LangChain](https://python.langchain.com/)
- **LLM Providers:** OpenAI (and/or other supported providers)
- **Vector Stores:** FAISS / Chroma *(as used in the vector store & RAG modules)*
- **Environment Management:** `python-dotenv`
- **Notebooks:** Jupyter

---

## ✨ Project Highlights

- **`A12__RAG__`** — A complete Retrieval-Augmented Generation pipeline: load → split → embed → retrieve → generate.
- **`A15_COMPLETE_AGENT`** — A fully wired agent combining models, tools, and reasoning.
- **`MINI_AGENT_FINAL`** — The capstone project demonstrating everything learned in a compact, functional agent.

---

## 🤝 Contributing

This is primarily a personal learning repository, but suggestions, corrections, and improvements are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b improvement/my-fix`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project currently has no explicit license. If you intend for others to reuse this code, consider adding an [MIT License](https://choosealicense.com/licenses/mit/) or similar.

---

<p align="center">Built with ❤️ while learning LangChain, one module at a time.</p>
