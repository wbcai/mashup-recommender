import numpy as np
import pandas as pd
import argparse
from os import path
import os
import logging.config
import sys

from src.analyze_tracks import identify_tracks, extract_features, verify_bpm, calculate_distances
import config.config as config


logging.config.fileConfig(config.LOGGING_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger('__name__')

if __name__ == '__main__':

	# Parsers for directory of audio files and prior features analysis
	parser = argparse.ArgumentParser(description="Extract chroma distribution and calculate harmonic distances")
	parser.add_argument("--append", "-a", default = None, help = "Path of existing library features")
	parser.add_argument("--dir", "-d", default = None, help = "Path of audio file directory")
	args = parser.parse_args() 

	if args.dir is None:
		logger.warning("Directory not provided or not found.")
		sys.exit()

	if args.append is None:
		past_features = None
	else:
		past_features = pd.read_csv(args.append)

	# Get list of audio file names to analyze, excluding those already analyzed in the past
	new_tracks = identify_tracks(args.dir, past_features)

	# Extract features
	features_df = extract_features(args.dir, new_tracks)

	# Replace BPM with Spotify Tempo (if available)
	features_df = verify_bpm(features_df)

	# Save features_df in /output
	if past_features is not None:
		# Concat new features to past features DataFrame
		concat_features = pd.concat([past_features,features_df])
		concat_features.to_csv(config.FEATURES_PATH, index = False)
	else:
		features_df.to_csv(config.FEATURES_PATH, index = False)
		concat_features = features_df

	# Calculate and save distances between each song pair
	distances_df = calculate_distances(concat_features)
	distances_df.to_csv(config.DISTANCES_PATH, index = False)


