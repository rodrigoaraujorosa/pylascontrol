# Pylascontrol

A Python package for personal financial management and budget analysis.

## Overview

Pylascontrol helps you manage and visualize your personal finances by loading budget data from Excel spreadsheets and generating insightful charts. It's designed for educational purposes and personal use.

## Features

- 📊 Load budget data from Excel files in matrix format
- 📈 Generate multiple chart types (line, bar, balance)
- 💰 Track income, expenses, and contributions
- 📅 Organize data by month, category, and type
- 🎨 Visualize financial trends with Matplotlib

## Installation

```sh
pip install pylascontrol
```

Or install from source:

```sh
git clone https://github.com/rodrigoaraujorosa/pylascontrol.git
cd pylascontrol
pip install -e .
```

## Requirements

- Python >= 3.12
- pandas
- numpy
- matplotlib
- openpyxl

## Usage

### Loading Budget Data

```python
import pylascontrol as pc

# Load budget data from Excel file
df = pc.load_budget_excel("orcamento_pessoal.xlsx", year=2025)

# View the data
print(df.head())
```

The function expects an Excel file with a sheet named "ORÇAMENTO PESSOAL" containing:
- Months as columns (JAN, FEV, MAR, etc.)
- Categories as rows
- Monetary values in cells

### Generating Charts

#### Line Chart (Income vs Expenses)

```python
pc.plot_chart_by_type(df, year=2025, type="line")
```

#### Bar Chart (Side-by-side comparison)

```python
pc.plot_chart_by_type(df, year=2025, type="bar")
```

#### Balance Chart (Monthly balance)

```python
pc.plot_chart_by_type(df, year=2025, type="saldo")
```

## Data Structure

The `load_budget_excel` function returns a DataFrame with the following columns:

- `ano`: Year of the record
- `mes`: Month number (1-12)
- `tipo`: Type of transaction ('receita', 'despesa', 'aporte')
- `grupo`: Category group (e.g., 'TRANSPORTE', 'ENTRETENIMENTO')
- `categoria`: Specific category name
- `valor`: Monetary value

## Example

```python
import pylascontrol as pc

# Load data
df = pc.load_budget_excel("orcamento_pessoal.xlsx", year=2025)

# Generate all chart types
pc.plot_chart_by_type(df, year=2025, type="line")
pc.plot_chart_by_type(df, year=2025, type="bar")
pc.plot_chart_by_type(df, year=2025, type="saldo")
```

## License

MIT License - see LICENSE file for details

## Author

**Rodrigo de Araujo Rosa**  
Email: rodrigoaraujo.r@gmail.com  
GitHub: [rodrigoaraujorosa](https://github.com/rodrigoaraujorosa)

## Contributing

This is a beta version for educational purposes. Contributions, issues, and feature requests are welcome!

## Disclaimer

This package is intended for personal and educational use. Always verify financial calculations and consult with financial professionals for important decisions.
