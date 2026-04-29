import flask
import requests
import functools

app = flask.Flask(__name__)

# ── Config ─────────────────────────────────────────
VALID_KEYS  = {"key_student_001", "key_faculty_999"}
COUNTRY_API = "https://restcountries.com/v3.1/name/{}"

# ── Data Store ──────────────────────────────────────
students = {
    "CS001": {"name": "Piyush Chouhan", "marks": 87, "country": "India"},
    "CS002": {"name": "Yash Patidar",  "marks": 92, "country": "Jamaica"},
    "CS003": {"name": "Om Kapoor", "marks": 78, "country": "Denmark"},
}

# ── Auth Decorator ──────────────────────────────────
def require_api_key(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        key = flask.request.headers.get("X-API-Key")
        if key not in VALID_KEYS:
            return flask.jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ── External API Call ───────────────────────────────
def get_country_info(country_name):
    try:
        resp = requests.get(
            COUNTRY_API.format(country_name.lower()),
            timeout=3
        )
        if resp.status_code == 200:
            data = resp.json()[0]
            return {
                "capital":    data.get("capital", ["N/A"])[0],
                "population": data.get("population", 0),
                "currency":   list(data.get("currencies", {}).keys())[0]
            }
    except Exception:
        pass
    return {"capital": "N/A", "population": 0, "currency": "N/A"}

# ── Routes ──────────────────────────────────────────

@app.route('/students', methods=['GET'])
@require_api_key
def get_students():
    return flask.jsonify(students), 200

@app.route('/students/<roll_no>', methods=['GET'])
@require_api_key
def get_student(roll_no):
    student = students.get(roll_no)
    if not student:
        return flask.jsonify({"error": "Student not found"}), 404
    # ⭐ Call external REST API to enrich our data
    country_info = get_country_info(student["country"])
    enriched = {**student, "country_details": country_info}
    return flask.jsonify(enriched), 200

@app.route('/students', methods=['POST'])
@require_api_key
def add_student():
    data = flask.request.get_json()
    roll = data.get("rollNo")
    if not roll or roll in students:
        return flask.jsonify({"error": "Invalid or duplicate roll number"}), 400
    students[roll] = {
        "name":    data.get("name", "Unknown"),
        "marks":   data.get("marks", 0),
        "country": data.get("country", "India")
    }
    return flask.jsonify({"message": "Student added", "rollNo": roll}), 201

@app.route('/students/<roll_no>/marks', methods=['PUT'])
@require_api_key
def update_marks(roll_no):
    if roll_no not in students:
        return flask.jsonify({"error": "Not found"}), 404
    data = flask.request.get_json()
    students[roll_no]["marks"] = data.get("marks", students[roll_no]["marks"])
    return flask.jsonify(students[roll_no]), 200

@app.route('/students/<roll_no>', methods=['DELETE'])
@require_api_key
def delete_student(roll_no):
    if roll_no not in students:
        return flask.jsonify({"error": "Not found"}), 404
    del students[roll_no]
    return flask.jsonify({"message": f"{roll_no} deleted"}), 200

if __name__ == '__main__':
    print("Mini Project API: http://localhost:5000")
    app.run(debug=True, port=5000)
