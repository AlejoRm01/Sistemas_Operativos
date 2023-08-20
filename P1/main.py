import argparse
import csv
import json
import queue
import threading
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
                    "time": fila[0],
                    "open": float(fila[1]),
                    "high": float(fila[2]),
                    "low": float(fila[3]),
                    "close": float(fila[4]),
                    "volume": int(fila[5])
                })
    elif formato == "JSON":
        with open('MonedasJSON/' + archivo, "r") as json_file:
            datos = json.load(json_file)

    return datos

def graficar_velas(datos, formato):

    fechas = []
    aperturas = []
    cierres = []
    maximos = []
    minimos = []

    if formato == "CSV":
        fechas = [item["time"] for item in datos]
        aperturas = [item["open"] for item in datos]
        cierres = [item["close"] for item in datos]
        maximos = [item["high"] for item in datos]
        minimos = [item["low"] for item in datos]

    elif formato == "JSON":
        fechas = datos["time"]
        aperturas = datos["open"]
        cierres = datos["close"]
        maximos = datos["high"]
        minimos = datos["low"]

    plt.figure(figsize=(16, 8))

    for i in range(len(fechas)):
        color = "g" if cierres[i] > aperturas[i] else "r"
        plt.plot([i, i], [minimos[i], maximos[i]], color=color)
        plt.plot([i - 0.2, i + 0.2], [aperturas[i], aperturas[i]], color=color, linewidth=0.5)
        plt.plot([i - 0.2, i + 0.2], [cierres[i], cierres[i]], color=color, linewidth=0.5)

    plt.ylabel("Precios")
    plt.title("Gráfico de Velas Japonesas")
    

def calcular_medias_moviles(datos, ventana, formato):
    cierres = []
    if formato == "CSV":
        cierres = [item["close"] for item in datos]

    elif formato == "JSON":
        cierres = datos["close"]

    medias_moviles = []

    for i in range(len(cierres) - ventana + 1):
        media = sum(cierres[i:i + ventana]) / ventana
        medias_moviles.append(media)

    return medias_moviles

def calcular_y_graficar_medias_moviles(datos, formato, result_queue):
    ventana_sma5 = 5
    ventana_sma13 = 13

    medias_moviles_sma5 = calcular_medias_moviles(datos, ventana_sma5, formato)
    medias_moviles_sma13 = calcular_medias_moviles(datos, ventana_sma13, formato)

    result_queue.put((medias_moviles_sma5, medias_moviles_sma13))

def graficar_medias_moviles(medias_moviles_sma5, medias_moviles_sma13):
    color_sma5 = 'blue'
    color_sma13 = 'red'

    plt.figure(figsize=(10, 10))

    plt.subplot(2, 1, 1)
    plt.plot(range(len(medias_moviles_sma5)), medias_moviles_sma5, color=color_sma5, label="SMA 5", linewidth=0.5)
    plt.ylabel("Promedio Móvil")
    plt.title("Gráfico de Promedio Móvil Simple (SMA5)")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(range(len(medias_moviles_sma13)), medias_moviles_sma13, color=color_sma13, label="SMA 13", linewidth=0.5)
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

    # Crear una cola para pasar resultados entre hilos
    result_queue = queue.Queue()

    # Crear hilos para las tareas
    thread_lectura = threading.Thread(target=leer_datos, args=(nombreArchivo, formato))
    thread_calculo = threading.Thread(target=calcular_y_graficar_medias_moviles, args=(datos, formato, result_queue))

    # Iniciar los hilos
    thread_lectura.start()
    thread_calculo.start()

    # Esperar a que los hilos terminen
    thread_lectura.join()
    thread_calculo.join()

    # Obtener los resultados de la cola
    medias_moviles_sma5, medias_moviles_sma13 = result_queue.get()

    # Generar gráficos en el hilo principal
    graficar_velas(datos, formato)
    graficar_medias_moviles(medias_moviles_sma5, medias_moviles_sma13)

if __name__ == "__main__":
    main()