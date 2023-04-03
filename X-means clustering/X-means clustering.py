# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 13:37:29 2023

The program reads the data from an Excel file with words in the first column 
and real numbers in the following columns. The words are clustered using the 
Xmeans algorithm, with the results presented in such a way that the words in 
each cluster are ordered by distance from the centroid (the words closest to 
the centroid are presented at the top, the words furthest from the centroid 
are presented at the bottom).
Xmeans clustering automatically finds the optimal number of clusters.
PCA is used to convert the feature space into a two-dimensional space and to 
visualise the clusters in plots.

@author: Ahti Lohk
"""


from pyclustering.cluster.xmeans import xmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
import pandas as pd
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Reading data from an Excel file
df = pd.read_excel('Koik_300_andmed_D(list)_lemmaga.xlsx')

# Separating words from the first column
data = df.iloc[:, 1:].values

#Preparing the centroids - the number of centroids determines the number of 
#clusters from which X-means starts the analysis.
initial_centers = kmeans_plusplus_initializer(data, 2).initialize()

# Create an instance of the X-means algorithm. The algorithm starts the analysis 
# from two clusters, the maximum number of clusters that can be extracted is 20.
xmeans_instance = xmeans(data, initial_centers, 20)
xmeans_instance.process()

# Extracting the results of clustering: clusters and their centroids
clusters = xmeans_instance.get_clusters()
centers = xmeans_instance.get_centers()

# Adding the clustering results back to the original dataset.
df['cluster'] = -1
for cluster_idx, cluster in enumerate(clusters):
    df.loc[cluster, 'cluster'] = cluster_idx

# For each cluster, we find the ranges of values and the words contained in 
#the cluster
for cluster in range(len(centers)):
    cluster_data = df[df['cluster'] == cluster]
    distances = cdist(cluster_data.iloc[:, 1:-1], [centers[cluster]])
    sorted_indices = distances.argsort(axis=0).flatten()
    sorted_words = cluster_data.iloc[sorted_indices, 0].str.cat(sep=', ')
    min_values = cluster_data.min().iloc[1:-1]
    max_values = cluster_data.max().iloc[1:-1]
    print(f'\nCluster {cluster}:')
    print(f'Words: {sorted_words}')
    for feature, min_value, max_value in zip(min_values.index, min_values, max_values):
        print(f'{feature}: {min_value} - {max_value}')

# Visualising results in two-dimensional space using PCA
pca = PCA(n_components=2)
pca_data = pca.fit_transform(data)
pca_centers = pca.transform(centers)

# Visualise all clusters together
plt.scatter(pca_data[:, 0], pca_data[:, 1], c=df['cluster'])
plt.scatter(pca_centers[:, 0], pca_centers[:, 1], c='red', marker='x')
plt.title('All Clusters')
plt.show()

# Visualising each cluster in a separate figure
for cluster in range(len(centers)):
    plt.figure(figsize=(12, 8))
    cluster_data = pca_data[df['cluster'] == cluster]
    plt.scatter(cluster_data[:, 0], cluster_data[:, 1])
    plt.scatter(pca_centers[cluster, 0], pca_centers[cluster, 1], c='red', marker='x')
    words = df[df['cluster'] == cluster].iloc[:, 0]
    for i, word in enumerate(words):
        plt.annotate(word, (cluster_data[i, 0], cluster_data[i, 1]), fontsize=14)
    plt.title(f'Cluster {cluster}')
    plt.show()