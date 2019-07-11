import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def get_files(filepath):
    """
    navigate through every file in every folder and returns all filepaths as a list
    
    example output:
        ['./data/song_data/A/A/C/TRAACER128F4290F96.json',
         './data/song_data/A/A/C/TRAACPE128F421C1B9.json',
         './data/song_data/A/A/C/TRAACHN128F1489601.json',
         './data/song_data/A/A/C/TRAACOW128F933E35F.json']
    """
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))
    return all_files

        
        
def process_song_file(cur, filepath):
    """
    processes song information and insert relevant values to tables
    for demonstration of logic, please refer to etl.ipynb and test.ipynb
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df[['song_id','title','artist_id','year','duration']]
    song_data = [x for x in song_data.values[0]]
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = df[['artist_id','artist_name','artist_location','artist_latitude','artist_longitude']].values
    artist_data = [item for item in artist_data[0]]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    processes user information and insert relevant values to tables
    for demonstration of the logic, please refer to etl.ipynb and test.ipynb
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page']=='NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'],unit='ms')
    
    # insert time data records
    column_labels =['start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday'] 
    time_data = (df['ts'].astype(str) +','+ t.dt.strftime('%H, %d, %W, %m, %Y, %a')).str.split(',')
    time_df = pd.DataFrame.from_dict(dict(time_data)).T
    time_df.columns = column_labels
    time_df.loc[:,'start_time']=pd.to_datetime(time_df['start_time'],unit='ms').astype(int)
    time_df.loc[:,'hour']=time_df['hour'].astype(int)
    time_df.loc[:,'day']=time_df['day'].astype(int)
    time_df.loc[:,'week']=time_df['week'].astype(int)
    time_df.loc[:,'month']=time_df['month'].astype(int)
    time_df.loc[:,'year']=time_df['year'].astype(int)
    time_df.loc[:,'weekday']=time_df['weekday'].str.strip()

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId','firstName','lastName','gender','level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    songplay_df = df
    songplay_df['ts'] = pd.to_datetime(songplay_df['ts'],unit='ms').astype(int)
    for index, row in df.iterrows():
        
        # get songid and artistid by using three pieces of information: 
        # 1. song title, 2. artist name, 3. duration of song
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        
        songplay_data = [index] + row[['ts', 'userId', 'level','sessionId','location','userAgent']].tolist() + [songid, artistid]
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    it is a pipeline function where it fetches data using all_files and then apply processing functions defined above
    """
    # get all files matching extension from directory
    all_files = get_files(filepath)

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()