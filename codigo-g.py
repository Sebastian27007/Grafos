#!/usr/bin/env python3
# coding: utf-8

"""
Solución Tarea TSP - Comparación Exhaustiva vs Heurística
---------------------------------------------------------
1. Calcula matriz de distancias reales (Haversine).
2. Ejecuta Búsqueda Exhaustiva (Óptimo Global).
3. Ejecuta Heurística Vecino Más Cercano (Aproximación).
4. Muestra métricas de comparación (GAP y Tiempo).
5. Genera un gráfico estático comparativo lado a lado.
"""

import math
import time
from itertools import permutations
import matplotlib.pyplot as plt

# =============================================================================
# 1. DATOS DE ENTRADA
# =============================================================================
CIUDADES = [
    ("Santiago", -33.447487, -70.673676),
    ("Valparaíso", -33.047237, -71.612686),
    ("Viña del Mar", -33.015347, -71.550026),
    ("Concepción", -36.827000, -73.049800),
    ("Temuco", -38.736280, -72.597380),
    ("Antofagasta", -23.650940, -70.397520),
    ("Iquique", -20.213260, -70.150270),
]

# =============================================================================
# 2. FUNCIONES MATEMÁTICAS
# =============================================================================

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos coordenadas (Fórmula Haversine)."""
    RADIO_TIERRA_KM = 6371.0
    
    # Conversión a radianes (CORREGIDO)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return RADIO_TIERRA_KM * c

def generar_matriz_distancias(ciudades):
    """Crea matriz de distancias NxN."""
    n = len(ciudades)
    matriz = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matriz[i][j] = calcular_distancia_haversine(
                    ciudades[i][1], ciudades[i][2],
                    ciudades[j][1], ciudades[j][2]
                )
    return matriz

def obtener_costo_ruta(ruta, matriz_distancias):
    """Suma distancia total de ruta + retorno al inicio."""
    costo = 0.0
    n = len(ruta)
    for i in range(n - 1):
        costo += matriz_distancias[ruta[i]][ruta[i+1]]
    costo += matriz_distancias[ruta[-1]][ruta[0]]
    return costo

# =============================================================================
# 3. ALGORITMOS
# =============================================================================

def busqueda_exhaustiva(matriz_distancias, inicio=0):
    """Algoritmo Exacto: Prueba TODAS las permutaciones (Lento pero seguro)."""
    n = len(matriz_distancias)
    ciudades_restantes = [i for i in range(n) if i != inicio]
    
    mejor_ruta = []
    minima_distancia = float('inf')
    
    t_inicio = time.perf_counter()
    
    for perm in permutations(ciudades_restantes):
        ruta_actual = [inicio] + list(perm)
        d = obtener_costo_ruta(ruta_actual, matriz_distancias)
        if d < minima_distancia:
            minima_distancia = d
            mejor_ruta = ruta_actual
            
    duracion = time.perf_counter() - t_inicio
    return mejor_ruta, minima_distancia, duracion

def vecino_mas_cercano(matriz_distancias, inicio=0):
    """Algoritmo Heurístico: Elige siempre la ciudad más cercana (Rápido)."""
    n = len(matriz_distancias)
    ruta = [inicio]
    por_visitar = set(range(n))
    por_visitar.remove(inicio)
    actual = inicio
    
    t_inicio = time.perf_counter()
    
    while por_visitar:
        siguiente = min(por_visitar, key=lambda c: matriz_distancias[actual][c])
        ruta.append(siguiente)
        por_visitar.remove(siguiente)
        actual = siguiente
        
    duracion = time.perf_counter() - t_inicio
    distancia = obtener_costo_ruta(ruta, matriz_distancias)
    return ruta, distancia, duracion

# =============================================================================
# 4. VISUALIZACIÓN COMPARATIVA (SIN ANIMACIÓN)
# =============================================================================

def graficar_comparacion_lado_a_lado(ciudades, ruta_ex, dist_ex, ruta_nn, dist_nn):
    """Genera una figura con dos mapas para comparar visualmente las soluciones."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Coordenadas generales
    lons = [c[2] for c in ciudades]
    lats = [c[1] for c in ciudades]
    
    # Función auxiliar para dibujar en un eje específico
    def dibujar_en_eje(ax, ruta, titulo, color_linea):
        # Fondo
        ax.scatter(lons, lats, c='gray', alpha=0.5)
        
        # Ruta cerrada
        ruta_cerrada = ruta + [ruta[0]]
        xs = [ciudades[i][2] for i in ruta_cerrada]
        ys = [ciudades[i][1] for i in ruta_cerrada]
        
        # Trazado
        ax.plot(xs, ys, 'o-', color=color_linea, linewidth=2, label='Ruta')
        ax.plot(xs[0], ys[0], 'D', color='green', markersize=8, label='Inicio')
        
        # Nombres
        for i, (nom, la, lo) in enumerate(ciudades):
            ax.annotate(nom, (lo, la), xytext=(3,3), textcoords='offset points', fontsize=8)
            
        ax.set_title(titulo)
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud")
        ax.grid(True, linestyle='--', alpha=0.6)

    # 1. Gráfico Exhaustivo
    dibujar_en_eje(ax1, ruta_ex, f"ÓPTIMO (Exhaustiva)\nDistancia: {dist_ex:.2f} km", 'blue')
    
    # 2. Gráfico Heurístico
    dibujar_en_eje(ax2, ruta_nn, f"APROXIMACIÓN (Vecino Más Cercano)\nDistancia: {dist_nn:.2f} km", 'red')
    
    plt.tight_layout()
    print("Mostrando gráfico comparativo...")
    plt.show()

# =============================================================================
# 5. MAIN
# =============================================================================

def main():
    print("=== COMPARACIÓN TSP: EXHAUSTIVA vs HEURÍSTICA ===\n")
    
    # 1. Preparar datos
    matriz = generar_matriz_distancias(CIUDADES)
    
    # 2. Ejecutar Exhaustiva
    print("Calculando Óptimo (Exhaustiva)... espere un momento.")
    ruta_ex, dist_ex, tiempo_ex = busqueda_exhaustiva(matriz)
    
    # 3. Ejecutar Heurística
    print("Calculando Heurística (Vecino Más Cercano)...")
    ruta_nn, dist_nn, tiempo_nn = vecino_mas_cercano(matriz)
    
    # 4. Reporte de Texto
    gap = ((dist_nn - dist_ex) / dist_ex) * 100.0
    aceleracion = tiempo_ex / tiempo_nn if tiempo_nn > 0 else 0
    
    print("\n--- RESULTADOS ---")
    print(f"Distancia Óptima:     {dist_ex:.2f} km  (Tiempo: {tiempo_ex:.6f} s)")
    print(f"Distancia Heurística: {dist_nn:.2f} km  (Tiempo: {tiempo_nn:.6f} s)")
    print(f"\nGAP de Error: {gap:.2f}%")
    print(f"Velocidad: La heurística es {aceleracion:.1f} veces más rápida.")
    
    # 5. Gráfico Final
    graficar_comparacion_lado_a_lado(CIUDADES, ruta_ex, dist_ex, ruta_nn, dist_nn)

if __name__ == "__main__":
    main()