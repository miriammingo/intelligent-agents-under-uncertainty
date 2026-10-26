import random

FILAS = 7
COLUMNAS = 6
N_ISLAS = 2
# GAMMA define cuánto importan las recompensas futuras frente a las inmediatas, como valoramos bastante las recompensas futuras:
GAMMA = 0.9
# THETA es el criterio de convergencia. Cuando el cambio máximo en cualquier valor de estado (delta) sea menor que THETA, 
# detendremos las iteraciones porque habrá convergido
THETA = 0.001
SEGURO = "R"
ISLA = "I"
SALIDA = "E"
WILLARD_KURTZ = "CWCK"
PEZ = "PEZ"
PIRANIA = "PIR"
ACCIONES = ["up", "down", "left", "right"]

def crear_mapa() ->list:
    """
    Crea el mapa del río con casillas seguras, islas, peces, piraña, 
    salida y la posición inicial de Willard y Kurtz.
    Takes:
    - None
    Returns:
    - list: matriz FILAS x COLUMNAS con los elementos del mapa
    """
    mapa = []
    # Inicialmente, creamos una matriz de tamaño FILASxCOLUMNAS donde todas las casillas son seguras (R)
    for i in range(FILAS):
        fila = []
        for j in range(COLUMNAS):
            fila.append(SEGURO)
        mapa.append(fila)
    
    # Quitamos las R de la primera y la última columnas
    for i in range(FILAS):
        if mapa[i][0] == SEGURO:
            mapa[i][0] = " "
        if mapa[i][COLUMNAS-1] == SEGURO:
            mapa[i][COLUMNAS-1] = " "
    
    # Colocamos la casilla de salida (E) en la última columna
    mapa[random.randint(0, FILAS-1)][COLUMNAS - 1] = SALIDA
    mapa[0][0] = WILLARD_KURTZ  # Colocamos a Willard y Kurtz en la casilla inicial (0,0)

    colocadas = 0
    while colocadas < N_ISLAS:
        i = random.randint(1, FILAS - 2)  # Evitamos que no esté ni en la primera ni en la última fila
        j = random.randint(0, COLUMNAS - 1)
        if mapa[i][j] in [SEGURO, " "]:  # Nos aseguramos de que esa casilla esté libre
            mapa[i][j] = ISLA
            colocadas += 1
    
    # MODIFICACIÓN: Colocamos 2 peces que proporcionarán una recompensa positiva
    colocados = 0
    while colocados < 2:
        i = random.randint(1, FILAS - 2)
        j = random.randint(1, COLUMNAS - 2)
        if mapa[i][j] == SEGURO:
            mapa[i][j] = PEZ
            colocados += 1

    # Colocamos 1 piraña que proporcionará una penalización
    colocado = False
    while not colocado:
        i = random.randint(1, FILAS - 2)
        j = random.randint(1, COLUMNAS - 2)
        if mapa[i][j] == SEGURO:
            mapa[i][j] = PIRANIA
            colocado = True

    return mapa

def imprimir_mapa(mapa:list):
    """
    Imprime el mapa del río
    Takes:
    - mapa: list, matriz con el estado de cada celda
    """
    for fila in mapa:
        linea = "|"
        for celda in fila:
            linea += f" {celda:^4} ||"  # Forzamos a que el ancho sean 4 caracteres y a que estén centrados (^)
        print(linea[:-1]) # Quitamos el último "|"
    print("\nLEYENDA:")
    print("  |CWCK|: Capitán Willard y Coronel Kurtz")
    print("  | R |: Casilla de río segura")
    print("  | I |: Isla/peligro")
    print("  | E |: Salida")
    print("  |PEZ|: Pez (+10)")
    print("  |PIR|: Piraña (-20)")
    print("  |   |: Orilla sin corriente")

def moverse(i:int, j:int, accion:str) ->tuple:
    """
    Calcula la nueva posición después de realizar una acción
    Takes:
    - i: int, fila actual
    - j: int, columna actual
    - accion: str, acción a realizar
    Returns:
    - tuple: nueva posición
    """
    if accion == "up":
        return i - 1, j
    if accion == "down":
        return i + 1, j
    if accion == "left":
        return i, j - 1
    if accion == "right":
        return i, j + 1
    return i, j  # (sería la acción "stay")

def river_strength() ->list:
    """
    Genera la fuerza de la corriente para cada columna del río
    Takes:
    - None
    Returns:
    - list: fuerza de la corriente por columna
    """
    corriente = []
    for j in range(COLUMNAS):
        if j == 0 or j == COLUMNAS - 1:  # Si está en los bordes no hay corriente
            corriente.append(0.0)
        else:
            corriente.append(round(random.uniform(0.06, 0.94), 1))  # Valor aleatorio entre 0.06 y 0.94 con distribución uniforme
    return corriente

