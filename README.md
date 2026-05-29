🗺️ MahaBHUMI — Land Records Management System
A mini web application inspired by MRSAC's MahaBHUMI initiative, built as part of internship preparation for Maharashtra Remote Sensing Application Centre (MRSAC), Nagpur.

📌 About the Project
MahaBHUMI is a Land Records Management System that allows users to register, search, update, and visualize land parcels across Maharashtra districts. It uses Remote Sensing and GIS concepts combined with a REST API backend and interactive frontend dashboard.

🚀 Features

📊 Dashboard — Live stats: total parcels, area, registered & disputed counts + bar charts
🗂️ Records — Searchable & filterable land parcel database
🗺️ Plot Map — Schematic color-coded parcel grid by land type
➕ Add Parcel — Register new land parcels with full details
🔌 REST API — Full CRUD API with search, filter & stats endpoints


🛠️ Tech Stack
LayerTechnologyBackendPython + FlaskDatabaseSQLite (sqlite3)FrontendHTML + CSS + JSAPI StyleREST

📁 Project Structure
mahabhumi/
├── app.py              ← Flask backend (REST API)
├── requirements.txt    ← Python dependencies
├── mahabhumi.db        ← SQLite database (auto-created)
├── static/
│   └── index.html      ← Frontend (Dashboard, Map, Records)
└── README.md

⚙️ Setup & Run
1. Clone the repository
bashgit clone https://github.com/YOUR_USERNAME/MahaBHUMI-GIS-Land-Records-System.git
cd MahaBHUMI-GIS-Land-Records-System
2. Create virtual environment
bashpython -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
3. Install dependencies
bashpip install -r requirements.txt
4. Run the server
bashpython app.py
5. Open in browser
http://127.0.0.1:5000

🔌 API Endpoints
MethodEndpointDescriptionGET/api/parcelsGet all parcels (supports ?search=, ?type=, ?district=)GET/api/parcels/:idGet single parcel by IDPOST/api/parcelsRegister new parcelPUT/api/parcels/:idUpdate existing parcelDELETE/api/parcels/:idDelete a parcelGET/api/statsDashboard summary statistics

🏛️ Inspired By
This project is inspired by MRSAC (Maharashtra Remote Sensing Application Centre) and their flagship MahaBHUMI land records digitization initiative under the Government of Maharashtra.

## 👨‍💻 Team

| Name | Branch |
|------|--------|
| Ayush | Data Science (DS) |
| Meghansh | Data Science (DS)  |
| Abhishek | Data Science (DS)  |
| Himanshu | Data Science (DS)  |

📍 Maharashtra, India

📄 License
This project is open source and available under the MIT License.
