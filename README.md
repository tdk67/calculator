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

## 🧮 3D Quaternion Calculator

An interactive, educational 3D wireframe cube calculator powered by 4D quaternions ($q = w + xi + yj + zk$) and controlled via calculator keypad inputs.

### 🎯 Key Features
- **Live 3D Viewport**: Real-time perspective projection of a wireframe cube with RGB coordinate axes (Red: X, Green: Y, Blue: Z).
- **Calculator Keypad Stepping**: Numpad keys (`7`, `8`, `9`, `4`, `5`, `6`, `1`, `2`, `3`) control pitch, yaw, and roll around X, Y, Z axes.
- **Scientific Degree Input**: Direct numeric degree keypad (`Rx`, `Ry`, `Rz` + numeric entry) to apply exact angles.
- **Degrees UI & Internal Radians**: Shows intuitive degrees (°) on the LCD while performing all quaternion math internally in radians.
- **Educational Quaternion Inspector**: Live metrics and step-by-step breakdowns for unit quaternions ($q_x, q_y, q_z$), Hamilton products ($Q_{\text{final}} = q_z \otimes q_y \otimes q_x$), and 3D vertex transformations ($p' = Q \cdot p \cdot Q^*$).

### 🚀 Usage

Launch the 3D Quaternion Calculator app:

```bash
streamlit run quaternion_calculator.py
```

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

Launch the Rational Calculator:

```bash
streamlit run streamlit_calculator.py
```

Or launch the 3D Quaternion Calculator:

```bash
streamlit run quaternion_calculator.py
```

Streamlit will automatically open the web interface in your default browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
calculator/
├── .gitignore               # Ignored files (venv, pycache, etc.)
├── .python-version          # Specified Python version (3.12.9)
├── README.md                # Project documentation
├── requirements.txt         # Python package dependencies
├── streamlit_calculator.py  # Rational number calculator app
├── quaternion_calculator.py # 3D Quaternion calculator web app

```

