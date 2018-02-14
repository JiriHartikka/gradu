import argparse
import os
import re
import json

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

import numpy as np

def read_data(data_dir):
    samples = []

    for dir_name in os.listdir(data_dir):
        if re.match("sample_\d+", dir_name):
            with open(os.path.join(data_dir, dir_name, "data.json"), 'r') as f:
                data = json.load(f)
            with open(os.path.join(data_dir, dir_name, "meta.json"), 'r') as f:
                meta_data = json.load(f)
            samples.append((meta_data, data))

    return samples


def plane(x, y, params):
    a, b, c = params
    z = a*x + b*y + c
    return z

def error(params, points):
    result = 0
    for x, y, z in points:
        plane_z = plane(x, y, params)
        diff = abs(plane_z - z)
        result += diff**2
    return result

def optimize_plane(points):
    import functools
    import scipy.optimize

    f = functools.partial(error, points = points)
    params0 = [0,0,0]
    res = scipy.optimize.minimize(f, params0)
    return res.x

def plot_plane(ax, points):

    x_min, y_min, z_min = np.min(points, 0)
    x_max, y_max, z_max = np.max(points, 0)

    a,b,c = optimize_plane(points)
    point = np.array([0.0, 0.0, c])
    normal = np.cross([1, 0, a], [0,1,b])
    d = -point.dot(normal)
    x, y = np.meshgrid([x_min, x_max], [y_min, y_max])
    z = (-normal[0] * x - normal[1] * y - d) * 1. / normal[2]
    ax.plot_surface(x, y, z, alpha = 0.2, color = [1,0,0])

def plot_num_rules(samples):
    support = []
    confidence = []
    num_rules = []

    for meta_data, data in samples:
        support.append(meta_data['support'])
        confidence.append(meta_data['confidence'])
        num_rules.append(len(data['rules']))

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    ax.set_xlabel('Min support')
    ax.set_ylabel('Min confidence')
    ax.set_zlabel('Number of rules')

    X, Y =  support, confidence
    #X, Y = np.meshgrid(support, confidence)
    Z = np.array(num_rules)
    Z = np.log10(num_rules)

    plot_plane(ax, zip(X, Y, Z))

    #ax.zaxis._set_scale('log')
    #ax.set_zscale('log')

    ax.w_zaxis.set_major_locator(LinearLocator(10))
    #ax.w_zaxis.set_major_formatter(FormatStrFormatter('10^%.1f'))
    ax.w_zaxis.set_major_formatter(FormatStrFormatter(r'$10^{%.1f}$'))

    ax.scatter(X, Y, Z)

    #ax.plot_wireframe(X, Y, Z)

    #surf = ax.plot_surface(
    #    X, Y, Z,
    #    cmap=cm.coolwarm,
    #    linewidth=0, antialiased=False
    #)

    #fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

def plot_runtime(samples):
    support = []
    confidence = []
    runtime = []

    for meta_data, data in samples:
        support.append(meta_data['support'])
        confidence.append(meta_data['confidence'])
        runtime.append(meta_data['execution_time'])

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    ax.set_xlabel('Min support')
    ax.set_ylabel('Min confidence')
    ax.set_zlabel('Runtime (seconds)')

    X, Y =  support, confidence
    Z = np.array(runtime)
    #Z = np.log10(runtime)

    plot_plane(ax, zip(X, Y, Z))

    #ax.w_zaxis.set_major_locator(LinearLocator(10))
    #ax.w_zaxis.set_major_formatter(FormatStrFormatter('10^%.0f'))

    ax.scatter(X, Y, Z)
    
    plt.show()
    
    
    
def main(data_dir):
    samples = read_data(data_dir)
    plot_num_rules(samples)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir")
    args = parser.parse_args()
    main(args.data_dir)
