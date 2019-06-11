#!/usr/bin/env python3

from DbHandler.TenantDbHandler import TenantDbHandler
from Recommenders.CollborativeRecommender import CollborativeRecommender
import pandas as pd
from pymongo import MongoClient

tenant_db_name = 'tn_GfxfFrKRovHKGJ4PNr4lOArxQNQEb'

# =====================================================
# Helper functions: dict for movies names and ids
# -----------------------------------------------------
movies_df = pd.read_csv('./Recommenders/movies.csv')
movieID_to_name = {}

for index, row in movies_df.iterrows():
	movieID = int(row[0])
	movieName = row[1]
	movieID_to_name[movieID] = movieName


# =====================================================
# store table in a dataframe
# -----------------------------------------------------
def prepare_df():
    df = pd.read_csv('./ratings.1.csv')
    return df

# =====================================================
# load data from mysql and train the model
# -----------------------------------------------------
# tenant = TenantDbHandler(tenant_db_name)
# items_table = tenant.get_pivot_table('ratings')
df = prepare_df()


line_format = 'user item rating'
sim_options = {'name': 'cosine', 'user_based': True}

cfr = CollborativeRecommender(sim_options, df, line_format)


# =====================================================
# get users recommendations and store them in mongodb
# -----------------------------------------------------
# users = df['end_user_id'].unique()
# mongo_client = MongoClient()
# mongo_db = mongo_client[tenant_db_name]
# count = 0
# recos = []
# for user in users:
#     res = cfr.get_recommendations(user)
#     recos.append({'user_id':int(user), 'items':[i[0] for i in res]})
#     count += 1
#     if count > 100000:
#         mongo_db.recommendations.insert_many(recos)
#         count = 0
#         recos = []

users = ['2']

for user in users:
	res = cfr.get_recommendations(user)
	for movie in res:
		print(movieID_to_name[movie[0]] , " ---- " , movie[1])
	print("--------------------------------------")


# =====================================================



# import sys
# db_name = sys.argv[1]
# print(t.get_eav_table("items"))
# file_path = "./Recommenders/ratings.1.csv"
# cfr = CollborativeRecommender(sim_options, file_path, line_format)

# =====================================================
# SELECT value FROM `iav` WHERE attribute_id = 1 AND item_id in (SELECT `item_id` FROM `ratings` WHERE end_user_id = 360 AND value = 5);
# SELECT value FROM `iav` WHERE item_id = 8864 AND attribute_id = 1


# users = ['611','612', '613']

# for user in users:
# 	res = cfr.get_recommendations(user)
# 	for movie in res:
# 		print(movieID_to_name[movie[0]] , " ---- " , movie[1])
# 	print("--------------------------------------")
