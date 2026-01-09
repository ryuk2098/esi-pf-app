# ESI PF - Payroll & Banking Tools

Welcome to the **Payroll & Banking Suite**, a streamlined application designed to simplify payroll processing and banking validations. This tool allows users to generate ESI/PF challan files for specific companies (Somany, HNG) and verify IFSC codes efficiently.

## Features

### 📄 PF/ESI Calculator
- **Automated Processing**: Process payroll Excel files (`.xlsx`) to calculate PF and ESI contributions.
- **Multi-Company Support**: specialized workflows for **Somany** and **HNG**.
- **Challan Generation**:
    - Generates **PF Challan** text files (custom separator format).
    - Generates **ESI Challan** Excel files.
- **Data Preview**: View processed data and verify active member lists before generating files.
- **Summary Statistics**: Instant view of internal totals (Gross Wages, Total Employees, ESI Days, etc.) to cross-check with payroll data.

### 🔍 IFSC Checker
- **Format Validation**: Ensures the entered IFSC code follows the standard 11-character format (4 letters, 0, 6 alphanumeric).
- **Existence Check**: Verifies if the IFSC code exists using an external API.
- **Bank Details**: Retrieves and displays:
    - Bank Name & Branch
    - City & District
    - Full Address

## Installation

### Prerequisites
- [Python 3.12](https://www.python.org/downloads/) or higher.

### Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd esi-pf
    ```

2.  **Install dependencies**:
    This project is managed with `uv`, but supports standard pip installation.

    **Using `uv` (Recommended):**
    ```bash
    uv sync
    ```

    **Using `pip`:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, you can install from `pyproject.toml` or manually install the core libraries: `streamlit`, `pandas`, `openpyxl`, `xlsxwriter`, `lxml`)*

## Usage

1.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

2.  **Open in Browser**:
    The app should automatically open in your default browser. If not, click the URL provided in the terminal (usually `http://localhost:8501`).

3.  **Navigate**:
    - Use the sidebar to switch tools or select from the Home page.
    - **ESI PF Calculator**: Select Company -> Upload Payroll & Member Files -> Process -> Download Challans.
    - **IFSC Checker**: Enter Code -> Validate -> View Result.

## Structure
- `app.py`: Main entry point and navigation.
- `pages/`: Individual tool pages.
- `src/features/`: Core logic for calculations and file generation.
- `config/`: Configuration and state management.
