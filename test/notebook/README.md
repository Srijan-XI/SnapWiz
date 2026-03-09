# SnapWiz Interactive Notebook Tests

**Date:** 2026-02-09  
**Type:** Jupyter Notebooks (`.ipynb`)

---

## 📓 Overview

This directory contains interactive Jupyter/IPython notebooks for detailed testing and exploration of SnapWiz modules. Notebooks allow you to:

1. Visually inspect configurations
2. Run interactive experiments
3. See real-time retry logic in action
4. Explore exception hierarchies visually

---

## 📂 Notebooks

### 1. `test_config.ipynb`
**Purpose:** Test and visualize configuration settings.
- Displays all supported package formats in a table
- Verifies theme settings visually
- Checks language support dictionaries
- **Run this to:** Verify `config.py` is loading correctly.

### 2. `test_exceptions.ipynb`
**Purpose:** Interactive exception handling playground.
- Visualizes the entire exception hierarchy tree
- Simulates raising and catching various errors
- Demonstrates error messages and icons
- **Run this to:** Test error handling patterns.

### 3. `test_retry_utils.ipynb`
**Purpose:** Visual demonstration of retry logic.
- Simulates unstable network requests
- Visualizes exponential backoff delays (wait times)
- Tests decorator patterns interactively
- **Run this to:** Watch retry logic handle failures in real-time.

---

## 🚀 How to Run

### Prerequisites
You need `jupyter` or `notebook` installed, along with `pandas` for data tables and `matplotlib` for charts (optional).

```bash
# Activate virtual environment
source ../../venv/bin/activate

# Install Jupyter support
pip install jupyter pandas matplotlib
```

### Starting Jupyter
```bash
# Navigate to this directory
cd test/notebook

# Start the notebook server
jupyter notebook
```
This will open your browser. Click on any `.ipynb` file to run it.

---

## 📝 Usage Tips

- **Run All Cells:** Use the "Run All" button to execute the entire test suite in a notebook.
- **Interactive:** Feel free to modify cells to test different scenarios (e.g., change retry counts).
- **Restart Kernel:** If imports get stuck, use "Kernel > Restart & Run All".

---

**SnapWiz Testing** - *Interactive & Visual* 📊  
