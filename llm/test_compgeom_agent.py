import pytest
from unittest.mock import MagicMock, patch
from compgeom_agent import create_compgeom_agent, main
import argparse
from agno.agent import Agent

def test_create_agent():
    """Verify that the agent is created with the correct instructions and tools."""
    agent = create_compgeom_agent(model_id="test-model")
    
    assert isinstance(agent, Agent)
    assert agent.model.id == "test-model"
    
    # Check if structured instructions are present
    instructions_text = " ".join(agent.instructions)
    assert "List of Algorithms" in instructions_text
    assert "Complexity Analysis" in instructions_text
    assert "Open-Source Implementations" in instructions_text
    
    # Verify tools are attached
    tool_names = [tool.__class__.__name__ for tool in agent.tools]
    assert "WikipediaTools" in tool_names
    assert "ArxivTools" in tool_names
    assert "WebSearchTools" in tool_names

@patch("compgeom_agent.create_compgeom_agent")
@patch("argparse.ArgumentParser.parse_args")
def test_main_cli_execution(mock_parse_args, mock_create_agent):
    """Verify the main CLI entry point handles arguments and calls the agent."""
    # Mock CLI arguments
    mock_parse_args.return_value = argparse.Namespace(
        model="test-model",
        query="Convex Hull",
        output=None
    )
    
    # Mock agent instance and its run method
    mock_agent = MagicMock()
    mock_agent.run.return_value = MagicMock(content="Mocked response")
    mock_create_agent.return_value = mock_agent
    
    # Run main
    with patch("builtins.print") as mock_print:
        main()
        
    # Verify calls
    mock_create_agent.assert_called_once_with("test-model")
    mock_agent.run.assert_called_once_with("Convex Hull")
    mock_print.assert_any_call("Mocked response")

@patch("compgeom_agent.save_response")
@patch("compgeom_agent.create_compgeom_agent")
@patch("argparse.ArgumentParser.parse_args")
def test_main_cli_output_file(mock_parse_args, mock_create_agent, mock_save_response):
    """Verify the output file argument is handled correctly."""
    mock_parse_args.return_value = argparse.Namespace(
        model="test-model",
        query="Convex Hull",
        output="test_output.txt"
    )
    
    mock_agent = MagicMock()
    mock_agent.run.return_value = MagicMock(content="Mocked response")
    mock_create_agent.return_value = mock_agent
    
    main()
    
    mock_save_response.assert_called_once_with("Mocked response", "test_output.txt")