def valido(i:int, j:int, mapa:list) ->bool:
    """
    Comprueba si una posición está dentro de los límites del mapa y no coincide con una isla
    Takes:
    - i: int, fila
    - j: int, columna
    - mapa: list, matriz del entorno
    Returns:
    - bool: True si la posición es válida, False si no
    """
    # Si la casilla está fuera de los límites del río o coincide con una isla, la probabilidad de moverse a ella
    # es nula y el agente permanece en su posición actual, la función devolverá False
    if i < 0 or i >= FILAS or j < 0 or j >= COLUMNAS:
        return False
    if mapa[i][j] == ISLA:
        return False
    return True

def value_iteration(mapa:list, corriente:list) ->dict:
    """
    Calcula los valores de los estados usando Value Iteration
    Takes:
    - mapa: list, matriz del entorno
    - corriente: list, fuerza de la corriente por columna
    Returns:
    - dict: V[(i,j)] con el valor óptimo de cada estado
    """
    # Inicializamos todos los estados con valor 0
    V = {(i, j): 0.0 for i in range(FILAS) for j in range(COLUMNAS)}
    bucle = True
    while bucle:
        delta = 0
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if mapa[i][j] not in [SALIDA, ISLA]:  # No evaluamos ni la salida ni las islas

                    mejor_valor = -float('inf')  # (lo inicializamos a un valor muy bajo)
                    
                    for accion in ACCIONES:  
                        # Calculamos la expectativa de recompensa de cada acción desde el estado actual aplicando la ec. de Bellman
                        valor = 0.0

                        if accion == "down":
                            ni, nj = moverse(i, j, accion)
                            if valido(ni, nj, mapa):
                                # Según donde nos encontremos obtenemos distintas recompensas 
                                if mapa[ni][nj] == SALIDA:
                                    recompensa = 100
                                elif mapa[ni][nj] == PEZ:
                                    recompensa = 10
                                elif mapa[ni][nj] == PIRANIA:
                                    recompensa = -20
                                else:
                                    recompensa = -1

                                valor += recompensa + GAMMA * V[(ni, nj)]
                            else:
                                valor += -1 + GAMMA * V[(i, j)]  # No nos movemos
                        else:
                            p_down = corriente[j]  # Probabilidad de ser arrastrado por la corriente hacia abajo
                            p_dir = 1 - p_down  # Probabilidad de que vayamos a donde queremos

                            # Probabilidad de moverse a la casilla deseada
                            ni, nj = moverse(i, j, accion)
                            if valido(ni, nj, mapa):
                                if mapa[ni][nj] == SALIDA:
                                    recompensa = 100
                                elif mapa[ni][nj] == PEZ:
                                    recompensa = 5
                                elif mapa[ni][nj] == PIRANIA:
                                    recompensa = -10
                                else:
                                    recompensa = -1

                                valor += p_dir * (recompensa + GAMMA * V[(ni, nj)])
                            else:
                                valor += p_dir * (-1 + GAMMA * V[(i, j)])

                            # Probabilidad de ser arrastrado por la corriente hacia abajo
                            di, dj = moverse(i, j, "down")
                            if valido(di, dj, mapa):
                                if mapa[di][dj] == SALIDA:
                                    r_down = 100
                                elif mapa[di][dj] == PEZ:
                                    r_down = 5
                                elif mapa[di][dj] == PIRANIA:
                                    r_down = -10
                                else:
                                    r_down = -1

                                valor += p_down * (r_down + GAMMA * V[(di, dj)])
                            else:
                                valor += p_down * (-1 + GAMMA * V[(i, j)])


                        if valor > mejor_valor: # Vamos cogiendo el mejor valor engre todas las acciones posibles
                            mejor_valor = valor

                     # Calculamos cuánto ha cambiado el valor del estado (i,j) respecto a la iteración anterior
                     # (Esto nos indica si los valores todavía están cambiando mucho o si ya se han estabilizado)
                    delta = max(delta, abs(V[(i, j)] - mejor_valor)) 
                    V[(i, j)] = mejor_valor

        # Condición de parada: si el cambio máximo en todo el mapa es menor que THETA, es que hemos convergido y salimos del bucle
        if delta < THETA:
            bucle = False

    return V

