# Household Expenditure Analysis

## Overview
This project analyzes household consumption expenditure data from the National Sample Survey Office (NSSO) in India. It aims to calculate the national share of spending across COICOP Level 1 categories and plot the Lorenz curve and computes the Gini coefficient.

## Dataset
The analysis uses three primary datasets located in the `data_package` directory:
- **households.csv**: Contains household identifiers, weights, urban/rural classification, and household sizes.
- **expenses.csv**: Contains household expenditures by product.
- **products.csv**: Contains product classifications under COICOP 1999.

## Methodology
The code is structured into functions for modular execution:
1. **Loading Data**: Reads and processes the three datasets.
2. **National Share of Spending**: Computes percentage spending for each category.
3. **Lorenz Curve & Gini Coefficient**: Plots the Lorenz curve and computes the Gini coefficient.

## Requirements
- Python 3.8+
- Pandas
- NumPy
- Matplotlib

Install dependencies using:
```sh
pip install -r requirements.txt
```

## Usage
Run the script using:
```sh
python analysis.py
```
Ensure that the dataset files are correctly placed in the `data_package` directory before execution.
Download the data from <a href="https://drive.google.com/file/d/1V4yCjs9Ug5-b8MSr5Iy1RAml_31Gg0aL/view">Dataset</a>
## Output
- National expenditure share printed to console.
- Lorenz curve plotted for visualization.
- Gini coefficient printed to console.

## Repository Structure
```
|-- data_package/
|   |-- households.csv
|   |-- expenses.csv
|   |-- products.csv
|-- analysis.py
|-- output
    |-- national_share.csv
    |-- lorez_cuve.png
|-- README.md
|-- requirements.txt
|-- technical_report.pdf
```
