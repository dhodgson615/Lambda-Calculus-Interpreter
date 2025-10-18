#!/usr/bin/env python3
"""
Tests for the web interface of the Lambda Calculus Interpreter.
"""

import json
import sys
import os

# Add src directory to the path so we can import webapp
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from webapp import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that the main page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Calculus Interpreter' in response.data  # Check for part without lambda
    assert b'Interactive Lambda Calculus Evaluation' in response.data

def test_examples_endpoint(client):
    """Test the examples endpoint returns valid JSON."""
    response = client.get('/examples')
    assert response.status_code == 200
    
    examples = json.loads(response.data)
    assert isinstance(examples, list)
    assert len(examples) > 0
    
    # Check first example has required fields
    example = examples[0]
    assert 'name' in example
    assert 'expression' in example
    assert 'description' in example

def test_evaluate_simple_expression(client):
    """Test evaluation of a simple lambda expression."""
    response = client.post('/evaluate', 
                          json={'expression': '(λx.x) y'},
                          content_type='application/json')
    
    assert response.status_code == 200
    
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['input'] == '(λx.x) y'
    assert result['final_expression'] == 'y'
    assert len(result['steps']) >= 2  # Initial + at least 1 step
    assert result['total_steps'] >= 1

def test_evaluate_arithmetic(client):
    """Test evaluation of arithmetic expression."""
    response = client.post('/evaluate', 
                          json={'expression': '+ 2 3'},
                          content_type='application/json')
    
    assert response.status_code == 200
    
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['input'] == '+ 2 3'
    assert result['abstracted'] == '5'  # Should be abstracted to the number 5
    assert result['total_steps'] > 0

def test_evaluate_parse_error(client):
    """Test that parse errors are handled gracefully."""
    response = client.post('/evaluate', 
                          json={'expression': 'λx'},  # Invalid syntax
                          content_type='application/json')
    
    assert response.status_code == 400
    
    result = json.loads(response.data)
    assert 'error' in result
    assert 'Parse error' in result['error']

def test_evaluate_empty_expression(client):
    """Test that empty expressions are handled."""
    response = client.post('/evaluate', 
                          json={'expression': ''},
                          content_type='application/json')
    
    assert response.status_code == 400
    
    result = json.loads(response.data)
    assert 'error' in result
    assert 'Please enter a lambda expression' in result['error']

def test_evaluate_missing_expression(client):
    """Test that missing expression field is handled."""
    response = client.post('/evaluate', 
                          json={},
                          content_type='application/json')
    
    assert response.status_code == 400
    
    result = json.loads(response.data)
    assert 'error' in result

if __name__ == '__main__':
    pytest.main([__file__, '-v'])