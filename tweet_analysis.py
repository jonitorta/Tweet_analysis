from tweet_scrapper import Tweet_analysis
from config_file import options
from os import path

querry = options["querry"]
limit = options["limit"]
user_info = options["user info"]
user_info_attributes = options["user info attributes"]
save_status = options["save status"]
file_name = options["file name"]

if not path.exists(file_name):
    get_data = Tweet_analysis( querry= querry, limit=limit,
                           user_info=user_info, 
                           user_info_attributes= user_info_attributes,
                           save_data=save_status,
                           file_name= file_name)