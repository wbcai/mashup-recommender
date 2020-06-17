# Finding harmonic and rhythmic connections in a DJ music collection

## Background

DJ software have evolved over the past decade to provide DJs with a wide array of features for music manipulation, such as loopers, samplers, beat match, and filters. While all these features were built around **how** DJs can perform their music, little advancements have been made on providing DJs with insights on **what music to play**.

A key differentiator of a skilled DJ is their ability to blend different songs together into a cohesive set. By executing seamless transitions between songs, DJs can introduce the audience to new ideas while sustaining the energy and momentum of the dancefloor – i.e., keep the crowd dancing! Because two or more songs are simultaneously playing during a transition, DJs must develop an intuition for rhythmic and harmonic differences between songs to ensure that they blend well together. 

Most DJ software compute two variables to help DJs assess these differences: beats per minute (BPM) and key. While BPM is effective for evaluating rhythmic differences, key is often an unreliable variable for evaluating harmonic differences due to complexities within a song such as sudden key changes or unconventional chord progressions. Furthermore, as key is a categorical variable, it cannot provide insight into the magnitude of harmonic differences between songs.

Thus, I was inspired to design a more sophisticated metric for evaluating harmonic differences between songs. More information on my *harmonic distance* metric can be found in my paper in `/deliverables`.

## Running the application

### Configure Spotify environment variables

Environment variables `SPOTIFY_CID` and `SPOTIFY_SECRET` are required for obtaining data from the Spotify Web API. You must first create a Spotify user account (Premium or Free). Then go to the [Dashboard](https://developer.spotify.com/dashboard) page at the Spotify Developer website and, if necessary, log in. Accept the latest Developer Terms of Service to complete your account set up.

At the Dashboard, you can now create a new Client ID (i.e., a new app). Once you fill in some general information and accept terms and conditions, you land in the app dashboard. Here you can see your Client ID and Client Secret. Set Client ID as your environment variable `SPOTIFY_CID` and the Client Secret as environment variable `SPOTIFY_SECRET`.

### Analyze audio files
`run.py` orchestrates the extraction of harmonic and rhythmic data from audio files and the calculation of harmonic distances between every possible song pair. 

The application accepts two arguements:
- REQUIRED: `--dir` or `-d` to specify the path of the directory that contains the audio files for analysis
- OPTIONAL: `--append` or `-a` specify the path of a previous analysis output (`features_*.csv` file); the app will exclude files that have already been analyzed, extract features for the new/additional files, and concatenate previous and new features into one `.csv` file.

For example, say your music collection is in `/audio_collection` and a portion of your collection has already be analyzed, with features exported as `features_2020_01_01.csv`. Then you would run the following code:

        python run.py -d /audio_collection -a features_2020_01_01.csv
        
All outputs from the application are saved in `/output`. 
