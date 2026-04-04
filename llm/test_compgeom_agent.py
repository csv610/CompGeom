import pytest
from unittest.mock import MagicMock, patch
from compgeom_agent import create_compgeom_team, main
import argparse
from agno.agent import Agent
from agno.team import Team

def test_create_team():
    """Verify that the team is created with correct members and instructions."""
    team = create_compgeom_team(model_id="test-model")
    
    assert isinstance(team, Team)
    assert team.model.id == "test-model"
    
    # Check if members are present
    member_names = [m.name for m in team.members]
    assert "Literature Researcher" in member_names
    assert "Geometry Expert" in member_names
    assert "Application Specialist" in member_names
    
    # Check for synthesized section headers in instructions
    instructions_text = " ".join(team.instructions)
    assert "Academic Background" in instructions_text
    assert "Algorithms & Complexity" in instructions_text
    assert "Real-World & Novel Applications" in instructions_text

@patch("compgeom_agent.create_compgeom_team")
@patch("argparse.ArgumentParser.parse_args")
def test_main_cli_execution(mock_parse_args, mock_create_team):
    """Verify the main CLI entry point handles arguments and calls the team."""
    # Mock CLI arguments
    mock_parse_args.return_value = argparse.Namespace(
        model="test-model",
        query="Convex Hull",
        output=None
    )
    
    # Mock team instance and its run method
    mock_team = MagicMock()
    mock_team.run.return_value = MagicMock(content="Mocked response")
    mock_create_team.return_value = mock_team
    
    # Run main
    with patch("builtins.print") as mock_print:
        main()
        
    # Verify calls
    mock_create_team.assert_called_once_with("test-model")
    mock_team.run.assert_called_once_with("Convex Hull")
    mock_print.assert_any_call("Mocked response")

@patch("compgeom_agent.save_response")
@patch("compgeom_agent.create_compgeom_team")
@patch("argparse.ArgumentParser.parse_args")
def test_main_cli_output_file(mock_parse_args, mock_create_team, mock_save_response):
    """Verify the output file argument is handled correctly."""
    mock_parse_args.return_value = argparse.Namespace(
        model="test-model",
        query="Convex Hull",
        output="test_output.txt"
    )
    
    mock_team = MagicMock()
    mock_team.run.return_value = MagicMock(content="Mocked response")
    mock_create_team.return_value = mock_team
    
    main()
    
    mock_save_response.assert_called_once_with("Mocked response", "test_output.txt")
