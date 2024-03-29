from numpy.random import normal
from numpy import clip

if __name__ == "__main__":
    w = 100
    h = 100
    # for mu in range(-1, 2, 1):
    #     for sigma in range(0, 5, 1):
    #         print(mu, sigma, normal(mu, sigma + 0.001, None))
    for i in range(10):
        x = normal(0, 0.5) * w
        y = normal(0, 0.5) * h
        x = clip(x, -100, 100)
        y = clip(y, -100, 100)
        print(x, y)
