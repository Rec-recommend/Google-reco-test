#!/usr/bin/env python3
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
from surprise import KNNWithMeans, KNNBasic, SVD
from surprise import Dataset
from surprise import accuracy
from surprise import Reader
from surprise.model_selection import train_test_split
import pandas as pd
import pprint

# from MovieLens import MovieLens
# to_raw_uid: if we have an array of 600 unique users,
# trainset.to_raw_uid(10) will get the userid(mysql) of the tenth unique user
# helpul to convert from the trainset matrix to the msql_id
# to_raw(num)  ==> from matrix_row to msql_id
# to_inner('num')  ==> from msql_id to matrix_row id



class CollborativeRecommender():
	def __init__(self, file_path, line_format):
		reader = Reader(line_format=line_format, skip_lines=1, sep=',')
		dataset = Dataset.load_from_file(file_path, reader)
		self.trainset = dataset.build_full_trainset()
		self.similarity_matrix = []

		self.movies_df = pd.read_csv('./Recommenders/movies.csv')
		self.movieID_to_name = {}
		for index, row in self.movies_df.iterrows():
			movieID = int(row[0])
			movieName = row[1]
			self.movieID_to_name[movieID] = movieName


	def set_sim_options(self, sim_options):
		self.sim_options = sim_options

	def calc_sim_matrix(self):
		algo = KNNBasic(sim_options=self.sim_options)
		algo.fit(self.trainset)
		self.similarity_matrix = algo.compute_similarities()

	def get_similar_users(self, msql_id):
		user_inner_id = self.trainset.to_inner_uid(str(msql_id))
		similar_users = []
		user_similarity_matrix = self.similarity_matrix[user_inner_id]

		for index, similarity in enumerate(user_similarity_matrix):
			similar_users.append([int(self.trainset.to_raw_uid(index)), similarity])

		return sorted(similar_users, key=lambda tup: tup[1], reverse=True)[:10]

	def get_similar_items(self, msql_id):
		item_inner_id = self.trainset.to_inner_iid(str(msql_id))
		similar_items = []
		items_similarity_matrix = self.similarity_matrix[item_inner_id]

		for index, similarity in enumerate(items_similarity_matrix):
			item_ratings = self.trainset.ir[index]
			item_avg_rating = np.average(np.array(item_ratings), axis=0)[1]
			if(len(item_ratings) > 15 and item_avg_rating >3):
				similar_items.append([self.movieID_to_name[int(self.trainset.to_raw_iid(index))], similarity])

		return sorted(similar_items, key=lambda tup: tup[1], reverse=True)[:70]

	def get_similar_users_liked_items(self, msql_id):
		similar_users = self.get_similar_users(msql_id)
		recommendations = []
		for user in similar_users:
			user_raw_id     = str(user[0])
			user_similarity = user[1]
			user_ratings    = self.trainset.ur[int(self.trainset.to_inner_uid(user_raw_id))]
			user_avg_rating = np.average(np.array(user_ratings), axis=0)[1]
			for user_rating in user_ratings:
				user_rating_value = user_rating[1]
				item_index 		  = user_rating[0]
				item_ratings 	  = self.trainset.ir[item_index]
				item_avg_rating   = np.average(np.array(item_ratings), axis=0)[1]
				if(len(item_ratings) > 15 and item_avg_rating >3):
					item_raw_id = self.trainset.to_raw_iid(item_index)
					recommendation_value = float((user_avg_rating-user_rating_value) * user_similarity**2)
					if(recommendation_value != 0):
						recommendations.append([self.movieID_to_name[int(item_raw_id)], recommendation_value])

		return sorted(recommendations, key=lambda tup: tup[1], reverse=True)[:70]





file_path = "./Recommenders/ratings.1.csv"
line_format = 'user item rating'
sim_options = {'name': 'cosine', 'user_based': False, 'min_support': 10}

cfr = CollborativeRecommender(file_path, line_format)
cfr.set_sim_options(sim_options)
cfr.calc_sim_matrix()

res = cfr.get_similar_items('115617')
# res = cfr.get_similar_users_liked_items('2')

for s in res:
    print(*s)