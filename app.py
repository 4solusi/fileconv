import os
import sys
import requests
import zipfile
import io
import ast
from flask import Flask, request, render_template_string

app = Flask(__name__)

def is_desired_file(file_path):
    return file_path.endswith('.py') or file_path.endswith('.js') or file_path.endswith('.ts') or file_path.endswith('.svelte') or file_path.endswith('.rs')

def is_likely_useful_file(file_path):
    excluded_dirs = ['docs', 'examples', 'tests', 'test', '__pycache__', 'scripts', 'utils', 'benchmarks', 'node_modules', '.venv']
    utility_or_config_files = ['hubconf.py', 'setup.py', 'package-lock.json']
    github_workflow_or_docs = ['stale.py', 'gen-card-', 'write_model_card']

    if any((part.startswith('.') for part in file_path.split('/'))):
        return False

    if 'test' in file_path.lower():
        return False

    for excluded_dir in excluded_dirs:
        if f'/{excluded_dir}/' in file_path or file_path.startswith(f'{excluded_dir}/'):
            return False

    for file_name in utility_or_config_files:
        if file_name in file_path:
            return False

    return all((doc_file not in file_path for doc_file in github_workflow_or_docs))

def has_sufficient_content(file_content, min_line_count=10):
    lines = [line for line in file_content.split('\n') if line.strip() and (not line.strip().startswith('#'))]
    return len(lines) >= min_line_count

def remove_comments_and_docstrings(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            node.value.s = ''
    return ast.unparse(tree)

def download_repo(repo_url, output_file):
    if '/tree/' in repo_url:
        repo_url = f'https://download-directory.github.io/?{repo_url}'

    response = requests.get(f'{repo_url}/archive/master.zip')
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in zip_file.namelist():
            if file_path.endswith('/') or not is_desired_file(file_path) or (not is_likely_useful_file(file_path)):
                continue

            file_content = zip_file.read(file_path).decode('utf-8')
            if is_desired_file(file_content) or not has_sufficient_content(file_content):
                continue

            try:
                file_content = remove_comments_and_docstrings(file_content)
            except SyntaxError:
                continue

            outfile.write(f'# File: {file_path}\n')
            outfile.write(file_content)
            outfile.write('\n\n')

@app.route('/', methods=['GET', 'POST'])
def download_repo_code():
    if request.method == 'POST':
        repo_url = request.form.get('repo_url')
        if repo_url:
            repo_name = repo_url.split('/')[-1]
            output_file = f'{repo_name}_code.txt'
            download_repo(repo_url, output_file)
            file_stream = io.StringIO()
            with open(output_file, 'r', encoding='utf-8') as f:
                file_stream.write(f.read())
            file_stream.seek(0)
            file_data = file_stream.getvalue()
            
            # Create a response object with the file data
            response = app.response_class(
                file_data,
                mimetype='text/plain',
                headers={'Content-Disposition': f'attachment; filename="{output_file}"'}
            )
            return response
    
    # Render the HTML template with CSS
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>GitHub Repository Code Downloader</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            h1 {
                color: #333;
            }
            input[type="text"] {
                padding: 10px;
                font-size: 16px;
                border-radius: 3px;
                border: 1px solid #ccc;
                width: 300px;
            }
            input[type="submit"] {
                padding: 10px 20px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>GitHub Repository Code Downloader</h1>
            <form method="post">
                <input type="text" id="repo_url" name="repo_url" placeholder="Enter repository URL" required>
                <br><br>
                <input type="submit" value="Download Code">
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True)