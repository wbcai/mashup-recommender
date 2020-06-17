import numpy as np
import pandas as pd
import librosa
import librosa.display
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config.config as config
from os import path
import os
import logging.config

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger('__name__')

def identify_tracks(dir_path, past_features = None):

	""" Get list of file names for analysis; remove files already analyzed
	input:
		dir_path (str): path of directory containing files for analysis
		past_analysis (obj): DataFrame of previous song features
	returns:
		new_tracks (obj): List of files to analyze
	"""

	# Obtain list of audio files from directory
	files = os.listdir(dir_path)
	# Exclude files starting with "." (DJ software metadata)
	files = [i for i in files if i[0] != '.']

	if past_features is not None:
		logger.info("Excluding songs already analyzed")

		# Remove files already analyzed
		past_tracks = past_features['track'].values.tolist()
		new_tracks = [i for i in files if i not in past_tracks]
	else:
		logger.info("No past analysis provided, will analyze all {} songs in {}".format(len(files), dir_path))
		new_tracks = files

	return new_tracks

def compute_chroma_bpm(filepath):
	
	"""Compute song's chromagram and BPM
	input: 
		filepath (str): path of audio file
	returns: 
		results (obj): list of 12 arrays of intensity values across samples
	"""
	
	y, sr = librosa.load(filepath)
	# Compute chroma features from the harmonic signal
	chromagram = librosa.feature.chroma_stft(y=y,sr=sr)
	chromaDF = pd.DataFrame(chromagram)

	# Filter intensity values less than 1
	chromaDF[chromaDF < 1] = 0
	chroma_f = chromaDF.sum(axis = 1)

	# Calculate chroma distribution
	chroma_p = [i / sum(chroma_f) for i in chroma_f]
	
	# Beat track on the percussive signal
	tempo, beat_frames = librosa.beat.beat_track(y=y,sr=sr)
	
	results = [tempo]
	results.append(chroma_p)
	
	return results

def extract_features(dir_path, tracks):
	
	"""
	input: 
		dir_path(str): directory path
		track (obj): list of filenames for analysis
	
	returns: 
		results_df (obj): DataFrame of track name, bpm, and chroma distribution
	"""
	
	# Identify all file paths
	track_paths = [path.join(dir_path, i) for i in tracks]

	results = []

	# Extract chroma and BPM data from tracks
	for track in track_paths:
		logger.info("Analyzing %s", track)
		new_result = compute_chroma_bpm(track)
		results.append(new_result)

	bpms = [i[0] for i in results]
	chromas = [i[1] for i in results]

	# Create Dataframe to store results
	results_df = pd.DataFrame(list(zip(tracks, bpms)), columns = ['track', 'bpm'])
	notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
	chroma_df = pd.DataFrame(chromas, columns = config.NOTES)
	results_df = pd.concat([results_df, chroma_df], axis = 1)

	# Convert tempo to fall between 80 and 160 BPMs
	results_df.loc[results_df.bpm <= config.BPM_MIN, 'bpm'] = \
		results_df.loc[results_df.bpm <= config.BPM_MIN, 'bpm'] * 2
	results_df.loc[results_df.bpm > config.BPM_MAX, 'bpm'] = \
		results_df.loc[results_df.bpm > config.BPM_MAX, 'bpm'] / 2

	return results_df

def get_spotify_features(search):
	
	""" Pull song metadata from Spotify API
	input: 
		search (str): search query (must replace all space with '+', e.g., beyonce+crazy+in+love)
	returns: 
		audio_feature (obj): dictionary of metadata
	"""
	
	# Configure API credentials
	client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CID, 
														client_secret=config.SPOTIFY_SECRET)
	sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
	
	# Find song ID
	query = sp.search(search)
	song_id = query['tracks']['items'][0]['id']

	# Use song ID to pull metadata
	audio_feature = sp.audio_features(song_id)[0]
	
	return audio_feature

