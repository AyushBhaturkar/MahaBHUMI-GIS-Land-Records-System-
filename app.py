from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import date
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__, static_folder='static')
CORS(app)

DB_PATH = 'mahabhumi.db'

# ---------- Database Setup ----------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parcels (
            id          TEXT PRIMARY KEY,
            owner       TEXT NOT NULL,
            district    TEXT NOT NULL,
            taluka      TEXT NOT NULL,
            village     TEXT NOT NULL,
            survey_no   TEXT NOT NULL,
            area_ha     REAL NOT NULL,
            land_type   TEXT NOT NULL,
            status      TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            latitude    REAL,
            longitude   REAL
        )
    ''')
    # Seed sample data if table is empty
    cursor.execute('SELECT COUNT(*) FROM parcels')
    if cursor.fetchone()[0] == 0:
        sample = [
            ('MH-NG-001','Ramesh Patil','Nagpur','Hingna','Bhandewadi','24/B',2.5,'Agricultural','Registered','2024-01-10', 21.1000, 78.9500),
            ('MH-NG-002','Sunita Deshpande','Nagpur','Kamptee','Khapri','88',0.8,'Residential','Registered','2024-02-14', 21.0583, 79.0683),
            ('MH-PN-003','Vijay Shinde','Pune','Haveli','Manjari','56/A',1.2,'Commercial','Pending','2024-03-05', 18.5275, 73.9482),
            ('MH-NS-004','Priya Kulkarni','Nashik','Niphad','Ozar','301',4.0,'Agricultural','Registered','2024-03-22', 20.1005, 73.9312),
            ('MH-MB-005','Ajay Tiwari','Mumbai','Borivali','Gorai','12/C',0.3,'Residential','Disputed','2024-04-01', 19.2325, 72.8450),
            ('MH-AU-006','Meera Gaikwad','Aurangabad','Paithan','Sarola','77',3.5,'Agricultural','Registered','2024-04-18', 19.6450, 75.3120),
            ('MH-AM-007','Suresh Wankhede','Amravati','Dhamangaon','Shelubazar','99/D',6.0,'Agricultural','Registered','2024-05-02', 20.7850, 78.1350),
            ('MH-PN-008','Lalita Bhosale','Pune','Mulshi','Pirangut','43',0.6,'Residential','Registered','2024-05-20', 18.5120, 73.6820),
            ('MH-NG-009','Deepak Ingle','Nagpur','Kalmeshwar','Saoner','18/E',1.8,'Industrial','Pending','2024-06-07', 21.2380, 78.9180),
            ('MH-NS-010','Anjali Pawar','Nashik','Baglan','Malegaon','55',0.9,'Commercial','Registered','2024-06-15', 20.5520, 74.5280),
        ]
        cursor.executemany(
            'INSERT INTO parcels VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', sample
        )
    conn.commit()
    conn.close()



# ---------- API Routes ----------

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# GET all parcels (with optional search & filter)
@app.route('/api/parcels', methods=['GET'])
def get_parcels():
    search = request.args.get('search', '').lower()
    land_type = request.args.get('type', '')
    district = request.args.get('district', '')

    conn = get_db()
    query = 'SELECT * FROM parcels WHERE 1=1'
    params = []

    if search:
        query += ' AND (LOWER(owner) LIKE ? OR LOWER(id) LIKE ? OR LOWER(village) LIKE ?)'
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if land_type:
        query += ' AND land_type = ?'
        params.append(land_type)
    if district:
        query += ' AND district = ?'
        params.append(district)

    query += ' ORDER BY created_at DESC'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# GET a single parcel by ID
@app.route('/api/parcels/<parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM parcels WHERE id = ?', (parcel_id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Parcel not found'}), 404


# POST — add a new parcel
@app.route('/api/parcels', methods=['POST'])
def add_parcel():
    data = request.get_json()
    required = ['owner', 'district', 'taluka', 'village', 'survey_no', 'area_ha', 'land_type', 'status']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Missing field: {field}'}), 400

    prefix_map = {
        'Nagpur': 'NG', 'Pune': 'PN', 'Mumbai': 'MB',
        'Nashik': 'NS', 'Aurangabad': 'AU', 'Amravati': 'AM'
    }
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM parcels').fetchone()[0]
    prefix = prefix_map.get(data['district'], 'XX')
    parcel_id = f"MH-{prefix}-{str(count + 1).zfill(3)}"

    # Assign default coordinates based on district center + small jitter
    district_centers = {
        'Nagpur': (21.1458, 79.0882),
        'Pune': (18.5204, 73.8567),
        'Mumbai': (19.0760, 72.8777),
        'Nashik': (19.9975, 73.7898),
        'Aurangabad': (19.8762, 75.3433),
        'Amravati': (20.9374, 77.7796)
    }
    import random
    center = district_centers.get(data['district'], (19.5, 76.0))
    lat = float(data.get('latitude', center[0] + random.uniform(-0.03, 0.03)))
    lon = float(data.get('longitude', center[1] + random.uniform(-0.03, 0.03)))

    conn.execute(
        'INSERT INTO parcels VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        (parcel_id, data['owner'], data['district'], data['taluka'],
         data['village'], data['survey_no'], float(data['area_ha']),
         data['land_type'], data['status'], str(date.today()), lat, lon)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Parcel registered', 'id': parcel_id}), 201


# PUT — update a parcel
@app.route('/api/parcels/<parcel_id>', methods=['PUT'])
def update_parcel(parcel_id):
    data = request.get_json()
    conn = get_db()
    row = conn.execute('SELECT * FROM parcels WHERE id = ?', (parcel_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Parcel not found'}), 404
    
    lat = data.get('latitude', row['latitude'])
    lon = data.get('longitude', row['longitude'])
    
    conn.execute('''
        UPDATE parcels SET owner=?, district=?, taluka=?, village=?,
        survey_no=?, area_ha=?, land_type=?, status=?, latitude=?, longitude=? WHERE id=?
    ''', (
        data.get('owner', row['owner']),
        data.get('district', row['district']),
        data.get('taluka', row['taluka']),
        data.get('village', row['village']),
        data.get('survey_no', row['survey_no']),
        float(data.get('area_ha', row['area_ha'])),
        data.get('land_type', row['land_type']),
        data.get('status', row['status']),
        float(lat) if lat is not None else None,
        float(lon) if lon is not None else None,
        parcel_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Parcel updated'})


# DELETE — remove a parcel
@app.route('/api/parcels/<parcel_id>', methods=['DELETE'])
def delete_parcel(parcel_id):
    conn = get_db()
    conn.execute('DELETE FROM parcels WHERE id = ?', (parcel_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Parcel deleted'})


# GET dashboard summary stats
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM parcels').fetchone()[0]
    total_area = conn.execute('SELECT ROUND(SUM(area_ha),2) FROM parcels').fetchone()[0] or 0
    registered = conn.execute("SELECT COUNT(*) FROM parcels WHERE status='Registered'").fetchone()[0]
    disputed = conn.execute("SELECT COUNT(*) FROM parcels WHERE status='Disputed'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM parcels WHERE status='Pending'").fetchone()[0]
    by_type = conn.execute(
        'SELECT land_type, COUNT(*) as count, ROUND(SUM(area_ha),2) as area FROM parcels GROUP BY land_type'
    ).fetchall()
    by_district = conn.execute(
        'SELECT district, COUNT(*) as count FROM parcels GROUP BY district ORDER BY count DESC'
    ).fetchall()
    conn.close()
    return jsonify({
        'total_parcels': total,
        'total_area_ha': total_area,
        'registered': registered,
        'disputed': disputed,
        'pending': pending,
        'by_type': [dict(r) for r in by_type],
        'by_district': [dict(r) for r in by_district],
    })


# ---------- Mock Image Generator ----------

def generate_mock_images():
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    samples_dir = os.path.join(static_dir, 'samples')
    os.makedirs(samples_dir, exist_ok=True)

    from PIL import Image, ImageDraw

    # Check if samples already exist
    sample_names = ['sample_agri.png', 'sample_industrial.png', 'sample_residential.png', 'sample_water.png']
    if all(os.path.exists(os.path.join(samples_dir, name)) for name in sample_names):
        return

    # 1. Agricultural (mostly green fields)
    img_agri = Image.new('RGB', (150, 150), (46, 125, 50))  # Dark green forest/fields base
    draw = ImageDraw.Draw(img_agri)
    # Draw various fields
    draw.rectangle([10, 10, 70, 70], fill=(76, 175, 80))    # Light green field
    draw.rectangle([80, 10, 140, 60], fill=(139, 195, 74))   # Yellow-green field
    draw.rectangle([10, 80, 60, 140], fill=(205, 220, 57))   # Chartreuse field
    draw.rectangle([70, 70, 140, 140], fill=(121, 85, 72))   # Brown soil field
    # Small house/shed
    draw.rectangle([40, 40, 50, 50], fill=(180, 180, 180))
    img_agri.save(os.path.join(samples_dir, 'sample_agri.png'))

    # 2. Industrial (concrete, grey, huge buildings)
    img_ind = Image.new('RGB', (150, 150), (220, 220, 220)) # Light grey concrete base
    draw = ImageDraw.Draw(img_ind)
    # Draw roads
    draw.line([0, 75, 150, 75], fill=(100, 100, 100), width=10) # main road
    draw.line([75, 0, 75, 150], fill=(100, 100, 100), width=8)  # branch road
    # Large factory buildings
    draw.rectangle([10, 10, 60, 60], fill=(170, 170, 180), outline=(130, 130, 140), width=2)
    draw.rectangle([90, 10, 140, 50], fill=(180, 150, 150), outline=(140, 110, 110), width=2)
    draw.rectangle([10, 90, 65, 140], fill=(150, 160, 170), outline=(110, 120, 130), width=2)
    draw.rectangle([90, 85, 140, 135], fill=(160, 160, 160), outline=(120, 120, 120), width=2)
    # A tiny patch of grass
    draw.rectangle([120, 55, 145, 80], fill=(90, 150, 90))
    img_ind.save(os.path.join(samples_dir, 'sample_industrial.png'))

    # 3. Residential (grids of small houses)
    img_res = Image.new('RGB', (150, 150), (235, 235, 230)) # Beige soil/pavement base
    draw = ImageDraw.Draw(img_res)
    # Grid of roads
    for offset in [30, 75, 120]:
        draw.line([0, offset, 150, offset], fill=(180, 180, 180), width=4)
        draw.line([offset, 0, offset, 150], fill=(180, 180, 180), width=4)
    # Red roof houses (small residential buildings)
    house_positions = [
        (5, 5), (40, 5), (85, 5), (125, 5),
        (5, 40), (45, 40), (85, 45), (130, 40),
        (10, 85), (50, 85), (90, 90), (125, 85),
        (5, 125), (40, 130), (80, 125), (125, 125)
    ]
    for px, py in house_positions:
        draw.rectangle([px, py, px+15, py+15], fill=(211, 47, 47)) # Red roof
        draw.rectangle([px+2, py+2, px+13, py+13], fill=(230, 74, 25)) # Bright red
    # Some green yards/trees
    draw.rectangle([85, 105, 115, 120], fill=(76, 175, 80))
    draw.rectangle([10, 105, 30, 120], fill=(76, 175, 80))
    img_res.save(os.path.join(samples_dir, 'sample_residential.png'))

    # 4. Water / Empty land
    img_water = Image.new('RGB', (150, 150), (210, 180, 140)) # Sandy brown/tan bare soil
    draw = ImageDraw.Draw(img_water)
    # Large water body (diagonal river or lake)
    draw.polygon([(0, 30), (60, 0), (150, 90), (150, 150), (90, 150)], fill=(33, 150, 243)) # Blue water
    # Wetlands edge (dark green-blue)
    draw.polygon([(0, 30), (20, 45), (60, 55), (100, 110), (90, 150)], fill=(56, 142, 60))
    img_water.save(os.path.join(samples_dir, 'sample_water.png'))


# ---------- AI/ML Classification Helper & Route ----------

import math

def get_tile_coords(lat, lon, zoom=17):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return xtile, ytile


@app.route('/api/classify', methods=['POST'])
def classify_land():
    data = request.get_json() or {}
    parcel_id = data.get('parcel_id')
    simulate_violation = data.get('simulate_violation', False)
    
    if not parcel_id:
        return jsonify({'error': 'Missing parcel_id'}), 400
        
    conn = get_db()
    parcel = conn.execute('SELECT * FROM parcels WHERE id = ?', (parcel_id,)).fetchone()
    if not parcel:
        conn.close()
        return jsonify({'error': 'Parcel not found'}), 404
        
    lat = parcel['latitude']
    lon = parcel['longitude']
    
    # If simulate_violation is enabled, override lat/lon with a dense industrial zone (MIDC Kalmeshwar)
    if simulate_violation:
        lat = 21.2380
        lon = 78.9180

    # Fetch satellite tile dynamically from Esri World Imagery
    zoom = 17
    xtile, ytile = get_tile_coords(lat, lon, zoom)
    tile_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ytile}/{xtile}"
    
    img = None
    try:
        req = urllib.request.Request(
            tile_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
            img = Image.open(BytesIO(img_data))
    except Exception as e:
        # Fallback to local sample image if fetch fails
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        fallback_map = {
            'Agricultural': 'sample_agri.png',
            'Industrial': 'sample_industrial.png',
            'Commercial': 'sample_industrial.png',
            'Residential': 'sample_residential.png'
        }
        fallback_file = fallback_map.get(parcel['land_type'], 'sample_agri.png')
        if simulate_violation:
            fallback_file = 'sample_industrial.png'
        fallback_path = os.path.join(static_dir, 'samples', fallback_file)
        if os.path.exists(fallback_path):
            img = Image.open(fallback_path)
        else:
            # Emergency blank fallback if samples are missing
            img = Image.new('RGB', (150, 150), (46, 125, 50))

    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Convert original to base64 so frontend can display the exact tile we classified
    buffered_orig = BytesIO()
    img.save(buffered_orig, format="JPEG")
    orig_b64 = f"data:image/jpeg;base64,{base64.b64encode(buffered_orig.getvalue()).decode('utf-8')}"

    # Resize for super fast K-Means (150x150 pixels)
    img_resized = img.resize((150, 150))
    pixels = np.array(img_resized)
    h, w, c = pixels.shape
    pixels_flat = pixels.reshape(-1, 3)

    # Run KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(pixels_flat)
    centers = kmeans.cluster_centers_

    # Identify classes by sorting centers
    # 1. Sort by greenness index (G - (R+B)/2) descending to find Vegetation
    cluster_stats = []
    for idx, center in enumerate(centers):
        r, g, b = center
        greenness = g - (r + b) / 2
        brightness = (r + g + b) / 3
        cluster_stats.append({
            'idx': idx,
            'greenness': greenness,
            'brightness': brightness
        })

    cluster_stats.sort(key=lambda x: x['greenness'], reverse=True)
    veg_cluster = cluster_stats[0]
    remaining = cluster_stats[1:]

    # 2. Sort remaining by brightness descending
    # Brighter is Built-up, darker is Water/Soil
    remaining.sort(key=lambda x: x['brightness'], reverse=True)
    built_cluster = remaining[0]
    water_cluster = remaining[1]

    label_map = {
        veg_cluster['idx']: 'Vegetation',
        built_cluster['idx']: 'Built-up',
        water_cluster['idx']: 'Water/Soil'
    }

    # Generate classified mask image
    colors = {
        'Vegetation': (46, 204, 113),  # Green
        'Built-up': (231, 76, 60),    # Red/Orange
        'Water/Soil': (52, 152, 219)  # Blue
    }

    classified_pixels = np.zeros_like(pixels_flat)
    for idx in range(3):
        class_name = label_map[idx]
        color = colors[class_name]
        classified_pixels[labels == idx] = color

    classified_img_arr = classified_pixels.reshape(h, w, 3).astype(np.uint8)
    classified_img = Image.fromarray(classified_img_arr)

    buffered = BytesIO()
    classified_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    classified_b64 = f"data:image/png;base64,{img_str}"

    # Calculate percentages
    total_pixels = len(labels)
    veg_pct = round((np.sum(labels == veg_cluster['idx']) / total_pixels) * 100, 1)
    built_pct = round((np.sum(labels == built_cluster['idx']) / total_pixels) * 100, 1)
    water_pct = round((np.sum(labels == water_cluster['idx']) / total_pixels) * 100, 1)

    is_mismatch = False
    land_type = parcel['land_type']
    current_status = parcel['status']

    if land_type == 'Agricultural':
        if built_pct > 35.0:
            is_mismatch = True
            audit_msg = f"WARNING: Mismatch detected! Parcel is registered as Agricultural, but satellite analysis detects {built_pct}% Built-up area (limit 35%). Potential encroachment/unauthorized construction."
        else:
            audit_msg = f"VERIFIED: Satellite analysis shows {veg_pct}% vegetation and {built_pct}% built-up area. Matches registered Agricultural land use."
    elif land_type in ['Industrial', 'Commercial', 'Residential']:
        if built_pct < 15.0:
            is_mismatch = True
            audit_msg = f"WARNING: Mismatch detected! Parcel is registered as {land_type}, but satellite analysis detects only {built_pct}% Built-up area (requires min 15%). Land appears vacant or undeveloped."
        else:
            audit_msg = f"VERIFIED: Satellite analysis shows {built_pct}% Built-up area. Matches registered {land_type} land use."
    else:
        audit_msg = f"VERIFIED: Satellite classification matches land use profile."

    if is_mismatch:
        if current_status != 'Disputed':
            conn.execute("UPDATE parcels SET status = 'Disputed' WHERE id = ?", (parcel_id,))
            conn.commit()
    else:
        if current_status == 'Disputed':
            conn.execute("UPDATE parcels SET status = 'Registered' WHERE id = ?", (parcel_id,))
            conn.commit()
    conn.close()

    return jsonify({
        'veg_pct': veg_pct,
        'built_pct': built_pct,
        'water_pct': water_pct,
        'original_image': orig_b64,
        'classified_image': classified_b64,
        'audit_message': audit_msg,
        'is_mismatch': is_mismatch,
        'parcel_id': parcel_id
    })


if __name__ == '__main__':
    init_db()
    generate_mock_images()
    print("MahaBHUMI server running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
