#Script for clustering some n-dimensional data by k-means

from math import pow, sqrt
from random import sample

def distance(point1, point2):
    return sqrt(sum(pow(point1[i]-point2[i], 2) for i in range(len(point1))))

def average_points(list_of_points):
    total=[0 for i in range(len(list_of_points[0]))]
    for point in list_of_points:
        for i in range(len(point)):
            total[i]+=point[i]
    for i in range(len(total)):
        total[i]/=len(list_of_points)
    return total

#function returns a list of points which are the centers 
def k_means(points, num_means, min_distance):
    above_distance=True
    new_means=sample(points, num_means)   
    mean_points={}
    while above_distance:
        for mean in new_means:
            mean_points[mean]=[] 
        above_distance=False
        for point in points:
            smallest_distance=float('inf')
            smallest_mean=new_means[0]
            for mean in new_means:
                dist=distance(point, mean)
                if dist < smallest_distance:
                    smallest_distance=dist
                    smallest_mean=mean
            mean_points[smallest_mean].append(point)
        old_means=new_means.copy()
        new_means.clear()
        for key in old_means: 
            new_means.append(tuple(average_points(mean_points[key])))
            if distance(key, new_means[-1])>=min_distance:
                above_distance=True
        mean_points.clear() 
    return new_means
