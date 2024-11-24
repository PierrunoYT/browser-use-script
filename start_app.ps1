# Check if virtual environment exists, if not create it
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate the virtual environment
& .\.venv\Scripts\activate

# Install dependencies if requirements.txt exists
if (Test-Path ".\requirements.txt") {
    Write-Host "Installing requirements..."
    pip install -r requirements.txt
}

# Install Playwright browsers
Write-Host "Installing Playwright browsers..."
playwright install

# Start the Flask application with the 'run' command
python app.py run
