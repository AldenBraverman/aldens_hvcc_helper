# PowerShell script to initialize and update Git submodules
# Assumes it's in the same directory as the .gitmodules file

# https://chatgpt.com/c/67887346-2d18-8012-8fab-c9af2abcabef

function Install-GitSubmodules {
    # Check if .gitmodules file exists in the current directory
    if (Test-Path ".gitmodules") {
        Write-Host "Initializing and updating Git submodules..."

        # Initialize the submodules
        git submodule init

        # Update submodules recursively
        git submodule update --init --recursive

        Write-Host "Git submodules initialized and updated."
    } else {
        Write-Host "No Git submodules found."
    }
}

# Call the function
Install-GitSubmodules
