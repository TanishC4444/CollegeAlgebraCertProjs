from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import json
import sympy as sp
from sympy import symbols, solve, sympify, lambdify, diff, integrate
import math
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Store functions in memory (in production, use a database)
functions_store = {}
results_log = []

def safe_eval(expr_str, x_val):
    """Safely evaluate mathematical expressions"""
    try:
        x = symbols('x')
        # Replace common mathematical expressions
        expr_str = expr_str.replace('^', '**').replace('ln', 'log')
        expr = sympify(expr_str)
        func = lambdify(x, expr, 'numpy')
        result = func(x_val)
        return result if np.isfinite(result) else np.nan
    except Exception as e:
        return np.nan

def generate_plot_data(functions, x_min=-10, x_max=10, num_points=1000):
    """Generate data for plotting functions"""
    x_vals = np.linspace(x_min, x_max, num_points)
    plot_data = {'x': x_vals.tolist()}
    
    for func_id, func_info in functions.items():
        try:
            y_vals = np.array([safe_eval(func_info['expression'], x) for x in x_vals])
            # Filter out invalid values
            y_vals = np.where(np.isfinite(y_vals), y_vals, None)
            plot_data[func_id] = y_vals.tolist()
        except Exception as e:
            plot_data[func_id] = [None] * len(x_vals)
    
    return plot_data

def create_matplotlib_plot(functions, x_min=-10, x_max=10, y_min=-10, y_max=10):
    """Create a matplotlib plot and return as base64 image"""
    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#DDA0DD', '#98D8C8']
    
    x_vals = np.linspace(x_min, x_max, 1000)
    
    for i, (func_id, func_info) in enumerate(functions.items()):
        try:
            y_vals = np.array([safe_eval(func_info['expression'], x) for x in x_vals])
            valid_mask = np.isfinite(y_vals)
            
            if np.any(valid_mask):
                ax.plot(x_vals[valid_mask], y_vals[valid_mask], 
                       color=colors[i % len(colors)], 
                       linewidth=3, 
                       label=func_info['name'],
                       alpha=0.8)
        except Exception as e:
            continue
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linewidth=0.8, alpha=0.7)
    ax.axvline(x=0, color='black', linewidth=0.8, alpha=0.7)
    ax.set_xlabel('x', fontsize=12, fontweight='bold')
    ax.set_ylabel('y', fontsize=12, fontweight='bold')
    ax.set_title('Function Graph', fontsize=16, fontweight='bold', pad=20)
    
    if functions:
        ax.legend(loc='best', framealpha=0.9)
    
    plt.tight_layout()
    
    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return img_str

def solve_quadratic(a, b, c):
    """Solve quadratic equation"""
    if a == 0:
        return {"error": "Coefficient 'a' cannot be zero"}
    
    discriminant = b**2 - 4*a*c
    vertex_x = -b / (2*a)
    vertex_y = a * vertex_x**2 + b * vertex_x + c
    
    results = {
        "discriminant": discriminant,
        "vertex": [vertex_x, vertex_y],
        "axis_of_symmetry": vertex_x,
        "equation": f"{a}x² + {b}x + {c} = 0"
    }
    
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        results["roots"] = [root1, root2]
        results["root_type"] = "Two real roots"
    elif discriminant == 0:
        root = -b / (2*a)
        results["roots"] = [root]
        results["root_type"] = "One repeated root"
    else:
        real_part = -b / (2*a)
        imag_part = math.sqrt(-discriminant) / (2*a)
        results["roots"] = [f"{real_part:.4f} + {imag_part:.4f}i", f"{real_part:.4f} - {imag_part:.4f}i"]
        results["root_type"] = "Two complex roots"
    
    return results

