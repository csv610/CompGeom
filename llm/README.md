# Computational Geometry Expert Team

A multi-agent research team powered by the [Agno](https://agno.com) framework (formerly Phidata) and [Ollama](https://ollama.com). This tool provides deep insights into computational geometry topics by coordinating specialized agents for academic literature and algorithmic analysis.

## 🚀 Features

- **Multi-Agent Orchestration**: A lead coordinator delegates tasks to specialized researchers.
- **Literature Specialist**: Searches ArXiv and Wikipedia for foundational papers, formal definitions, and theoretical background.
- **Algorithm Specialist**: Analyzes computational complexity and identifies robust open-source implementations (CGAL, SciPy, QHull, etc.).
- **Interactive Mode**: A REPL-style interface for ongoing geometric exploration.
- **Local-First**: Runs locally using Ollama for privacy and control.

## 🛠️ Prerequisites

- **Python 3.12+**
- **Ollama**: [Download and install Ollama](https://ollama.com/).
- **Model**: The default model is `gemma4:latest` (can be changed via CLI).
  ```bash
  ollama pull gemma4:latest
  ```

## 📦 Installation

1. Install the required dependencies:
   ```bash
   pip install agno wikipedia arxiv duckduckgo-search httpx pytest
   ```

2. (Optional) Set your Ollama host if it's not the default:
   ```bash
   export OLLAMA_HOST="http://localhost:11434"
   ```

## 📖 Usage

### Single Query
Run a quick research report on a specific topic:
```bash
python3 compgeom_agent.py -q "Convex Hull in 3D"
```

### Save to File
Save the synthesized report to a markdown file:
```bash
python3 compgeom_agent.py -q "Delaunay Triangulation" -o delaunay_report.md
```

### Interactive Mode
Start a conversational research session:
```bash
python3 compgeom_agent.py
```

### Custom Model
Specify a different Ollama model:
```bash
python3 compgeom_agent.py -m "llama3:latest" -q "Polygon Triangulation"
```

## 🧠 Team Architecture

The system utilizes a `Team` of specialized agents:

1.  **Literature Researcher**: Uses ArXiv and Wikipedia tools to find theoretical foundations and key academic citations.
2.  **Geometry Expert**: Uses Web Search and Wikipedia to identify practical algorithms, complexity (Big O), and high-quality code implementations.
3.  **Lead Coordinator**: Receives the query, plans the delegation, and synthesizes the final report into a cohesive, structured document.

## 🧪 Testing

The codebase includes a suite of unit tests using `pytest` and `unittest.mock`. To run the tests:

```bash
pytest test_compgeom_agent.py
```

## 📝 License

Apache License 2.0 (See `compgeom_agent.py` header).
