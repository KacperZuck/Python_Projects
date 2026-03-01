import timeit
from itertools import count

import pandas as pd # do danych
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import math
import xml.etree.ElementTree as ET

PLIKI = ["elblag-makowo.gpx", "gdansk-elblag.gpx", "zakopane-bielsko.gpx"] # , "elblag-wroclaw.gpx"
tab = []
ACCURACY = [5,10,27,50,70]

def ParseFileToTable(file):
    tree = ET.parse(file)
    root = tree.getroot()
    namespace = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    elevation = []
    points = 0

    for trkpt in root.findall(".//gpx:trkpt", namespace):
        x = trkpt.find("gpx:ele", namespace)
        if x is not None:
            points = points + 1
            elevation.append({"Wysokosc":float(x.text),"Punkt":points})

    return elevation

def Plot1(tab, filename):   # punkty z podpisem co 5 pkt
    df_data = pd.DataFrame(tab)
    plt.figure(figsize=(15, 10))
    sns.lineplot(data=df_data, y="Wysokosc", x="Punkt", color="g", label=f"{filename[:-4]}", linewidth=2)
    plt.scatter(data=df_data, y="Wysokosc", x="Punkt", s=12, color="r" )   # punkty
    for i in range( 0, len(df_data), 5):                                 # ( 0, len, co x ) ew. do zaimplementowania
        x = df_data.iloc[i]["Punkt"]
        y = df_data.iloc[i]["Wysokosc"]
        plt.text(x, y, f"{y:.1f}", color="black", fontsize=9, rotation=30)

    plt.xlabel("Numer badanego punktu")
    plt.ylabel("Wysokosc n.p.m [m]")
    plt.title(f"Wykres danych dla trasy: {filename[:-4]}")
    plt.xticks(ticks=range(0, len(df_data), 5), rotation=45, fontsize=8)
    plt.grid(True)
    plt.show()

def ProbkiPunktoweRownomierne(accuracy, tab, filename):
    if len(tab) < accuracy:
        print(f"Za mało punktów w {filename} do interpolacji.")
        return
    x_wartosc = [tab[i]["Punkt"] for i in range(0, len(tab), accuracy)]
    y_wartosc = [tab[i]["Wysokosc"] for i in range(0, len(tab), accuracy)]
    return x_wartosc, y_wartosc

def ProbkiPunktoweNieRownomiernie(accuracy, tab, filename):
    if len(tab) < accuracy:
        print(f"Za mało punktów w {filename} do interpolacji.")
        return
    points = int(len(tab)/accuracy)

    indices = [int((1 - np.cos(np.pi * i / (points - 1))) / 2 * (len(tab) - 1)) for i in range(points)]
    indices = sorted(set(indices))

    x_n = [tab[k]["Punkt"] for k in indices]
    y_n = [tab[k]["Wysokosc"] for k in indices]
    return x_n, y_n

def Lagrange(tab, filename ,x_wartosc, y_wartosc, rownomiernie):
    accuracy = int(len(tab)/len(x_wartosc))
    y_interp = []
    x_plot = np.linspace(min(x_wartosc), max(x_wartosc), len(tab))
    for x in x_plot:
        phi = 0
        buf = 0
        for i in range(len(x_wartosc)):
            buf = y_wartosc[i]
            for j in range(len(x_wartosc)):
                if j != i:
                    denominator = x_wartosc[i] - x_wartosc[j]
                    if denominator == 0:
                        buf = 0
                        break
                    buf *= (x - x_wartosc[j]) / denominator
            phi += buf

        y_interp.append(phi)


    plt.figure(figsize=(25, 10))
    plt.scatter(x_wartosc[3:-3], y_wartosc[3:-3], color='red', label='Interpolowane punkty', s=10)
    for i in range( 3, len(x_wartosc)-3):
        plt.text(x_wartosc[i], y_wartosc[i], f"{y_wartosc[i]:.1f}", color="black", fontsize=9, rotation=40)
    plt.plot(x_plot[3:-3], y_interp[3:-3], color='blue', label='Krzywa interpolacji')
    plt.xlabel('Numer punktu')
    plt.ylabel('Wysokość')
    plt.title(f"Interpolacja Lagrange’a dla {len(x_wartosc)} punktów {rownomiernie}(1/{accuracy} wszystkich) drogi {filename[:-4]}")
    plt.legend()
    plt.grid(True)
    plt.show()

