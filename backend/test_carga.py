import time
import threading
import requests

# URL de tu backend (puedes cambiar el endpoint si prefieres "/" o "/tareas/")
URL = "http://127.0.0.1:8000/"

# Lista para almacenar los tiempos de respuesta de cada "usuario"
resultados = []

def simular_usuario(usuario_id):
    """Simula la petición HTTP de un usuario concurrente."""
    inicio = time.time()
    try:
        response = requests.get(URL)
        fin = time.time()
        duracion = fin - inicio
        resultados.append((usuario_id, response.status_code, duracion))
        print(f"Usuario {usuario_id}: Código {response.status_code} - Tiempo: {duracion:.4f} segundos")
    except Exception as e:
        fin = time.time()
        print(f"Usuario {usuario_id}: Error - {e}")

def ejecutar_prueba_carga():
    print("--- INICIANDO PRUEBA DE CARGA PNF-005 (3 Usuarios Concurrentes) ---")
    hilos = []

    # Creamos 3 hilos para simular a los 3 usuarios al mismo tiempo
    for i in range(1, 4):
        hilo = threading.Thread(target=simular_usuario, args=(i,))
        hilos.append(hilo)

    # Cronometramos el inicio global
    tiempo_global_inicio = time.time()

    # Lanzamos todos los hilos simultáneamente
    for hilo in hilos:
        hilo.start()

    # Esperamos a que los 3 terminen
    for hilo in hilos:
        hilo.join()

    tiempo_global_fin = time.time()
    print(f"-----------------------------------------------------------------")
    print(f"Tiempo total de la prueba concurrente: {tiempo_global_fin - tiempo_global_inicio:.4f} segundos")

if __name__ == "__main__":
    ejecutar_prueba_carga()