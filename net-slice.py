import sys
from src.UI.slicer_UI import Visualizer

app = Visualizer(application_id="com.OnDemandSlices.GTKSlicer")

app.run(sys.argv)