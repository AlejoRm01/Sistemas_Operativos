import argparse
import csv
import json
import matplotlib.pyplot as plt

def parsear_argumentos():
    parser = argparse.ArgumentParser(description="Simulador de Trading")

    parser.add_argument("-p", "--periodo", default="H1", help="Período (default: H1)")
    parser.add_argument("-f", "--formato", required=True, choices=["CSV", "JSON"], help="Formato del archivo")
    parser.add_argument("-m", choices=[
        "BRENTCMDUSD", "BTCUSD", "EURUSD", "GBPUSD",
        "USA30IDXUSD", "USA500IDXUSD", "USATECHIDXUSD",
        "XAGUSD", "XAUUSD"
    ])
    return parser.parse_args()

def leer_datos(archivo, formato):
    datos = []

    if formato == "CSV":
        with open('MonedasCSV/' + archivo, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for fila in csv_reader:
                datos.append({
                    "fecha": fila[0],
                    "apertura": float(fila[1]),
                    "maximo": float(fila[2]),
                    "minimo": float(fila[3]),
                    "cierre": float(fila[4]),
                    "operaciones": int(fila[5])
                })
    elif formato == "JSON":
        with open('MonedasJSON/' + archivo, "r") as json_file:
            datos = json.load(json_file)

    return datos

def graficar_velas(datos):
    fechas = [item["fecha"] for item in datos]
    aperturas = [item["apertura"] for item in datos]
    cierres = [item["cierre"] for item in datos]
    maximos = [item["maximo"] for item in datos]
    minimos = [item["minimo"] for item in datos]

    plt.figure(figsize=(16, 8))

    for i in range(len(fechas)):
        color = "g" if cierres[i] > aperturas[i] else "r"
        plt.plot([i, i], [minimos[i], maximos[i]], color=color)
        plt.plot([i - 0.2, i + 0.2], [aperturas[i], aperturas[i]], color=color, linewidth=0.5)
        plt.plot([i - 0.2, i + 0.2], [cierres[i], cierres[i]], color=color, linewidth=0.5)

    plt.ylabel("Precios")
    plt.title("Gráfico de Velas Japonesas")

def calcular_medias_moviles(datos, ventana):
    cierres = [item["cierre"] for item in datos]
    medias_moviles = []

    for i in range(len(cierres) - ventana + 1):
        media = sum(cierres[i:i + ventana]) / ventana
        medias_moviles.append(media)

    return medias_moviles

def graficar_medias_moviles(datos):
    ventana_sma5 = 5
    ventana_sma13 = 13

    medias_moviles_sma5 = calcular_medias_moviles(datos, ventana_sma5)
    medias_moviles_sma13 = calcular_medias_moviles(datos, ventana_sma13)

    color_sma5 = 'blue'
    color_sma13 = 'red'

    plt.figure(figsize=(10, 10))

    plt.subplot(2, 1, 1)
    plt.plot(range(ventana_sma5 - 1, len(datos)), medias_moviles_sma5, color=color_sma5, label=f"SMA {ventana_sma5}", linewidth=0.5)
    plt.ylabel("Promedio Móvil")
    plt.title("Gráfico de Promedio Móvil Simple (SMA5)")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(range(ventana_sma13 - 1, len(datos)), medias_moviles_sma13, color=color_sma13, label=f"SMA {ventana_sma13}", linewidth=0.5)
    plt.xlabel("Tiempo")
    plt.ylabel("Promedio Móvil")
    plt.title("Gráfico de Promedio Móvil Simple (SMA13)")
    plt.legend()

    plt.tight_layout()
    plt.show()

def main():
    args = parsear_argumentos()
    periodo = args.periodo
    formato = args.formato
    par = args.m

    nombreArchivo = par + "_" + periodo + "." + formato

    datos = leer_datos(nombreArchivo, formato)

    graficar_velas(datos)
    graficar_medias_moviles(datos)

if __name__ == "__main__":
    main()