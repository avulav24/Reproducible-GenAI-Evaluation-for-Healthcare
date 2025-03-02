# CK AI Data Files for Manuscript and Analysis
## Table of Contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [License](#license)


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

## License 
MIT License

Copyright (c) 2025 avulav24

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
