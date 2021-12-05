import requests
import re
import json
import numpy as np
import pandas as pd
from datetime import datetime
pd.set_option('display.max_columns', None)

class YouTubeData:
    def __init__(self, api1, api2):
        self.api1 = api1
        self.api2 = api2
        self.word = ''
        self.sk = {'камчатка': ['вулканы', 'заповедник', 'серфинг', 'поход'], 'экология': ['катастрофы','проблем', 'природопользование'], 'экотуризм': ['россия','мир'], 'заповедники': ['волонтеры', 'россии','охрана']}

    def get_info_video(self, record):
        columns = ['video_id','publishe_date','channel_id','title','channel_title']
        rows = []
        list_rows = []
        
        rows.append(record['id'].get('videoId'))
        rows.append(record['snippet'].get('publishedAt'))
        rows.append(record['snippet'].get('channelId'))
        rows.append(record['snippet'].get('title'))
        rows.append(record['snippet'].get('channelTitle'))
        
        
        list_rows.append(rows)
        df_record = pd.DataFrame(list_rows,columns=columns)

        return df_record

    def chanel_id_func(self, key_word):
        api_key = self.api1
        search_link = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={key_word}&type=video&videoCaption=closedCaption&maxResults=50&key={api_key}'
        df_channels = pd.DataFrame()
        while True:

            response = requests.get(search_link).json()
            next_page_token = response.get('nextPageToken')
            
            for record in response['items']:
                
                df = self.get_info_video(record)
                df_channels = pd.concat([df_channels,df])
            #print(df_channels.shape)
            
            if next_page_token == None:
                break
                
            search_link  = search_link  + f'&pageToken={next_page_token}'

        return df_channels

    def dataa(self, date):
        data = date.split('T')[0]
        data = datetime.strptime(data, '%Y-%m-%d')
        return data

    def checkTitles(self, title):
        ws = self.word.split('+')
    #     a = False
    #     for w in ws:
    #         a |= (re.search(w.lower(), title.lower()) != None)
        a = []
        for w in ws:
            a.append(re.search(w.lower(), title.lower()) != None)
        if sum(a) == len(a):
            return 5
        if a[0]:
            return 3
        if a[1]:
            return 1
        return 0

    def youtube_video_statistics(self, api_key, video_id):
        base_info_url = 'https://www.googleapis.com/youtube/v3/videos?'
        info_url = base_info_url + f'part=statistics&key={api_key}&id={video_id}'
        response = requests.get(info_url).json()
        return response

    def youtube_channel_statistics(self, api_key,channel_id):
        base_info_url = 'https://www.googleapis.com/youtube/v3/channels?'
        info_url = base_info_url + f'part=statistics&id={channel_id}&key={api_key}'
        response = requests.get(info_url).json()
        return response

    def get_info_channel(self, record_video_statistic,record_channel_statistic):
        columns = ['all_channels_view_count','channel_subscriber_count','channel_video_count','view_count','like_count','dislike_count','comment_count']
        rows = []
        list_rows = []
        
        rows.append(record_channel_statistic['items'][0]['statistics'].get('viewCount'))
        rows.append(record_channel_statistic['items'][0]['statistics'].get('subscriberCount'))
        rows.append(record_channel_statistic['items'][0]['statistics'].get('videoCount'))
        
        rows.append(record_video_statistic['items'][0]['statistics'].get('viewCount'))
        rows.append(record_video_statistic['items'][0]['statistics'].get('likeCount'))
        rows.append(record_video_statistic['items'][0]['statistics'].get('dislikeCount'))
        rows.append(record_video_statistic['items'][0]['statistics'].get('commentCount'))

        list_rows.append(rows)
        df_record = pd.DataFrame(list_rows,columns=columns)

        return df_record

    def get_statistic_df(self, all_videos_id, all_channel_id):
        df_statistic = pd.DataFrame()
        for i in range(len(all_videos_id)):
            record_video_statistic = self.youtube_video_statistics(self.api2,all_videos_id[i])
            record_channel_statistic = self.youtube_channel_statistics(self.api2,all_channel_id[i])
            df = self.get_info_channel(record_video_statistic,record_channel_statistic)
            df_statistic = pd.concat([df_statistic,df])
        return df_statistic
    

    def index(self):
        our_dataframe = pd.DataFrame()
        for key_word in self.sk:
            for nonkey_word in self.sk[key_word]:
                df_search = self.chanel_id_func('+'.join([key_word, nonkey_word]))
                df_search.reset_index(drop=True,inplace = True)
                global word
                word = '+'.join([key_word, nonkey_word])
                df_search['check_title'] = df_search['title'].apply(self.checkTitles)
                df_search['publishe_date']= df_search['publishe_date'].apply(self.dataa)
                df_search = df_search[df_search['check_title'] > 1]
                our_dataframe = pd.concat([our_dataframe, df_search])
                
        our_dataframe.reset_index(drop=True,inplace = True)

        our_dataframe2 = our_dataframe.copy()

        all_videos_id = our_dataframe['video_id'].to_numpy()
        all_channels_id = our_dataframe['channel_id'].to_numpy()
        df_statistic = self.get_statistic_df(all_videos_id, all_channels_id)
        df_statistic.reset_index(drop=True,inplace = True)

        our_dataframe2 = our_dataframe2.join(df_statistic)

        list_of_columns = our_dataframe2.columns[-7:]
        for column in list_of_columns:
            our_dataframe2[column] = our_dataframe2[column].replace({None: 0})
            our_dataframe2[column] = our_dataframe2[column].astype(np.int64)

        our_dataframe2['avg_views_per_subsriber'] = our_dataframe2['all_channels_view_count']/(our_dataframe2['channel_subscriber_count']*our_dataframe2['channel_video_count'])
        our_dataframe2['avg_vieods_views_per_subsriber']=our_dataframe2['view_count']/our_dataframe2['channel_subscriber_count']
        our_dataframe2['likes_views_on'] = our_dataframe2['like_count']/our_dataframe2['view_count']
        our_dataframe2['comments_views_on']=our_dataframe2['comment_count']/our_dataframe2['view_count']
        our_dataframe2['likes_on_dislikes']=our_dataframe2['like_count']/our_dataframe2['dislike_count']

        return our_dataframe2

    
