# Github Repository Code Downloder

Python script utilizing Flask to create a web application that allows users to download code from public Github repository.

# Dependencies

pip install flask requests zipfile io ast

# Code breakdown

## Functions :

*  is_desired_file : Checks if a path ends with a common code file extension (python, javascript, typescript, svelte, rust).
*  is_likely_useful_file : Excludes files likely for configuration, testing, documentation or utility purposes based on file path and names.
*  has_sufficient_content : Filters out small files with less than a minimum number of lines (excluding comments).
*  remove_comments_and_docstrings : Uses the ast library to remove comments and docstrings from the code to potentially make it smaller.
*  download_repo : Downloads a zip archive of the Github repository master branch, extracts files, and writes relevant code snippets to a text file after applying the filtering functions.

## Flask App :

###  Defines routes(/ for GET and POST requests).
*  GET request on / renders an HTML template with a form to enter a Github repository URL.
*  POST request on / with the repository URL in the form data :
*  Downloads and processes the code using download_repo.
*  Creates a downloadable file containing the processed code.

# Running the application

*  Download the code from Github
*  git clone https://github.com/4solusi/fileconv.git
*  cd fileconv
*  pip install flask requests zipfile io ast (if you have not install dependencies)
*  python flask_app.py
*  This will start the Flask development server, typically making the application accessible on http://127.0.0.1:5000/ in your web browser.
*  Open the application URL in your web browser (http://127.0.0.1/5000/ by default)
*  Enter the URL of the public Github repository you want to download code from in the text field.
*  Click the "Download Code" button.
*  If the download is successful, your browser will prompt you to save a file named after the repository with the processed code content.

# Additional Notes

*  This is a development server meant for testing purposes. For a production environment. consider deploying the Flask application using a web server like Gunicorn
*  The script focuses on downloading code files and might not capture other repository assets.

## This README.md was written by free tier Google Gemini AI.