def verify_bpm(results_df):
	
	""" Replace Librosa BPM with Spotify Tempo (more accurate)
	input: 
		results_df (obj): DataFrame from extract_features output
	output:
		verified_results_df (obj): DataFrame with Spotify Tempo
	"""
	
	tracks = results_df.loc[:,['track']]
	tracks['search_name'] = tracks.track
	
	# Edit track names for Spotify API call
	tracks.search_name = tracks.search_name.str.replace('.mp3', '')
	tracks.search_name = tracks.search_name.str.replace('.wav', '')
	tracks.search_name = tracks.search_name.str.replace('.m4a', '')
	tracks.search_name = tracks.search_name.str.replace('(', '')
	tracks.search_name = tracks.search_name.str.replace(')', '')
	tracks.search_name = tracks.search_name.str.replace(' - ', ' ')
	tracks.search_name = tracks.search_name.str.replace(' ', '+')
	
	search_list = tracks.search_name.to_list()
	
	searches = []
	features = []
	
	# Fetch track metadata from Spotify
	for search in search_list:

		try:
			feature = get_spotify_features(search)
			features.append(feature)
			searches.append(search)
			logger.info("%s found via Spotify API", search)

		except:
			logger.info("%s not found on Spotify API", search)
			
	spotify_results =  pd.DataFrame(features)
	spotify_results['search_name'] = searches
	
	# Ensure BPMs fall between 80 and 160
	spotify_results.loc[spotify_results.tempo < config.BPM_MIN, 'tempo'] = \
		spotify_results.loc[spotify_results.tempo < config.BPM_MIN, 'tempo'] * 2
	spotify_results.loc[spotify_results.tempo > config.BPM_MAX, 'tempo'] = \
		spotify_results.loc[spotify_results.tempo > config.BPM_MAX, 'tempo'] / 2

	spotify_results = tracks.merge(spotify_results, on = 'search_name')

	# Replace BPM with available Spotify tempo
	replace_tracks = spotify_results.track.to_list()

	results_df.loc[results_df.track.isin(replace_tracks), 'bpm'] = spotify_results.tempo

	logger.info("{} bpm values updated with Spotify data".format(len(replace_tracks)))

	return results_df

def calculate_distances(results_df):
	
	"""Calculate chroma bpm distances for every permutation pair;
		filter pairs with bpm distances that exceeds threshold
	input: 
		results_df (obj): DataFrame with chroma distribution and bpm
	output: 
		distances_df (obj): DataFrame of every pair permutation with chroma distribution difference and % bpm change
	"""
	
	# Perform cartesian join (compare each song to every other song)
	results_df['join'] = 1
	results_ct = results_df.merge(results_df, on = 'join', how = 'outer')

	s1_col = ['C_x', 'Db_x', 'D_x', 'Eb_x', 'E_x', 'F_x', 'Gb_x', 'G_x', 'Ab_x','A_x', 'Bb_x', 'B_x']
	
	s2_col = ['C_y', 'Db_y', 'D_y', 'Eb_y', 'E_y', 'F_y', 'Gb_y', 'G_y', 'Ab_y','A_y', 'Bb_y', 'B_y']

	# Create new dataframe to calculate chroma distances between songs
	distances_df = results_ct.loc[:,['track_x', 'track_y']]
	for i in range(0, len(s1_col)):
		dist = (results_ct[s1_col[i]] - results_ct[s2_col[i]])**2
		distances_df = pd.concat([distances_df, dist], axis = 1)

	distances_df['dist'] = distances_df.iloc[:,2:].sum(axis = 1)
	distances_df = distances_df.loc[distances_df.dist != 0, ['track_x', 'track_y', 'dist']]

	# Calculate % increase in BPM between songs
	bpm_dist = pd.DataFrame((results_ct['bpm_x'] - results_ct['bpm_y']).abs() / 
							results_ct[['bpm_x','bpm_y']].min(axis = 1), columns = ['bpm_inc'])

	bpm_dist = pd.concat([bpm_dist, results_ct[['track_x', 'track_y']]], axis = 1)

	# Merge features
	distances_df = distances_df.merge(bpm_dist, on = ['track_x', 'track_y'])
	start_len = len(distances_df)

	# Remove pairs with large bpm increases
	distances_df = distances_df[distances_df.bpm_inc < config.BPM_THRESHOLD].sort_values(by = 'dist')
	end_len = len(distances_df)

	logger.info("Track distances calculated. {} removed due to BPM differences greater than {}."\
		.format(start_len - end_len, config.BPM_THRESHOLD))
	
	return distances_df

