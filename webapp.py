#!/usr/bin/env python3
"""
Flask web application for the Lambda Calculus Interpreter.
Provides a web interface for easier interaction with the interpreter.
"""

import sys
import os
from io import StringIO
from contextlib import redirect_stdout

# Add src directory to the path so we can import the interpreter modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, render_template, request, jsonify
from _config import DELTA_ABSTRACT, SHOW_STEP_TYPE
from _defs import DEFS
from _expressions import Expression
from _parser import Parser
from _printer import format_expr, highlight_diff
from _reduce import reduce_once
from main import abstract_numerals

app = Flask(__name__)

def normalize_for_web(expression: Expression) -> dict:
    """
    Normalize the expression to its normal form and return steps as a dict.
    Modified version of normalize() that captures output instead of printing.
    """
    steps = []
    step = 0
    previous_render = format_expr(expression)
    steps.append({
        'step': step,
        'expression': previous_render,
        'type': 'initial'
    })
    
    while True:
        result = reduce_once(expression, DEFS)
        if not result:
            break
            
        expression = result[0]
        stype = result[1]
        step += 1
        rend = format_expr(expression)
        # For web display, we won't use highlight_diff as it includes ANSI codes
        
        step_info = {
            'step': step,
            'expression': rend,
            'type': stype
        }
        steps.append(step_info)
        previous_render = rend
    
    # Get final abstracted form if enabled
    final_abstracted = None
    if DELTA_ABSTRACT:
        abstracted = abstract_numerals(expression)
        final_abstracted = format_expr(abstracted)
    
    return {
        'steps': steps,
        'final_expression': previous_render,
        'abstracted': final_abstracted,
        'total_steps': step
    }

@app.route('/')
def index():
    """Main page with the lambda calculus input form."""
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Evaluate a lambda calculus expression and return the steps."""
    try:
        user_input = request.json.get('expression', '').strip()
        if not user_input:
            return jsonify({'error': 'Please enter a lambda expression'}), 400
        
        # Parse the expression
        try:
            tree = Parser(user_input).parse()
        except SyntaxError as e:
            return jsonify({'error': f'Parse error: {str(e)}'}), 400
        
        # Normalize and get steps
        result = normalize_for_web(tree)
        
        return jsonify({
            'success': True,
            'input': user_input,
            **result
        })
        
    except Exception as e:
        return jsonify({'error': f'Evaluation error: {str(e)}'}), 500

@app.route('/examples')
def examples():
    """Return common lambda calculus examples."""
    examples = [
        {
            'name': 'Identity Function',
            'expression': '(λx.x) (λy.y)',
            'description': 'Applies the identity function to another identity function'
        },
        {
            'name': 'Simple Arithmetic',
            'expression': '+ 2 3',
            'description': 'Addition of Church numerals 2 and 3'
        },
        {
            'name': 'Multiplication',
            'expression': '* 2 3',
            'description': 'Multiplication of Church numerals 2 and 3'
        },
        {
            'name': 'Boolean True',
            'expression': 'true 5 7',
            'description': 'Boolean true chooses the first argument'
        },
        {
            'name': 'Boolean False',
            'expression': 'false 5 7',
            'description': 'Boolean false chooses the second argument'
        },
        {
            'name': 'Factorial (small)',
            'expression': 'fact 3',
            'description': 'Factorial of 3 using recursive definition'
        }
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)