from flask import Flask
from flask_cors import CORS
from routes.MontlyOutputPerWorkCell import monthlyOutputperWorkcell
from routes.PartsLiveData import parts_liveE24
from routes.PartsLiveData2 import parts_liveE25

app = Flask(__name__)
CORS(app)

# Register routes
app.register_blueprint(monthlyOutputperWorkcell)                    # Monthly Output per Workcell
app.register_blueprint(parts_liveE24)                                  # Parts Live Data
app.register_blueprint(parts_liveE25)

@app.route("/")
def home():
    return {"status": "Backend is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
