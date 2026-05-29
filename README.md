# MahaBHUMI-GIS-Land-Records-System-
A project inspired by MRSAC's MahaBHUMI initiative
Project Structure
mahabhumi/
├── app.py              ← Flask backend (API server)
├── requirements.txt    ← Python dependencies
├── mahabhumi.db        ← SQLite database (auto-created on first run)
├── static/
│   └── index.html      ← Frontend (HTML + CSS + JS)
└── README.md
Step-by-Step Setup & Execution
Step 1 — Install Python
Make sure Python 3.8+ is installed. Check by running:

python --version
If not installed → download from https://www.python.org/downloads/

Step 2 — Open Terminal / Command Prompt
Windows: Press Win + R → type cmd → Enter
Mac/Linux: Open Terminal
Navigate to the project folder:

cd path/to/mahabhumi
Example:

cd C:\Users\YourName\Downloads\mahabhumi
Step 3 — Create a Virtual Environment (recommended)
python -m venv venv
Activate it:

Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate
You'll see (venv) appear in your terminal — that means it's active.

Step 4 — Install Dependencies
pip install -r requirements.txt
This installs Flask and Flask-CORS.

Step 5 — Run the Server
python app.py
You should see:

MahaBHUMI server running at http://127.0.0.1:5000
 * Running on http://127.0.0.1:5000
Step 6 — Open in Browser
Open your browser and go to:

http://127.0.0.1:5000
The full app will load with Dashboard, Records, Plot Map, Add Parcel, and API Docs tabs.

API Endpoints
Method	Endpoint	Description
GET	/api/parcels	Get all parcels (search/filter)
GET	/api/parcels/:id	Get one parcel by ID
POST	/api/parcels	Register new parcel
PUT	/api/parcels/:id	Update existing parcel
DELETE	/api/parcels/:id	Delete a parcel
GET	/api/stats	Dashboard summary statistics
Test the API with curl
Get all parcels:

curl http://127.0.0.1:5000/api/parcels
Add a new parcel:

curl -X POST http://127.0.0.1:5000/api/parcels \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "Ramesh Patil",
    "district": "Nagpur",
    "taluka": "Hingna",
    "village": "Bhandewadi",
    "survey_no": "24/B",
    "area_ha": 2.5,
    "land_type": "Agricultural",
    "status": "Registered"
  }'
Get stats:

curl http://127.0.0.1:5000/api/stats
Technologies Used
Layer	Technology
Backend	Python + Flask
Database	SQLite (via Python's built-in sqlite3)
Frontend	HTML + CSS + Vanilla JS
API Style	REST
Stop the Server
Press Ctrl + C in the terminal.

Common Errors & Fixes
Error	Fix
ModuleNotFoundError: flask	Run pip install -r requirements.txt
Address already in use	Another app is on port 5000. Change port=5000 to port=5001 in app.py
python not found	Use python3 instead of python
Page not loading	Make sure server is running and URL is http://127.0.0.1:5000
