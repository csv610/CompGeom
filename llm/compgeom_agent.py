"""
Computational Geometry Expert Team using Agno Framework.

This system uses a multi-agent team to provide:
1. Academic research and literature search (ArXiv, Wikipedia).
2. Algorithm exploration, complexity analysis, and open-source implementations.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from agno.agent import Agent
from agno.team import Team
from agno.models.ollama import Ollama
from agno.tools.wikipedia import WikipediaTools
from agno.tools.arxiv import ArxivTools
from agno.tools.websearch import WebSearchTools

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Global Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def create_literature_agent(model_id: str) -> Agent:
    """Agent specialized in academic and literature research."""
    return Agent(
        name="Literature Researcher",
        role="Academic researcher specialized in geometry and mathematics",
        model=Ollama(id=model_id, host=OLLAMA_HOST),
        tools=[
            ArxivTools(all=True),
            WikipediaTools(all=True),
            WebSearchTools(backend="auto"),
        ],
        instructions=[
            "Your goal is to find academic papers, formal definitions, and historical context for geometric topics.",
            "Prioritize ArXiv and Wikipedia for theoretical foundations.",
            "Identify the most influential papers, authors, or theorems related to the query.",
            "Summarize the key theoretical contributions in the field.",
        ],
    )

def create_geometry_expert_agent(model_id: str) -> Agent:
    """Agent specialized in algorithms and implementation."""
    return Agent(
        name="Geometry Expert",
        role="Expert in computational geometry algorithms and software implementation",
        model=Ollama(id=model_id, host=OLLAMA_HOST),
        tools=[
            WebSearchTools(backend="auto"),
            WikipediaTools(all=True),
        ],
        instructions=[
            "Your goal is to identify practical algorithms and their implementations.",
            "For any query, you MUST provide:",
            "1. **List of Algorithms**: Identify and describe primary algorithms.",
            "2. **Complexity Analysis**: Provide theoretical Time and Space Complexity (e.g., O(n log n)).",
            "3. **Open-Source Implementations**: Provide links or names of well-known implementations (e.g., CGAL, SciPy).",
        ],
    )

def create_compgeom_team(model_id: str = "gemma4:latest") -> Team:
    """
    Create a team of agents orchestrated by a lead agent.
    """
    lit_agent = create_literature_agent(model_id)
    geo_agent = create_geometry_expert_agent(model_id)
    
    return Team(
        name="CompGeom Team",
        members=[lit_agent, geo_agent],
        model=Ollama(id=model_id, host=OLLAMA_HOST),
        description="Computational Geometry Expert Team",
        instructions=[
            "You are the lead coordinator for a Computational Geometry research team.",
            "When a user query is received:",
            "1. Delegate to the 'Literature Researcher' to find academic background and key papers.",
            "2. Delegate to the 'Geometry Expert' to find algorithms, complexity, and code implementations.",
            "3. Synthesize their findings into a single, cohesive, and professionally formatted report.",
            "Ensure the report has clear sections: Academic Background, Algorithms & Complexity, and Implementations.",
        ],
        markdown=True,
        show_members_responses=True,
    )

def save_response(content: str, output_path: str) -> None:
    """Safely save the response to a file."""
    try:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        logger.info(f"Response saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save response to {output_path}: {e}")

def run_interactive(team: Team):
    """Run the team in an interactive loop (REPL)."""
    print("\n--- Computational Geometry Research Team ---")
    print("Type 'exit' or 'quit' to stop, or press Ctrl+C.\n")
    
    while True:
        try:
            query = input("Query: ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            
            print("\nTeam is researching and synthesizing results...")
            response = team.run(query)
            print(f"\n{response.content}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"An error occurred during interaction: {e}")

def main():
    parser = argparse.ArgumentParser(description="Computational Geometry Multi-Agent Team")
    parser.add_argument(
        "-m", "--model", type=str, default="gemma4:latest", help="Ollama model ID"
    )
    parser.add_argument(
        "-q", "--query", type=str, help="Query to ask the team"
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output file (only with -q)"
    )
    args = parser.parse_args()

    try:
        team = create_compgeom_team(args.model)
    except Exception as e:
        logger.error(f"Failed to initialize team: {e}")
        sys.exit(1)

    if args.query:
        logger.info(f"Processing query: {args.query}")
        try:
            response = team.run(args.query)
            if args.output:
                save_response(response.content, args.output)
            else:
                print(response.content)
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            sys.exit(1)
    else:
        run_interactive(team)

if __name__ == "__main__":
    main()