def extraer_politica(V:dict, mapa:list, corriente:list) ->dict:
    """ Recorre todos los estados y, usando los valores V[(i,j)] calculados antes, elige la 
    acción que produce ese valor máximo
    Takes:
    - V: dict, valores óptimos por cada estado
    - mapa: list, matriz del entorno
    - corriente: list, fuerza de la corriente por columna
    Returns:
    - dict: política óptima con la acción a realizar en cada estado
    """
    politica = {}  # Iremos guardando los movimientos que debe realizar
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if mapa[i][j] != ISLA:  # No evaluamos las islas
                mejor_valor = -float('inf')   # (lo inicializamos a un valor muy bajo)
                mejor_accion = None

                for accion in ACCIONES:  # Probamos con todas las acciones
                    valor = 0.0
                    p_down = corriente[j]
                    p_dir = 1 - p_down
                    ni, nj = moverse(i, j, accion)
                    if valido(ni, nj, mapa):  # Descartamos las acciones inválidas
                        recompensa = 0
                        if mapa[ni][nj] == SALIDA:
                            recompensa = 100
                        elif mapa[ni][nj] == PEZ:
                            recompensa = 5
                        elif mapa[ni][nj] == PIRANIA:
                            recompensa = -10
                        else:
                            recompensa = -1
                        valor += p_dir * (recompensa + GAMMA * V[(ni, nj)])
                    else:
                        valor += p_dir * (-1 + GAMMA * V[(i, j)])
                    
                    # Acción down o corriente hacia abajo
                    di, dj = moverse(i, j, "down")
                    if valido(di, dj, mapa):
                        if mapa[di][dj] == SALIDA:
                            r_down = 100
                        elif mapa[di][dj] == PEZ:
                            r_down = 5
                        elif mapa[di][dj] == PIRANIA:
                            r_down = -10
                        else:
                            r_down = -1
                        valor += p_down * (r_down + GAMMA * V[(di, dj)])
                    else:
                        valor += p_down * (-1 + GAMMA * V[(i, j)])
                        
                    if valor > mejor_valor:  # Vamos seleccionando la acción que nos proporcioné el mejor valor
                        mejor_valor = valor
                        mejor_accion = accion
                
                if mapa[i][j] == SALIDA:
                    politica[(i,j)] = None
                else:
                    politica[(i, j)] = mejor_accion  # Como politica, elegiremos la acción óptima (mayor valor)

    return politica

def simular_partida(mapa, politica, corriente):
    """
    Simula una partida siguiendo la política óptima y mostrando cada movimiento
    Takes:
    - mapa: list, matriz del entorno
    - politica: dict, acciones óptimas por estado
    - corriente: list, fuerza de la corriente por columna
    """
    i, j = 0, 0  # Empezaremos en la casilla (0,0)
    pasos = 0  # Contaremos los pasos para establecer un límite y que no se formen bucles infinitos (por si acaso)
    terminado = False  # (para controlar el flujo del juego)
    print("\n-----------------------------")
    print("Comienza la partida")
    print("-----------------------------")

    while pasos < 500 and not terminado:
        accion = politica.get((i,j))
        if accion is None:
            terminado = True  # Han llegado a la salida
            
        else:
            # Vamos mostrando cómo el capitán toma decisiones en cada situación
            print(f"\nPaso {pasos}: posición ({i},{j}), acción elegida: {accion}")

            # Para simular un suceso probabilístico utilizamos random.random(), que genera un número aleatorio uniforme entre 0 y 1
            # Si es menor que la fuerza de la corriente, la corriente les arrastra y viceversa
            if accion != "down" and random.random() < corriente[j]:
                accion_real = "down"
                print("\n-----------------------------------------------------")
                print("¡Ohhh, la corriente arrastra a Willard y a Kurtz hacia abajo!\n")
            else:
                accion_real = accion

            ni, nj = moverse(i, j, accion_real)

            if valido(ni, nj, mapa):
                contenido = mapa[ni][nj]  # Guardamos lo que había antes
                # Quitamos la posición anterior
                if j != 0 and j != COLUMNAS-1:
                    mapa[i][j] = SEGURO   
                else:
                    mapa[i][j] = " "  # Si está en la primera o última columnas lo cambiamos a una casilla vacía
                i, j = ni, nj

                if contenido == PEZ:
                    print("\n-----------------------------------------------------")
                    print("Willard y Kurtz han pescado un pez (+5)\n")
                elif contenido == PIRANIA:
                    print("\n-----------------------------------------------------")
                    print("¡A Willard y a Kurtz les ha mordido una piraña! (-10)\n")
                
                mapa[i][j] = WILLARD_KURTZ  # Les movemos de casilla

            else:
                print("\n-----------------------------------------------------")
                print("Movimiento no válido, Willard y Kurtz permanecen en su posición actual\n")

            imprimir_mapa(mapa)
            pasos += 1

    if terminado:
        print("\n¡Willard y Kurtz han llegado por fin a la salida!")
    else:
        print("\nWillard y Kurtz no han conseguido llegar a la salida")


if __name__ == "__main__":
    mapa = crear_mapa()
    corriente = river_strength()

    print("La corriente por columnas es:", corriente)
    imprimir_mapa(mapa)

    V = value_iteration(mapa, corriente)
    politica = extraer_politica(V, mapa, corriente)

    simular_partida(mapa, politica, corriente)