def Interpolacja3Stopnia(x, y):
    n = len(x) - 1
    h = [x[i+1] - x[i] for i in range(n)]


    A = np.zeros((n+1, n+1))
    b_vec = np.zeros(n+1)

    A[0][0] = 1
    A[n][n] = 1

    for i in range(1, n):
        A[i][i-1] = h[i-1]
        A[i][i]   = 2*(h[i-1] + h[i])
        A[i][i+1] = h[i]
        b_vec[i] = 3*((y[i+1] - y[i])/h[i] - (y[i] - y[i-1])/h[i-1])

    c = np.linalg.solve(A, b_vec)

    a = y[:-1]
    b = [(y[i+1] - y[i])/h[i] - h[i]*(2*c[i] + c[i+1])/3 for i in range(n)]
    d = [(c[i+1] - c[i]) / (3*h[i]) for i in range(n)]

    return a, b, c[:-1], d

def Plot2(tab, x_wartosc, y_wartosc, a, b, c, d, filename):
    x_plot = np.linspace(min(x_wartosc), max(x_wartosc), len(tab))
    y_plot = []

    for x_val in x_plot:
        for i in range(len(x_wartosc) - 1):
            if x_wartosc[i] <= x_val <= x_wartosc[i + 1]:
                dx = x_val - x_wartosc[i]
                y_val = a[i] + b[i] * dx + c[i] * dx ** 2 + d[i] * dx ** 3
                y_plot.append(y_val)
                break

    plt.figure(figsize=(25, 10))
    plt.scatter(x_wartosc, y_wartosc, color="red", label="Punkty bazowe")
    for i in range(0, len(x_wartosc)):
        plt.text(x_wartosc[i], y_wartosc[i], f"{y_wartosc[i]:.1f}", color="black", fontsize=9, rotation=40)
    plt.plot(x_plot, y_plot, label="Interpolacja 3. stopnia", color="blue")
    plt.legend()
    plt.grid(True)
    plt.title(f"Interpolacja wielomianowa 3. stopnia dla {len(x_wartosc)} punktow drogi: {filename[:-4]}")
    plt.xlabel("Badane punkty")
    plt.ylabel("Wysokosc n.p.m [m]")
    plt.show()


time_l = []
time_w = []
for road in range(len(PLIKI)):
    tab = ParseFileToTable(PLIKI[road])
    # Plot1(tab, PLIKI[road])
    for k in ACCURACY:
          x_wartosc_n, y_wartosc_n = ProbkiPunktoweNieRownomiernie(k, tab, PLIKI[road])
          x_wartosc, y_wartosc = ProbkiPunktoweRownomierne(k, tab, PLIKI[road])
          start = timeit.default_timer()
          Lagrange(tab, PLIKI[road], x_wartosc, y_wartosc, "rownomiernie")
          end = timeit.default_timer()
          time_l.append(end-start)
          Lagrange(tab, PLIKI[road], x_wartosc_n, y_wartosc_n, "nie rownomiernie")
          # Współczynniki splajnu
          start = timeit.default_timer()
          a, b, c, d = Interpolacja3Stopnia(x_wartosc, y_wartosc)
          Plot2(tab, x_wartosc, y_wartosc, a, b, c, d, PLIKI[road])
          end = timeit.default_timer()
          time_w.append(end- start)

          a, b, c, d = Interpolacja3Stopnia(x_wartosc_n, y_wartosc_n)
          Plot2(tab, x_wartosc_n, y_wartosc_n, a, b, c, d, PLIKI[road])

    #break
    #print(road)

sr = 0.0
sr_w = 0.0
for i in range(len(time_l)):
    sr += time_l[i]
    sr_w += time_w[i]

print("L: ", sr/len(time_l))

print("w: ", sr_w/len(time_l))
