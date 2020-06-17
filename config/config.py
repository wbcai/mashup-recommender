from os import path
import os
from datetime import date

TODAY = date.today()

# Output directory
PROJECT_HOME = path.dirname(path.dirname(path.abspath(__file__)))

# Logging
LOGGING_CONFIG = path.join(PROJECT_HOME, 'config/logging.conf')

# Features path
FEATURES_FILE = "output/features_" + str(TODAY) + ".csv"
FEATURES_PATH = path.join(PROJECT_HOME, FEATURES_FILE)
# Song distance path
DISTANCES_FILE = "output/distances_" + str(TODAY) + ".csv"
DISTANCES_PATH = path.join(PROJECT_HOME, DISTANCES_FILE)

# Features variable
NOTES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
BPM_MIN = 80
BPM_MAX = BPM_MIN * 2

# Distance calculation variables
BPM_THRESHOLD = 0.15

# Spotify API keys
SPOTIFY_CID = os.environ.get("SPOTIFY_CID")
SPOTIFY_SECRET = os.environ.get("SPOTIFY_SECRET")

