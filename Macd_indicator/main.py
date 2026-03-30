
import pandas as pd # do danych
import matplotlib.pyplot as plt
import seaborn as sns
from functools import lru_cache

ZAKRES_PKT = 500

def wylicz(adres,adres_zapis, instrument):
        df = pd.read_csv(adres)
        df = df.tail(ZAKRES_PKT+1)

        KAPITAL_POCZATKOWY = 1000
        AKCJE = 0
        PROCENT_SPRZEDARZY = 50 # polowa
        MACD = []
        SIGNAL = []
        PKT_PRZECIECIA = []
        PORTFEL = []
        EMA_12 = 0
        EMA_26 = 0
        do_wykresow_kapitalu = []

        @lru_cache(maxsize=None)
        def ema_n( i, N): # i-przedział czasowy, N liczba okresów
                alfa = 2/(N+1)
                if i > 0:
                        return alfa* df.iloc[i]["Zamkniecie"] + (1-alfa)*ema_n(i-1,N)
                else:
                        return df.iloc[i]["Zamkniecie"]

        @lru_cache(maxsize=None)
        def signal_n( i, N):
                alfa = 2 / (N + 1)
                if i > 0:
                        return alfa * MACD[i]["MACD"] + (1 - alfa) * signal_n(i - 1, N)
                else:
                        return MACD[0]["MACD"]


        for i in range(ZAKRES_PKT):
                EMA_12 = ema_n( i,12)
                EMA_26 = ema_n( i,26)

                MACD.append({"Data": df.iloc[i]["Data"], "MACD": (EMA_12 - EMA_26)})
                SIGNAL.append({"Data": df.iloc[i]["Data"], "SIGNAL": signal_n(i, 9)})
        flaga = 0
        for i in range(len(MACD)-1):
                if MACD[i]["MACD"] > SIGNAL[i]["SIGNAL"] and MACD[i+1]["MACD"] <= SIGNAL[i+1]["SIGNAL"] and flaga == 1 : # sprzedaz
                        PKT_PRZECIECIA.append({"Data": df.iloc[i]["Data"], "Przeciecie": 0, "Wartosc": df.iloc[i]["Zamkniecie"]}) # df.iloc[i]["Zamkniecie"] -- dla zaznaczenie punktów na wykresie akcji ///  SIGNAL[i]["SIGNAL"] dla wyznacznikow
                        Zysk_strata = KAPITAL_POCZATKOWY
                        KAPITAL_POCZATKOWY = AKCJE*df.iloc[i]["Zamkniecie"]
                        AKCJE = 0
                        PORTFEL.append({"Data": df.iloc[i]["Data"], "Wykonana_akcja":  "sprzedaż","Cena": round(df.iloc[i]["Zamkniecie"],2), "Ilosc_akacji": round(AKCJE,2),"Zysk/Strata": round(KAPITAL_POCZATKOWY-Zysk_strata,2), "Wartosc_kapitalu": round(KAPITAL_POCZATKOWY,2)})

                elif MACD[i]["MACD"] < SIGNAL[i]["SIGNAL"] and MACD[i + 1]["MACD"] >= SIGNAL[i + 1]["SIGNAL"]:  # kupno
                        flaga =1
                        PKT_PRZECIECIA.append({"Data": df.iloc[i]["Data"], "Przeciecie": 1, "Wartosc": df.iloc[i]["Zamkniecie"]})
                        AKCJE = KAPITAL_POCZATKOWY/df.iloc[i]["Zamkniecie"]
                        PORTFEL.append({"Data": df.iloc[i]["Data"], "Wykonana_akcja":  "kupno", "Cena": round(df.iloc[i]["Zamkniecie"],2), "Ilosc_akacji": round(AKCJE,2),"Zysk/Strata": 0, "Wartosc_kapitalu": round(KAPITAL_POCZATKOWY,2)})
                        do_wykresow_kapitalu.append({"Data": df.iloc[i]["Data"], "Wartość": KAPITAL_POCZATKOWY}) # DO WYKRESOW Z ZYSKIEM ( kapitaøu

        df_wykres_kapitalu = pd.DataFrame(do_wykresow_kapitalu)       # do wykresów kapitałowych

        df_portfel = pd.DataFrame(PORTFEL)
        df_portfel.to_csv(adres_zapis, index=False)

        df_macd = pd.DataFrame(MACD)
        df_signal = pd.DataFrame(SIGNAL)
        df_przeciecie = pd.DataFrame(PKT_PRZECIECIA)

        #TODO- WARTOSC AKCJI
        plt.figure(figsize=(15, 10))  # Ustawienie rozmiaru wykresu, ZMIENIC NA TAIL
        sns.lineplot(data=df.head(ZAKRES_PKT), x="Data", y="Zamkniecie", label = "Cena BTCOIN")  # właściwa wartosc

        for i in range(len(df_przeciecie)):
            if df_przeciecie.iloc[i]["Przeciecie"] == 1:  # Kupno
                plt.scatter(df_przeciecie.iloc[i]["Data"], df_przeciecie.iloc[i]["Wartosc"], color='g', label='Kupno' if i <2 else None, zorder=5)
               # plt.text(df_przeciecie.iloc[i]["Data"], df_przeciecie.iloc[i]["Wartosc"]+10, f'{df_przeciecie.iloc[i]["Wartosc"]:.2f}', color='black', fontsize=13, ha='left', rotation=45)    # oznaczenia przy punktach

            elif df_przeciecie.iloc[i]["Przeciecie"] == 0:  # Sprzedaż
                plt.scatter(df_przeciecie.iloc[i]["Data"], df_przeciecie.iloc[i]["Wartosc"], color='y', label='Sprzedaż' if i < 2 else None, zorder=5)
              #  plt.text(df_przeciecie.iloc[i]["Data"], df_przeciecie.iloc[i]["Wartosc"]+10, f'{df_przeciecie.iloc[i]["Wartosc"]:.2f}', color='black', fontsize=13, ha='left',rotation=45)

        plt.xlabel("Data")
        plt.ylabel("Wartość")
        plt.title("Wykres wartości akcji ")
        plt.xticks(ticks=range(0, len(df), 5), rotation=90)    # 2 arg dla długości naszego argumentu
        plt.legend()
        plt.grid(True)
        plt.show()

        #TODO-MACD
        plt.figure(figsize=(15,10))  # Ustawienie rozmiaru wykresu, ZMIENIC NA TAIL
        sns.lineplot(data=df_signal, x="Data", y="SIGNAL", color="r", label="SIGNAL")  # SIGNAL
        sns.lineplot(data=df_macd, x="Data", y="MACD", color="b", label="MACD")  # MACDS
        # sns.lineplot(data=df_wykres_kapitalu, x="Data", y="Wartość", color="g", label="Zysk/Strata w zł")   # kapitał

        for i in range(len(df_przeciecie)):
            if df_przeciecie.iloc[i]["Przeciecie"] == 1:  # Kupno
                plt.scatter(df_przeciecie.iloc[i]["Data"], SIGNAL[i]["SIGNAL"], color='g', label='Kupno' if i <2 else None, zorder=5)
               # plt.text(df_przeciecie.iloc[i]["Data"], df_przeciecie.iloc[i]["Wartosc"]+10, f'{df_przeciecie.iloc[i]["Wartosc"]:.2f}', color='black', fontsize=13, ha='left', rotation=45)    # oznaczenia przy punktach

            elif df_przeciecie.iloc[i]["Przeciecie"] == 0:  # Sprzedaż
                plt.scatter(df_przeciecie.iloc[i]["Data"], SIGNAL[i]["SIGNAL"], color='y', label='Sprzedaż' if i < 2 else None, zorder=5)
              #  plt.text(df_przeciecie.iloc[i]["Data"], df_przeciecie.iloc[i]["Wartosc"]+10, f'{df_przeciecie.iloc[i]["Wartosc"]:.2f}', color='black', fontsize=13, ha='left',rotation=45)

        plt.xlabel("Data")
        plt.ylabel("Wartość")
        plt.title("Wykres wartości akcji ")
        plt.xticks(ticks=range(0, len(df), 5), rotation=90)    # 2 arg dla długości naszego argumentu
        plt.legend()
        plt.grid(True)
        plt.show()

        # WYKRESY KAPITALU
        sns.lineplot(data=df_wykres_kapitalu, x="Data", y="Wartość", color="g", label="Zysk/Strata w zł")  # kapitał

        for i in range(len(df_wykres_kapitalu)): # oznaczanie punktow na wykresie
                plt.scatter(df_wykres_kapitalu.iloc[i]["Data"], df_wykres_kapitalu.iloc[i]["Wartość"], color='b', label='Sprzedaż' if i < 2 else None, zorder=5)
                plt.text(df_wykres_kapitalu.iloc[i]["Data"], df_wykres_kapitalu.iloc[i]["Wartość"] + 10,
                f'{df_wykres_kapitalu.iloc[i]["Wartość"]:.2f}', color='black', fontsize=8, ha='left', rotation=45)

        plt.xlabel("Data")
        plt.ylabel("Wartość")
        plt.title("Wykres wartości portfela ")
        plt.xticks(ticks=range(0, len(df_wykres_kapitalu), 1), rotation=90)  # 2 arg dla długości naszego argumentu
        plt.legend()
        plt.grid(True)
        plt.show()

# adres = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\BTCusd.csv"
# adres_zapis = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\BTC_portfel.csv"
# wylicz(adres, adres_zapis,"BITCOIN")

# adres = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\WIG20.csv"
# adres_zapis = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\WIG20_portfel.csv"
# wylicz(adres, adres_zapis,"WIG20")

# adres = r"C:\Users\zucek\Downloads\lpp_d.csv"
# adres_zapis = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\LPP_portfel.csv"
# wylicz(adres, adres_zapis,"LPP")
# #
adres = r"C:\Users\zucek\Downloads\pkn_d.csv"
adres_zapis = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\ORLEN_portfel.csv"
wylicz(adres, adres_zapis,"ORLEN")
#
# adres = r"C:\Users\zucek\Downloads\rbw_d.csv"
# adres_zapis = r"C:\Users\zucek\PycharmProjects\MetodyNumeryczne-P1\RAINBOW_portfel.csv"
# wylicz(adres, adres_zapis,"RAINBOW")