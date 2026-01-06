from flask import Flask
from flask_cors import CORS
from routes.MontlyOutputPerWorkCell import monthlyOutputperWorkcell
from routes.WeeklyOutputPerWorkCell import weeklyOutputperWorkcell
from routes.DailyOutputPerWorkCell import dailyOutputperWorkcell
from routes.PartsLiveData import parts_liveE24
from routes.PartsLiveData2 import parts_liveE25
from routes.SummaryCOperMonth import summaryCO
from routes.OEEByWCPerDay import OEE_by_WorkCell_per_Day
from routes.OEEByWCPerWeek import OEE_by_WorkCell_per_Week
from routes.OEEByWCPerMonth import OEE_by_WorkCell_per_Month
from routes.OEEByWC import OEE_by_WorkCell
from routes.OEEByZone import OEE_by_Zone
from routes.OEEByZonePerMonth import OEE_by_Zone_per_Month
from routes.OEEByZonePerWeek import OEE_by_Zone_per_Week
from routes.OEEByZonePerDay import OEE_by_Zone_per_Day
from routes.OEEByStation import OEE_by_Station
from routes.OEEByStationPerMonth import OEE_by_Station_per_Month
from routes.OEEByStationPerWeek import OEE_by_Station_per_Week
from routes.OEEByStationPerDay import OEE_by_Station_per_Day
from routes.RunningStatusWorkcell import Running_Status_Workcell
from routes.RunningStatusZone import Running_Status_Zone
from routes.RunningStatusStation import Running_Status_Station
from routes.OutputVsDailyTarget import OutputVsDailyTarget
from routes.COCompletion import COCompletion
import routes.RefreshMaterialized as refreshMaterialized

app = Flask(__name__)
CORS(app)

# Register routes
app.register_blueprint(monthlyOutputperWorkcell)                    # Monthly Output per Workcell
app.register_blueprint(weeklyOutputperWorkcell)                     # Weekly Output per Workcell
app.register_blueprint(dailyOutputperWorkcell)                      # Daily Output per Workcell 
app.register_blueprint(parts_liveE24)                               # Part E24-0100 Live Data
app.register_blueprint(parts_liveE25)                               # Part E25-0100 Live Data
app.register_blueprint(summaryCO)                                   # Summary CO per Month
app.register_blueprint(OEE_by_WorkCell_per_Day)                     # OEE by WorkCell per Day
app.register_blueprint(OEE_by_WorkCell_per_Week)                    # OEE by WorkCell per Week
app.register_blueprint(OEE_by_WorkCell_per_Month)                   # OEE by WorkCell per Month
app.register_blueprint(OEE_by_WorkCell)                             # OEE by WorkCell
app.register_blueprint(OEE_by_Zone)                                 # OEE by Zone
app.register_blueprint(OEE_by_Zone_per_Month)                       # OEE by WorkCell per Month
app.register_blueprint(OEE_by_Zone_per_Week)                        # OEE by WorkCell per Week
app.register_blueprint(OEE_by_Zone_per_Day)                         # OEE by WorkCell per Day
app.register_blueprint(OEE_by_Station)                              # OEE by Station
app.register_blueprint(OEE_by_Station_per_Month)                    # OEE by WorkCell per Month
app.register_blueprint(OEE_by_Station_per_Week)                     # OEE by WorkCell per Week
app.register_blueprint(OEE_by_Station_per_Day)                      # OEE by WorkCell per Day
app.register_blueprint(Running_Status_Workcell)                     # Running Status Workcell
app.register_blueprint(Running_Status_Zone)                         # Running Status Zone
app.register_blueprint(Running_Status_Station)                      # Running Status Station
app.register_blueprint(OutputVsDailyTarget)                         # Output vs Daily Target
app.register_blueprint(COCompletion)                                # Customer Order Completion

@app.route("/")
def home():
    return {"status": "Backend is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    refreshMaterialized.refresh_worker()  