def analyze_function(expression, point):
    """Analyze function at a given point"""
    try:
        x = symbols('x')
        expr = sympify(expression.replace('^', '**'))
        
        # Function value
        value = float(expr.subs(x, point))
        
        # First derivative
        derivative = diff(expr, x)
        derivative_value = float(derivative.subs(x, point))
        
        # Second derivative
        second_derivative = diff(derivative, x)
        second_derivative_value = float(second_derivative.subs(x, point))
        
        analysis = {
            "point": point,
            "value": value,
            "derivative": derivative_value,
            "second_derivative": second_derivative_value,
            "derivative_expr": str(derivative),
            "critical_point": abs(derivative_value) < 1e-10
        }
        
        if analysis["critical_point"]:
            if second_derivative_value > 0:
                analysis["critical_type"] = "Local minimum"
            elif second_derivative_value < 0:
                analysis["critical_type"] = "Local maximum"
            else:
                analysis["critical_type"] = "Inflection point"
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_function', methods=['POST'])
def add_function():
    try:
        data = request.get_json()
        expression = data.get('expression', '').strip()
        
        if not expression:
            return jsonify({"error": "Please enter a function"})
        
        # Test the function
        test_val = safe_eval(expression, 1.0)
        if np.isnan(test_val):
            return jsonify({"error": "Invalid function expression"})
        
        # Generate unique ID
        func_id = f"f{len(functions_store) + 1}"
        functions_store[func_id] = {
            "name": f"f{len(functions_store) + 1}(x) = {expression}",
            "expression": expression,
            "id": func_id
        }
        
        # Log the action
        results_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": f"Added function: {expression}",
            "type": "success"
        })
        
        return jsonify({
            "success": True,
            "function": functions_store[func_id],
            "functions": list(functions_store.values())
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/remove_function', methods=['POST'])
def remove_function():
    try:
        data = request.get_json()
        func_id = data.get('func_id')
        
        if func_id in functions_store:
            removed_func = functions_store.pop(func_id)
            results_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": f"Removed function: {removed_func['expression']}",
                "type": "info"
            })
            
        return jsonify({
            "success": True,
            "functions": list(functions_store.values())
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/clear_functions', methods=['POST'])
def clear_functions():
    global functions_store
    functions_store = {}
    results_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": "Cleared all functions",
        "type": "info"
    })
    return jsonify({"success": True})

