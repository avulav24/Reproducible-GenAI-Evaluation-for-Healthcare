# CK AI Data Files for Manuscript and Analysis
## Table of Contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [License](#license)

## Requirements

- Python 3.7+
- Required libraries are listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate 

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   
## Usage 
1. Prepare the input data:
   - Ensure you have the necessary input files in the specified directories.
   - Input files:
   `query_metadata_initial.xlsx`
    `query_output-initial.xlsx`
    `query_output-initial-failed.xlsx`
    `Publication.xlsx`
    `sme_jira_master.xlsx`
2. Pass the below directory location path in the arguments
   - `feedback_directory` : location to all feedback data
   - `input_directory` : location to your input files
   - `out_directory` : location to store your output files
3. Run the script:
   ```bash
   python main.py feedback_directory input_directory out_directory
## Project Structure

## License 
