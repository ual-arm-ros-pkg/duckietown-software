#!/usr/bin/env python
import numpy as np
from anti_instagram.kmeans_rebuild import CENTERS_BRYW, CENTERS_BYW

"""
This class calculates the optimal transform parameters based on the least squares optimization.
We want to map the input color space [B, G, R] to the 'true' color space [B', G', R'].

The color transform:     |a_B    0       0      b_B|       |B|     |B'|
                         |0      a_G     0      b_G|   *   |G| =   |G'|
                         |0      0       a_R    b_R|       |R|     |R'|
                                                           |1|

is a transform based on a scale [a_B, a_G, a_R] and a shift [b_B, b_G, b_R]
with the Ansatz y = a*x + b per channel.

For each channel there are two unknown parameters, 'a' and 'b'. Thus we need AT LEAST TWO correspondences
(from the found center 1 to the 'true' center and from the found center 2 to the 'true' center),
so that we can build the per-channel equations:

|B1 1|  *   |a_B|   =   |B'|
|B2 1|      |b_B|       |B'|

|G1 1|  *   |a_G|   =   |G'|
|G2 1|      |b_G|       |G'|

|R1 1|  *   |a_R|   =   |R'|
|R2 1|      |b_R|       |R'|

  A     *     x     =    b

I.e. we want to solve the problem Ax=b for each channel, where x are the transform parameters,
b the desired color value and A the matrix containing the color values of the found centers.



The inputs:
- number of centers:      this is the number of centers which are used to compute the transform
- found centers:          this is an array containing the centers of the clusters.

The outputs:
- scale and shift:        The scale and shift values correspond to 'a' and 'b' in y = a*x + b for each channel
"""

class calcTransform:

    # hardcoded centers from anti_instagram.kmeans
    centers_BYW = CENTERS_BYW
    centers_BRYW = CENTERS_BRYW

    centers = []            # n x 3 array, containing n 'true' centers in BGR
    num_centers = -1        # n
    found_centers = []      # n x 3 array, containing n found centers in BGR
    valueArrayBGR = []
    matrices_A = []         # 3 x n x 2 array, containing for each channel the found colol values   |R1   1|
                            #                                                                       |  ... |
                            #                                                                       |Rn   1|
    vectors_b = []          # 3 x n array, containing the 'true' colors for each channel
    scale = []
    shift = []
    residuals = []
    residualNorm = -1

    # initialize
    def __init__(self, numOcenters, found):
        assert (numOcenters >= 2), "at least two centers needed. Otherwise under constrained"
        self.num_centers = numOcenters
        if self.num_centers == 4:
            self.centers = self.centers_BRYW
        elif self.num_centers == 3:
            self.centers = self.centers_BYW

        self.found_centers = found
        self.scale = np.zeros(3, np.float64)
        self.shift = np.zeros(3, np.float64)
        self.residuals = np.zeros((3, 3), np.float64)
        self.valueArrayBGR = np.zeros((3, self.num_centers), np.uint8)
        for k in range(3): self.valueArrayBGR[k,:] = self.found_centers[:,k]

        self.matrices_A = np.zeros((3, self.num_centers, 2), np.uint8)
        self.vectors_b = np.zeros((3, self.num_centers), np.uint8)
        for channel in range(3):
            # prepare vectors b for each channel
            self.vectors_b[channel] = self.centers[:, channel]
            # prepare matrices A for each channel
            self.matrices_A[channel] = np.array(([[self.valueArrayBGR[channel, j], 1] for j in range(self.num_centers)]))
        print('matrices A: ' + str(self.matrices_A))
        print('vectors b: ' + str(self.vectors_b))

        print('created instance of calcTransform!')

    def returnResidualNorm(self):
        return self.residualNorm

    def calcTransform(self):
        # loop over the three color channels
        for channel in range(3):
            # calculate least squares
            X, r, rank, s = np.linalg.lstsq(self.matrices_A[channel],self.vectors_b[channel])
            self.scale[channel] = X[0]
            self.shift[channel] = X[1]
            self.residuals[channel] = r
        print('scale: ' + str(self.scale))
        print('shift: ' + str(self.shift))
        self.residualNorm = np.linalg.norm(self.residuals)
        print('residuals: ' + str(self.residualNorm))