@app.route('/api/plot_data', methods=['POST'])
def get_plot_data():
    try:
        data = request.get_json()
        x_min = data.get('x_min', -10)
        x_max = data.get('x_max', 10)
        y_min = data.get('y_min', -10)
        y_max = data.get('y_max', 10)
        
        plot_data = generate_plot_data(functions_store, x_min, x_max)
        
        return jsonify({
            "success": True,
            "data": plot_data,
            "functions": list(functions_store.values())
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/matplotlib_plot', methods=['POST'])
def get_matplotlib_plot():
    try:
        data = request.get_json()
        x_min = data.get('x_min', -10)
        x_max = data.get('x_max', 10)
        y_min = data.get('y_min', -10)
        y_max = data.get('y_max', 10)
        
        img_str = create_matplotlib_plot(functions_store, x_min, x_max, y_min, y_max)
        
        return jsonify({
            "success": True,
            "image": img_str
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/solve_quadratic', methods=['POST'])
def solve_quad():
    try:
        data = request.get_json()
        a = float(data.get('a', 1))
        b = float(data.get('b', 0))
        c = float(data.get('c', 0))
        
        results = solve_quadratic(a, b, c)
        
        if "error" not in results:
            # Add quadratic function
            expression = f"{a}*x**2 + {b}*x + {c}"
            func_id = "quadratic"
            functions_store[func_id] = {
                "name": f"Quadratic: {results['equation']}",
                "expression": expression,
                "id": func_id
            }
            
            results_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": f"Solved quadratic: {results['equation']}",
                "type": "success"
            })
        
        return jsonify({
            "success": True,
            "results": results,
            "functions": list(functions_store.values())
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/analyze_function', methods=['POST'])
def analyze_func():
    try:
        data = request.get_json()
        func_id = data.get('func_id')
        point = float(data.get('point', 0))
        
        if func_id not in functions_store:
            return jsonify({"error": "Function not found"})
        
        expression = functions_store[func_id]['expression']
        analysis = analyze_function(expression, point)
        
        if "error" not in analysis:
            results_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": f"Analyzed function at x={point}",
                "type": "info"
            })
        
        return jsonify({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/generate_table', methods=['POST'])
def generate_table():
    try:
        data = request.get_json()
        x_min = data.get('x_min', -10)
        x_max = data.get('x_max', 10)
        points = data.get('points', 21)
        
        if not functions_store:
            return jsonify({"error": "No functions to create table for"})
        
        x_vals = np.linspace(x_min, x_max, points)
        table_data = {"x": x_vals.tolist()}
        
        for func_id, func_info in functions_store.items():
            y_vals = [safe_eval(func_info['expression'], x) for x in x_vals]
            table_data[func_info['name']] = [round(y, 4) if np.isfinite(y) else "undefined" for y in y_vals]
        
        return jsonify({
            "success": True,
            "table_data": table_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/export_csv', methods=['POST'])
def export_csv():
    try:
        data = request.get_json()
        table_data = data.get('table_data')
        
        df = pd.DataFrame(table_data)
        csv_string = df.to_csv(index=False)
        
        return jsonify({
            "success": True,
            "csv_data": csv_string
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/results_log')
def get_results_log():
    return jsonify({
        "success": True,
        "log": results_log[-50:]  # Last 50 entries
    })

@app.route('/api/clear_log', methods=['POST'])
def clear_log():
    global results_log
    results_log = []
    return jsonify({"success": True})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Graphing Calculator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.11.0/math.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            overflow: hidden;
            display: grid;
            grid-template-columns: 400px 1fr;
            min-height: 80vh;
        }

        .control-panel {
            background: linear-gradient(180deg, #f8f9ff 0%, #e8ecff 100%);
            padding: 25px;
            border-right: 1px solid rgba(102, 126, 234, 0.2);
            overflow-y: auto;
        }

        .plot-area {
            padding: 25px;
            background: white;
            display: flex;
            flex-direction: column;
        }

        .section {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
        }

        .section:hover {
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }

        .section h3 {
            color: #4c6ef5;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: 600;
        }

        .input-group {
            margin-bottom: 15px;
        }

        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #555;
        }

        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e7ff;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: #f8f9ff;
        }

        input[type="text"]:focus, input[type="number"]:focus, select:focus {
            outline: none;
            border-color: #4c6ef5;
            background: white;
            box-shadow: 0 0 0 3px rgba(76, 110, 245, 0.1);
        }

        .btn {
            background: linear-gradient(135deg, #4c6ef5 0%, #6c5ce7 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            margin: 5px 5px 5px 0;
            box-shadow: 0 4px 15px rgba(76, 110, 245, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(76, 110, 245, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        }

        .btn-danger {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        }

        .btn-success {
            background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
        }

        .functions-list {
            background: #f8f9ff;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            max-height: 150px;
            overflow-y: auto;
        }

        .function-item {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            border-left: 4px solid;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }

        .function-item:hover {
            transform: translateX(5px);
        }

        .function-item.color-0 { border-left-color: #FF6B6B; }
        .function-item.color-1 { border-left-color: #4ECDC4; }
        .function-item.color-2 { border-left-color: #45B7D1; }
        .function-item.color-3 { border-left-color: #96CEB4; }
        .function-item.color-4 { border-left-color: #FECA57; }

        .range-inputs {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 10px;
            align-items: center;
            margin: 10px 0;
        }

        .range-inputs span {
            text-align: center;
            color: #666;
            font-weight: 500;
        }

        .chart-container {
            position: relative;
            height: 500px;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(102, 126, 234, 0.1);
            margin-bottom: 20px;
        }

        .results-area {
            background: #f8f9ff;
            border-radius: 15px;
            padding: 20px;
            min-height: 200px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #333;
            overflow-y: auto;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .coefficient-inputs {
            display: grid;
            grid-template-columns: auto 1fr auto 1fr auto 1fr;
            gap: 10px;
            align-items: center;
            margin: 15px 0;
        }

        .coefficient-inputs input {
            margin: 0;
        }

        .table-container {
            max-height: 400px;
            overflow-y: auto;
            background: white;
            border-radius: 10px;
            margin: 10px 0;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table th, .table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            font-size: 12px;
        }

        .table th {
            background: #4c6ef5;
            color: white;
            position: sticky;
            top: 0;
        }

        .table tr:nth-child(even) {
            background: #f8f9ff;
        }

        .log-entry {
            padding: 5px;
            margin: 2px 0;
            border-radius: 5px;
            font-size: 12px;
        }

        .log-entry.success {
            background: #d4edda;
            color: #155724;
        }

        .log-entry.error {
            background: #f8d7da;
            color: #721c24;
        }

        .log-entry.info {
            background: #d1ecf1;
            color: #0c5460;
        }

        .plot-image {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        @media (max-width: 1024px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: auto 1fr;
            }
            
            .control-panel {
                border-right: none;
                border-bottom: 1px solid rgba(102, 126, 234, 0.2);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="control-panel">
            <!-- Function Input Section -->
            <div class="section">
                <h3>📊 Function Input</h3>
                <div class="input-group">
                    <label for="functionInput">Enter function f(x):</label>
                    <input type="text" id="functionInput" placeholder="x**2, sin(x), log(x)">
                    <small style="color: #666; font-style: italic;">
                        Examples: x**2, sin(x), cos(x), log(x), sqrt(x), abs(x)
                    </small>
                </div>
                <button class="btn" onclick="addFunction()">Add Function</button>
                <button class="btn btn-danger" onclick="clearAllFunctions()">Clear All</button>
                
                <div class="functions-list" id="functionsList">
                    <div style="text-align: center; color: #666; padding: 20px;">
                        No functions added yet
                    </div>
                </div>
            </div>

            <!-- Plot Controls -->
            <div class="section">
                <h3>🔍 Plot Range</h3>
                <label>X Range:</label>
                <div class="range-inputs">
                    <input type="number" id="xMin" value="-10" step="0.5">
                    <span>to</span>
                    <input type="number" id="xMax" value="10" step="0.5">
                </div>
                <label>Y Range:</label>
                <div class="range-inputs">
                    <input type="number" id="yMin" value="-10" step="0.5">
                    <span>to</span>
                    <input type="number" id="yMax" value="10" step="0.5">
                </div>
                <button class="btn btn-secondary" onclick="updatePlot()">Update Plot</button>
                <button class="btn" onclick="resetRange()">Reset Range</button>
            </div>

            <!-- Quadratic Solver -->
            <div class="section">
                <h3>📐 Quadratic Solver</h3>
                <div>ax² + bx + c = 0</div>
                <div class="coefficient-inputs">
                    <label>a:</label>
                    <input type="number" id="coeffA" value="1" step="0.1">
                    <label>b:</label>
                    <input type="number" id="coeffB" value="0" step="0.1">
                    <label>c:</label>
                    <input type="number" id="coeffC" value="0" step="0.1">
                </div>
                <button class="btn btn-success" onclick="solveQuadratic()">Solve & Graph</button>
            </div>

            <!-- Function Analysis -->
            <div class="section">
                <h3>🔬 Function Analysis</h3>
                <div class="input-group">
                    <label>Select Function:</label>
                    <select id="analysisFunctionSelect">
                        <option value="">No functions available</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Analysis Point (x-value):</label>
                    <input type="number" id="analysisPoint" value="0" step="0.1">
                </div>
                <button class="btn btn-secondary" onclick="analyzeFunction()">Analyze</button>
            </div>

            <!-- Table Generation -->
            <div class="section">
                <h3>📋 Generate Table</h3>
                <button class="btn btn-secondary" onclick="generateTable()">Create Value Table</button>
                <div id="tableContainer" class="table-container" style="display: none;"></div>
                <button class="btn btn-success" onclick="exportCSV()" style="display: none;" id="exportBtn">Export CSV</button>
            </div>
        </div>

        <div class="plot-area">
            <div class="chart-container">
                <div id="plotContainer">
                    <div style="text-align: center; padding: 50px; color: #666;">
                        <h3>📊 Function Plot</h3>
                        <p>Add functions using the sidebar to see them plotted here</p>
                        <button class="btn" onclick="addExampleFunctions()">Add Example Functions</button>
                    </div>
                </div>
            </div>
            
            <div class="results-area" id="resultsArea">
                <strong>🧮 Advanced Graphing Calculator - Results Log</strong><br><br>
                Welcome! Enter functions using standard mathematical notation.<br>
                Supported functions: sin, cos, tan, log, ln, sqrt, abs, exp<br>
                Use ** for exponents (e.g., x**2 for x²)<br><br>
                <em>Results will appear here as you use the calculator...</em>
            </div>
        </div>
    </div>

    <script>
        let currentTableData = null;
        
        function addFunction() {
            const input = document.getElementById('functionInput');
            const expression = input.value.trim();
            
            if (!expression) {
                logMessage('Please enter a function!', 'error');
                return;
            }
            
            fetch('/api/add_function', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expression: expression })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    input.value = '';
                    updateFunctionsList(data.functions);
                    updateAnalysisSelect(data.functions);
                    updatePlot();
                    logMessage(`Added function: ${expression}`, 'success');
                } else {
                    logMessage(data.error, 'error');
                }
            })
            .catch(error => {
                logMessage(`Error: ${error}`, 'error');
            });
        }
        
        function removeFunction(funcId) {
            fetch('/api/remove_function', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ func_id: funcId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateFunctionsList(data.functions);
                    updateAnalysisSelect(data.functions);
                    updatePlot();
                }
            });
        }
        
        function clearAllFunctions() {
            fetch('/api/clear_functions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateFunctionsList([]);
                    updateAnalysisSelect([]);
                    updatePlot();
                    logMessage('Cleared all functions', 'info');
                }
            });
        }
        
        function updateFunctionsList(functions) {
            const container = document.getElementById('functionsList');
            
            if (functions.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">No functions added yet</div>';
                return;
            }
            
            container.innerHTML = '';
            
            functions.forEach((func, index) => {
                const item = document.createElement('div');
                item.className = `function-item color-${index % 5}`;
                item.innerHTML = `
                    <span>${func.name}</span>
                    <button class="btn btn-danger" onclick="removeFunction('${func.id}')" style="padding: 5px 10px; margin: 0; font-size: 12px;">×</button>
                `;
                container.appendChild(item);
            });
        }
        
        function updateAnalysisSelect(functions) {
            const select = document.getElementById('analysisFunctionSelect');
            select.innerHTML = '';
            
            if (functions.length === 0) {
                select.innerHTML = '<option value="">No functions available</option>';
                return;
            }
            
            functions.forEach(func => {
                const option = document.createElement('option');
                option.value = func.id;
                option.textContent = func.name;
                select.appendChild(option);
            });
        }
        
        function updatePlot() {
            const xMin = parseFloat(document.getElementById('xMin').value);
            const xMax = parseFloat(document.getElementById('xMax').value);
            const yMin = parseFloat(document.getElementById('yMin').value);
            const yMax = parseFloat(document.getElementById('yMax').value);
            
            fetch('/api/matplotlib_plot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    x_min: xMin,
                    x_max: xMax,
                    y_min: yMin,
                    y_max: yMax
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const plotContainer = document.getElementById('plotContainer');
                    plotContainer.innerHTML = `<img src="data:image/png;base64,${data.image}" class="plot-image" alt="Function Plot">`;
                }
            })
            .catch(error => {
                logMessage(`Plot error: ${error}`, 'error');
            });
        }
        
        function resetRange() {
            document.getElementById('xMin').value = -10;
            document.getElementById('xMax').value = 10;
            document.getElementById('yMin').value = -10;
            document.getElementById('yMax').value = 10;
            updatePlot();
            logMessage('Reset plot range to default', 'info');
        }
        
        function solveQuadratic() {
            const a = parseFloat(document.getElementById('coeffA').value) || 0;
            const b = parseFloat(document.getElementById('coeffB').value) || 0;
            const c = parseFloat(document.getElementById('coeffC').value) || 0;
            
            fetch('/api/solve_quadratic', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ a: a, b: b, c: c })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && !data.results.error) {
                    const results = data.results;
                    updateFunctionsList(data.functions);
                    updateAnalysisSelect(data.functions);
                    updatePlot();
                    
                    let message = `Quadratic Solution:\\n`;
                    message += `Equation: ${results.equation}\\n`;
                    message += `Discriminant: ${results.discriminant.toFixed(4)}\\n`;
                    message += `Root type: ${results.root_type}\\n`;
                    
                    if (Array.isArray(results.roots[0])) {
                        results.roots.forEach((root, i) => {
                            message += `Root ${i+1}: ${root}\\n`;
                        });
                    } else {
                        results.roots.forEach((root, i) => {
                            message += `Root ${i+1}: ${typeof root === 'number' ? root.toFixed(4) : root}\\n`;
                        });
                    }
                    
                    message += `Vertex: (${results.vertex[0].toFixed(4)}, ${results.vertex[1].toFixed(4)})`;
                    
                    logMessage(message, 'success');
                } else {
                    logMessage(data.results?.error || data.error || 'Error solving quadratic', 'error');
                }
            });
        }
        
        function analyzeFunction() {
            const funcId = document.getElementById('analysisFunctionSelect').value;
            const point = parseFloat(document.getElementById('analysisPoint').value) || 0;
            
            if (!funcId) {
                logMessage('Please select a function to analyze', 'error');
                return;
            }
            
            fetch('/api/analyze_function', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ func_id: funcId, point: point })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && !data.analysis.error) {
                    const analysis = data.analysis;
                    let message = `Function Analysis at x = ${analysis.point}:\\n`;
                    message += `f(${analysis.point}) = ${analysis.value.toFixed(4)}\\n`;
                    message += `f'(${analysis.point}) = ${analysis.derivative.toFixed(4)}\\n`;
                    message += `f''(${analysis.point}) = ${analysis.second_derivative.toFixed(4)}\\n`;
                    
                    if (analysis.critical_point) {
                        message += `Critical point: ${analysis.critical_type}`;
                    }
                    
                    logMessage(message, 'info');
                } else {
                    logMessage(data.analysis?.error || data.error || 'Error analyzing function', 'error');
                }
            });
        }
        
        function generateTable() {
            const xMin = parseFloat(document.getElementById('xMin').value);
            const xMax = parseFloat(document.getElementById('xMax').value);
            
            fetch('/api/generate_table', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    x_min: xMin,
                    x_max: xMax,
                    points: 21
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentTableData = data.table_data;
                    displayTable(data.table_data);
                    document.getElementById('exportBtn').style.display = 'inline-block';
                    logMessage('Generated function value table', 'success');
                } else {
                    logMessage(data.error, 'error');
                }
            });
        }
        
        function displayTable(tableData) {
            const container = document.getElementById('tableContainer');
            const headers = Object.keys(tableData);
            const rowCount = tableData[headers[0]].length;
            
            let html = '<table class="table"><thead><tr>';
            headers.forEach(header => {
                html += `<th>${header}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            for (let i = 0; i < rowCount; i++) {
                html += '<tr>';
                headers.forEach(header => {
                    const value = tableData[header][i];
                    html += `<td>${value}</td>`;
                });
                html += '</tr>';
            }
            
            html += '</tbody></table>';
            container.innerHTML = html;
            container.style.display = 'block';
        }
        
        function exportCSV() {
            if (!currentTableData) {
                logMessage('No table data to export', 'error');
                return;
            }
            
            fetch('/api/export_csv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ table_data: currentTableData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const blob = new Blob([data.csv_data], { type: 'text/csv' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'function_table.csv';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    logMessage('Exported table to CSV file', 'success');
                }
            });
        }
        
        function logMessage(message, type = 'info') {
            const resultsArea = document.getElementById('resultsArea');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.innerHTML = `<strong>[${timestamp}]</strong> ${message.replace(/\\n/g, '<br>')}`;
            resultsArea.appendChild(entry);
            resultsArea.scrollTop = resultsArea.scrollHeight;
        }
        
        function addExampleFunctions() {
            const examples = ['sin(x)', 'cos(x)', 'x**2/4'];
            
            examples.forEach(expr => {
                fetch('/api/add_function', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ expression: expr })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateFunctionsList(data.functions);
                        updateAnalysisSelect(data.functions);
                        updatePlot();
                    }
                });
            });
            
            logMessage('Added example functions: sin(x), cos(x), x²/4', 'success');
        }
        
        // Event listeners
        document.getElementById('functionInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addFunction();
            }
        });
        
        // Auto-update plot when range changes
        ['xMin', 'xMax', 'yMin', 'yMax'].forEach(id => {
            document.getElementById(id).addEventListener('change', function() {
                setTimeout(updatePlot, 500); // Debounce
            });
        });
        
        // Load results log on page load
        function loadResultsLog() {
            fetch('/api/results_log')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.log.length > 0) {
                    const resultsArea = document.getElementById('resultsArea');
                    resultsArea.innerHTML = '<strong>🧮 Advanced Graphing Calculator - Results Log</strong><br><br>';
                    
                    data.log.forEach(entry => {
                        const logEntry = document.createElement('div');
                        logEntry.className = `log-entry ${entry.type}`;
                        logEntry.innerHTML = `<strong>[${entry.timestamp}]</strong> ${entry.message}`;
                        resultsArea.appendChild(logEntry);
                    });
                    
                    resultsArea.scrollTop = resultsArea.scrollHeight;
                }
            });
        }
        
        // Initialize the app
        document.addEventListener('DOMContentLoaded', function() {
            loadResultsLog();
            logMessage('Advanced Graphing Calculator initialized', 'info');
            logMessage('Enter functions like: x**2, sin(x), log(x), sqrt(x)', 'info');
        });
    </script>
</body>
</html>"""
    
    with open('templates/index.html', 'w') as f:
        f.write(html_template)
    
    print("🚀 Starting Flask Graphing Calculator...")
    print("📊 Open your browser and go to: http://localhost:5000")
    print("✨ Features: Function plotting, quadratic solver, analysis tools, CSV export")
    
    app.run(debug=True, host='0.0.0.0', port=5000)