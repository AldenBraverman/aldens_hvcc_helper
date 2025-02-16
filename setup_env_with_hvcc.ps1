# https://chatgpt.com/c/67887346-2d18-8012-8fab-c9af2abcabef

# example usage .\setup_env_with_hvcc.ps1 

# PowerShell script to initialize Git submodules, create a virtual environment, and install hvcc

function Install-GitSubmodules {
    if (Test-Path ".gitmodules") {
        Write-Host "Initializing and updating Git submodules..."

        git submodule init
        git submodule update --init --recursive

        Write-Host "Git submodules initialized and updated."
    } else {
        Write-Host "No Git submodules found."
    }
}

function Setup-VirtualEnv {
    $venvName = "hvcc_juce_helper_venv"

    # Check if the virtual environment already exists
    if (Test-Path $venvName) {
        Write-Host "Virtual environment '$venvName' already exists."
    } else {
        Write-Host "Creating virtual environment '$venvName'..."
        python -m venv $venvName
    }

    # Activate the virtual environment
    Write-Host "Activating virtual environment..."
    $activateScript = ".\$venvName\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Write-Host "Virtual environment '$venvName' activated."

        # Install hvcc
        Write-Host "Installing 'hvcc'..."
        pip3 install hvcc
    } else {
        Write-Host "Error: Failed to activate virtual environment."
    }
}

# Function to run hvcc
function Run-Hvcc {
    param (
        [string]$FilePath,
        [string]$Tag,
        [string]$Name,
        [string]$Generator = "js"
    )

    $outputsDir = "outputs"
    $timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
    $newDir = "$outputsDir/${timestamp}_$Tag"
    $env:new_dir_export = $newDir
    $heavyDir = "$newDir/Heavy"

    # Create required directories
    New-Item -ItemType Directory -Force -Path $outputsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $heavyDir | Out-Null

    # Validate and copy .pd file
    if (Test-Path $FilePath) {
        Copy-Item -Path $FilePath -Destination $newDir
    } else {
        Write-Host "Error: File '$FilePath' does not exist." -ForegroundColor Red
        exit 1
    }

    $hvccInputFile = "$newDir\" + (Split-Path -Leaf $FilePath)

    # Validate generator argument
    if ($Generator -eq "juce") {
        $generatorArg = "js" # this is hardcoded! we will have to change this
    } elseif ($Generator -eq "web") {
        Write-Host "Web support coming soon!" -ForegroundColor Yellow
        exit 1
    } else {
        $generatorArg = $Generator
    }

    # Run hvcc command
    Write-Host "Running hvcc..."
    hvcc $hvccInputFile -o $heavyDir -n $Name -g $generatorArg -p "./heavylib"

    # Run Python script with the new directory
    Write-Host "Running parse_params.py..."
    python3 parse_params.py $heavyDir $Name
}

# Execute functions
Install-GitSubmodules
Setup-VirtualEnv
Run-Hvcc -FilePath "C:\Users\Alden\Documents\GitHub\aldens_hvcc_helper\osc2.pd" -Tag "windows_test" -Name "my_synth" -Generator "juce"

