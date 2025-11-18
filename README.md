# Chemical Equipment Parameter Visualizer

This is a hybrid application that runs both as a Web Application (React) and a Desktop Application (PyQt5), as required by the screening task.

Both applications connect to a common Django backend that processes uploaded CSV files containing chemical equipment data.

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| Backend | Django + Django REST Framework | Common backend API |
| Frontend (Web) | React.js + Chart.js | Show table + charts |
| Frontend (Desktop) | PyQt5 + Matplotlib | Same visualization in desktop |
| Data Handling | Pandas | Reading CSV & analytics |
| Database | SQLite | Store last 5 uploaded datasets |

## Features Implemented

* **Basic Authentication**: Secure login is required on both Web and Desktop apps to access features.
* **CSV Upload**: Both Web and Desktop UIs can upload a CSV file to the backend.
* **Data Summary**: The backend analyzes the CSV and provides total count, averages (flowrate, pressure, temperature), and equipment type distribution.
* **Visualization**:
    * **Web**: Displays equipment distribution as a bar chart using Chart.js.
    * **Desktop**: Displays the same chart using Matplotlib.
* **History Management**: The backend stores and retrieves the 5 most recent uploads. Both UIs can view this history, load old data, and delete items.
* **PDF Report**: A "Download PDF" button generates a PDF report of the summary data for the selected file.

## Setup and Run Instructions

This project is divided into three parts. You must run all three simultaneously in separate terminals.

```sh
    #clone the project
    git clone https://github.com/ras-al/Chemical-Visualizer.git
```

### 1. Backend (Django)

The backend server must be running for the frontends to work.

1.  Navigate to the backend directory:
    ```sh
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```sh
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required packages:
    ```sh
    pip install -r requirements.txt 
    ```
4.  Run the database migrations:
    ```sh
    python manage.py migrate
    ```
5.  **Create a User (Required for Login):**
    Since authentication is enabled, you must create a user account to log in from the frontends.
    ```sh
    python manage.py createsuperuser
    # Follow the prompts to set a username and password
    ```
6.  Start the server (it will run on `http://127.0.0.1:8000`):
    ```sh
    python manage.py runserver
    ```

### 2. Frontend (React Web)

1.  Open a **new terminal** and navigate to the web frontend directory:
    ```sh
    cd frontend-web
    ```
2.  Install the Node.js dependencies:
    ```sh
    npm install
    ```
3.  Start the React development server:
    ```sh
    npm start
    ```
4.  Open your browser at `http://localhost:3000`. You will be prompted to log in. Use the credentials you created in the backend step.

### 3. Frontend (PyQt5 Desktop)

1.  Open a **third terminal** and navigate to the desktop frontend directory:
    ```sh
    cd frontend-desktop
    ```
2.  Create and activate a virtual environment (can be different from the backend's):
    ```sh
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```sh
    python main.py
    ```
5.  A login dialog will appear. Enter the credentials you created in the backend step to access the application.

## API Endpoints

* `POST /api/upload/`: Upload a CSV file.
* `GET /api/history/`: Retrieve a list of the last 5 uploads.
* `GET /api/summary/<int:pk>/`: Get detailed summary for a specific upload ID.
* `DELETE /api/summary/<int:pk>/`: Delete a specific upload.
* `GET /api/summary/<int:pk>/report/`: Download a PDF report for a specific upload.
