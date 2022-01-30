import random
import matplotlib.pyplot as plt

def random_walk(mu, X0, sigma2, N):
    n = 0
    while (n < N):
        wt = random.normalvariate(0, (sigma2)**0.5)
        X1 = mu + X0 + wt
        yield X0
        X0 = X1
        n += 1
    return "done"

def zip_random_walk(mu, X0, sigma2, N, M):
    # M维时间上对齐的多维随机游走序列
    gen_list = []
    for i in range(M):
        gen_list.append(random_walk(mu, X0, sigma2, N))
    z = zip(*gen_list)
    return z

if __name__ == "__main__":
    z = zip_random_walk(1, 5, 200, 100, 6)
    ls = list(z)
    plt.plot(ls)
    plt.title("$X_t = 1 + X_{t-1} + w_t,\ \ \ w_t\sim N(0, 200)$")
    plt.savefig("high-dim.png", dpi=1000)
    plt.show()
    # while True:
    #     try:
    #         print(next(z))
    #     except StopIteration as si:
    #         print("Done")
    #         break