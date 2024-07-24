# Ortho Projects

## Overview
This repository contains two main projects related to orthopedic research:
- `soccer_acl`: Analysis of soccer ACL injuries.
- `scoliosis`: Analysis of scoliosis data.

## Project Structure

```plaintext
ortho_projects/
├── requirements.txt
├── rendering_tools/
├── soccer_acl/
│   ├── data/
│   ├── notebooks/
│   ├── scripts/
│   ├── docs/
│   └── results/
└── scoliosis/
    ├── data/
    ├── notebooks/
    ├── scripts/
    ├── docs/
    └── results/
```

### Prerequisites
- Python 3.8 or higher
- `pip` for package management

### Setting Up the Environment

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/ortho_projects.git
    cd ortho_projects
    ```

2. **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

### Word Analyzer Tool ###

**Overview**

This tool provides various functionalities for text analysis, including tokenization, stemming, lemmatization, part-of-speech tagging, named entity recognition, sentiment analysis, word cloud generation, and more. It also includes BERT-based sentiment analysis and SHAP explanations for sentiment analysis results.

**Requirements**

To ensure compatibility with your system, make sure you have the following dependencies installed. The required packages are listed in requirements.txt.

**Installation**

Below are the instructions to use the script:

**3.1 Navigate to the script directory**

```bash
cd scoliosis/scripts
```
Run the script

**3.2 Use the following command to run the script. Replace <function> with one of the available functions: tokenize, stem, lemmatize, pos_tagging, ner, sentiment, wordcloud, top, bert.**

```bash
python3 text_to_tone.py <function> --text <path_to_text_file>
```

If no text file is provided, the script will use the default text file located at /Users/stephenmacneille/Desktop/20240616_Trial1.docx.


Example Commands

Tokenize text

```bash
python3 text_to_tone.py tokenize
```
Generate word cloud

```bash
python3 text_to_tone.py wordcloud
```

**Functions**

1. tokenize: Tokenizes the text into words and sentences.
2. stem: Applies stemming to the text.
3. lemmatize: Applies lemmatization to the text.
4. pos_tagging: Performs part-of-speech tagging.
5. ner: Conducts named entity recognition.
6. sentiment: Analyzes sentiment using TextBlob.
7. wordcloud: Generates a word cloud.
8. top: Displays the top words after removing stop words.
9. bert: Performs BERT-based sentiment analysis and explains results using SHAP.

**Additional Notes**

Ensure that the necessary NLTK data is downloaded. The script handles this automatically.
Custom stop words can be added or modified in the script.

Sample Data

A sample document (20240616_Trial1.docx) is provided for testing purposes.

### `soccer_acl` Project

1. Place your `acl_soccer_before.xlsx` file in the `data/` directory.
2. Run the data fetching script:
    ```bash
    python scripts/fetch_player_data.py
    ```
3. The results will be saved in the `results/` directory as `acl_soccer_after.xlsx`.
