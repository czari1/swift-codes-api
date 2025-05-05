# SWIFT Parser API

A FastAPI application to parse, store, and query SWIFT/BIC codes from Excel (`.xlsx`) or CSV (`.csv`) files. The API provides endpoints to retrieve SWIFT code details, list codes by country, and perform basic CRUD operations.

---

## Features

*   **Data Parsing**: Loads SWIFT code data from `.xlsx` or `.csv` files using `pandas`.
*   **Database Storage**: Stores parsed data in an SQLite database using `SQLAlchemy`.
*   **API Endpoints**: Provides RESTful endpoints built with `FastAPI` for querying and managing SWIFT codes.
*   **Branch Association**: Automatically links branch codes to their headquarters during data loading and creation.
*   **Validation**: Includes basic validation for SWIFT code format using regex.
*   **Case Insensitive**: SWIFT code lookups are case-insensitive.
*   **Docker Support**: Ready for containerized deployment using Docker and Docker Compose.
*   **Testing**: Includes unit and integration tests using `pytest`, covering parser, repository, service, controller, and API layers.
*   **Interactive Docs**: Provides Swagger UI (`/docs`) and ReDoc (`/redoc`) for easy API exploration.

---

## Requirements

*   Python 3.12+
*   Docker & Docker Compose (Recommended for deployment)
*   Dependencies listed in [`requirements.txt`](requirements.txt)

---

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd SWITFParser
    ```

2.  **Prepare Data File:**
    *   Place your SWIFT code data file (e.g., `swiftCodes.xlsx` or `swiftCodes.csv`) inside the [`data/`](data/) directory. Create the directory if it doesn't exist:
        ```bash
        mkdir data
        cp /path/to/your/swift_data.xlsx data/
        ```
    *   The application looks for the file specified by the `SWIFT_DATA_PATH` environment variable in [`docker-compose.yml`](docker-compose.yml) or defaults to `data/swiftCodes.xlsx` if run locally (see [`app/main.py`](app/main.py)).

3.  **Option A: Using Docker (Recommended)**
    *   Ensure Docker and Docker Compose are installed.
    *   Build and run the container:
        ```bash
        # Make sure your user is in the 'docker' group or run with sudo
        # sudo usermod -aG docker $USER && newgrp docker
        docker compose up --build -d
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

The application can be configured using environment variables, primarily set in [`docker-compose.yml`](docker-compose.yml):

*   `SWIFT_DATA_PATH`: Path *inside the container* to the SWIFT code data file (e.g., `/app/data/swift_data.xlsx`).
*   `DATABASE_PATH`: Path *inside the container* to the SQLite database file (e.g., `/app/database/swift_codes.db`).
*   `PYTHONPATH`: Set to `/app` to ensure Python can find the application modules within the container.

When running locally, the application uses default paths relative to the project root (see [`app/main.py`](app/main.py) and [`app/database.py`](app/database.py)).

---

## Usage

### Running the Application

*   **Docker:** `docker compose up` (add `-d` to run in detached mode)
*   **Local:** `python -m app.main`

### Accessing the API

*   **Base URL:** `http://localhost:8080`
*   **Swagger UI (Interactive Docs):** `http://localhost:8080/docs`
*   **ReDoc:** `http://localhost:8080/redoc`
*   **Health Check:** `http://localhost:8080/health`

### API Endpoints

Defined in [`app/routes/swift_codes.py`](app/routes/swift_codes.py):

*   **`GET /health`**: Checks the API status. Returns `{"status": "healthy"}`.
*   **`GET /v1/swift-codes/{swift_code}`**: Retrieves details for a specific SWIFT code (case-insensitive), including associated branches if it's a headquarters.
*   **`GET /v1/swift-codes/country/{country_iso2}`**: Retrieves all SWIFT codes for a given country ISO2 code.
*   **`POST /v1/swift-codes/`**: Creates a new SWIFT code entry. Requires a JSON body matching the `SwiftCodeBase` schema defined in [`app/models/types.py`](app/models/types.py).
*   **`DELETE /v1/swift-codes/{swift_code}`**: Deletes a specific SWIFT code and its associations.

---

## Testing

Tests are written using `pytest` and cover various aspects of the application. Fixtures and test configurations are defined in [`tests/conftest.py`](tests/conftest.py).

1.  Make sure you have installed the development dependencies:
    ```bash
    # Ensure virtual environment is active if not using Docker
    pip install pytest pytest-asyncio pytest-cov httpx
    ```
2.  Run tests from the project root directory:

    *   **Locally:**
        ```bash
        # Run all tests
        python -m pytest

        # Run with verbose output
        python -m pytest -v

        # Run with test coverage report
        python -m pytest --cov=app
        ```
    *   **Using Docker:**
        ```bash
        # Run all tests inside the container
        docker compose run --rm api pytest

        # Run with coverage
        docker compose run --rm api pytest --cov=app
        ```

---

## Project Structure

```
SWITFParser/
├── app/                  # Application code
│   ├── controllers/      # API controllers
│   ├── models/           # Data models
│   ├── repositories/     # Database repositories
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── utils/            # Utilities
│   ├── database.py       # Database configuration
│   └── main.py           # Application entry point
├── data/                 # Data files directory
├── database/             # Database files directory
├── tests/                # Test suite
│   ├── fixtures/         # Test data fixtures
│   ├── integration/      # Integration tests
│   ├── unit/             # Unit tests
│   └── conftest.py       # Test configuration
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

