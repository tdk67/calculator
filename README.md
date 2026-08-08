# Rational Number Calculator

A lightweight interactive calculator web app built with Python and Streamlit that performs exact arithmetic using rational numbers (fractions).

---

## 📌 Background & Context

This project originated as a small demo experiment created during an **AI pair-programming** session. While the specific AI tool and original prompt details are no longer recorded, the core motivation was to test how effectively an AI assistant could design and implement a web-based calculator with exact fraction arithmetic rather than standard floating-point operations.

---

## 🎯 Goal & Features

Standard calculators use floating-point numbers, which can lead to representation errors (e.g., `1/3 + 1/6 = 0.49999999999999994`). The goal of this application is to perform exact mathematical operations using Python's built-in `fractions.Fraction` class.

### Key Capabilities
- **Exact Fraction Arithmetic**: Computes additions, subtractions, multiplications, and divisions using exact rational fractions.
- **Automatic Output Formatting**: Displays results as simplified fractions (e.g., `1/2`) or integers (e.g., `5` when denominator is 1).
- **Operator Precedence**: Correctly respects multiplication (`*`) and division (`/`) precedence over addition (`+`) and subtraction (`-`).
- **Interactive UI**: Built with Streamlit buttons (`st.button`) arranged in a clean calculator grid layout.

---

## 🐍 Prerequisites & Python Version

* **Python**: `3.12.x` (tested with Python 3.12)

---

## ⚙️ Installation

1. **Navigate to the project directory**:
   ```bash
   cd C:\Data\work\learning\calculator
   ```

2. **Create a Python 3.12 virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   * **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

Launch the Streamlit web app by running:

```bash
streamlit run streamlit_calculator.py
```

Streamlit will automatically open the web interface in your default browser at `http://localhost:8501`.

---

## 🧪 Testing & Edge Cases

When manually testing the application, verify the following scenarios and edge cases:

### 1. Basic Exact Rational Arithmetic
* **Test Input**: `1 / 3 + 1 / 6 =`
* **Expected Result**: `1/2` (demonstrates fraction simplification).

### 2. Operator Precedence
* **Test Input**: `2 + 3 * 4 =`
* **Expected Result**: `14` (multiplication evaluates before addition, rather than naive left-to-right evaluation `20`).

### 3. Division by Zero Handling
* **Test Input**: `5 / 0 =`
* **Expected Result**: Graceful error message displayed (`Division by zero is not allowed`) without crashing the Streamlit app.

### 4. Integer Simplification
* **Test Input**: `8 / 2 =`
* **Expected Result**: `4` (simplifies `4/1` to integer `4`).

### 5. Clear Button (`C`)
* **Test Input**: Enter `7 + 8`, then press `C`.
* **Expected Result**: Display resets to `0`, clears session state and previous error/result messages.

### 6. New Input After Evaluation
* **Test Input**: Evaluate `4 + 5 =` (`9`), then immediately press `2`.
* **Expected Result**: Display changes to `2` (starts a new expression) instead of `92`.

---

## 📁 Project Structure

```
calculator/
├── .gitignore               # Ignored files (venv, pycache, etc.)
├── .python-version          # Specified Python version (3.12.9)
├── README.md                # Project documentation
├── requirements.txt         # Python package dependencies
└── streamlit_calculator.py  # Main Streamlit calculator application
```
