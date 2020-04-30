# Finding harmonic and rhythmic connections in my music

A set of methodologies to identify harmonic and rhythmic pairs in a music library:
- Using librosa to compute the chromagram (pitch class profile) of audio files and calculate the distance in pitch distribution between songs
- Using spotipy to fetch song metadata via the Spotify API and filtering out pairings that are too dissimilar in terms of key and tempo

