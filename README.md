# Ortho Projects

## Overview
This repository contains two main projects related to orthopedic research:
- `soccer_acl`: Analysis of soccer ACL injuries.
- `scoliosis`: Analysis of scoliosis data.

## Project Structure## Getting Started

ortho_projects/
├── soccer_acl/
│ ├── data/
│ ├── notebooks/
│ ├── scripts/
│ ├── docs/
│ └── results/
└── scoliosis/
├── data/
├── notebooks/
├── scripts/
├── docs/
└── results/

### Prerequisites
- Python 3.8 or higher
- `pip` for package management

### Setting Up the Environment

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/ortho_projects.git
    cd ortho_projects
    ```

2. **Navigate to the `soccer_acl` Project**:
    ```bash
    cd soccer_acl
    ```

3. **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### `soccer_acl` Project

1. Place your `acl_soccer_before.xlsx` file in the `data/` directory.
2. Run the data fetching script:
    ```bash
    python scripts/fetch_player_data.py
    ```
3. The results will be saved in the `results/` directory as `acl_soccer_after.xlsx`.