# SWIFT Parser API

A FastAPI application to parse, store, and query SWIFT/BIC codes from Excel (`.xlsx`) or CSV (`.csv`) files. The API provides endpoints to retrieve SWIFT code details, list codes by country, and perform basic CRUD operations.

---

## Features

*   **Data Parsing**: Loads SWIFT code data from `.xlsx` or `.csv` files.
*   **Database Storage**: Stores parsed data in a database (SQLite by default).
*   **API Endpoints**: Provides RESTful endpoints for querying and managing SWIFT codes.
*   **Branch Association**: Automatically links branch codes to their headquarters.
*   **Validation**: Includes basic validation for SWIFT code format.
*   **Case Insensitive**: SWIFT code lookups are case-insensitive.
*   **Docker Support**: Ready for containerized deployment using Docker and Docker Compose.
*   **Testing**: Includes unit and integration tests using `pytest`.
*   **Interactive Docs**: Provides Swagger UI (`/docs`) for easy API exploration.

---

## Requirements

*   Python 3.12+
*   Docker & Docker Compose (Recommended for deployment)
*   Dependencies listed in `requirements.txt`

---

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd SWITFParser
    ```

2.  **Prepare Data File:**
    *   Place your SWIFT code data file (e.g., `swiftCodes.xlsx` or `swiftCodes.csv`) inside the `data/` directory. Create the directory if it doesn't exist:
        ```bash
        mkdir data
        cp /path/to/your/swiftCodes.xlsx data/
        ```
    *   The application looks for the file specified by the `SWIFT_DATA_PATH` environment variable, defaulting to `data/swiftCodes.xlsx`.

3.  **Option A: Using Docker (Recommended)**
    *   Ensure Docker and Docker Compose are installed.
    *   Build and run the container:
        ```bash
        # Make sure your user is in the 'docker' group or run with sudo
        # sudo usermod -aG docker $USER && newgrp docker
        docker compose up --build
        ```
    *   The API will be available at `http://localhost:8080`.

4.  **Option B: Local Python Environment**
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Run the application:
        ```bash
        python -m app.main
        ```
    *   The API will be available at `http://localhost:8080`.

---

## Configuration

The application can be configured using environment variables:

*   `SWIFT_DATA_PATH`: Path to the SWIFT code data file (default: `data/swiftCodes.xlsx`).
*   `DATABASE_PATH`: Path to the SQLite database file (default: `./swift_codes.db`).

These can be set in your environment or within the `docker-compose.yml` file.

---

## Usage

### Running the Application

*   **Docker:** `docker compose up`
*   **Local:** `python -m app.main`

### Accessing the API

*   **Base URL:** `http://localhost:8080`
*   **Swagger UI (Interactive Docs):** `http://localhost:8080/docs`
*   **Health Check:** `http://localhost:8080/health`

### API Endpoints

*   **`GET /health`**: Checks the API status.
*   **`GET /v1/swift-codes/{swift_code}`**: Retrieves details for a specific SWIFT code (case-insensitive).
*   **`GET /v1/swift-codes/country/{country_iso2}`**: Retrieves all SWIFT codes for a given country ISO2 code.
*   **`POST /v1/swift-codes/`**: Creates a new SWIFT code entry. Requires a JSON body matching the `SwiftCodeBase` schema.
*   **`DELETE /v1/swift-codes/{swift_code}`**: Deletes a specific SWIFT code.

---

## Testing

Tests are written using `pytest`.

1.  Make sure you have installed the development dependencies (if any, otherwise `requirements.txt` is sufficient).
2.  Run tests from the project root directory:
    ```bash
    # Ensure virtual environment is active if not using Docker
    python -m pytest
    ```
    Or run with more details:
    ```bash
    python -m pytest -v
    ```

---

## Project Structure
