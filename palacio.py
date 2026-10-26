import random

N = 6
UMBRAL_RIESGO = 0.2
VACIO = []
WILLARD = "CW"
KURTZ = "CK"
SOLDADO = "M"
FUEGO = "F"
PINCHOS = "P"
DARDOS = "D"
TRAMPAS = [FUEGO, PINCHOS, DARDOS]
SALIDA = "S"
DIRECCIONES = {"W": (-1, 0), "A": (0, -1), "S": (1, 0), "D": (0, 1)}
ACCIONES = {"W": "Arriba", "A": "Izquierda", "S": "Abajo", "D": "Derecha"}

class Palacio:
    def __init__(self):
        self.mapa = [[[] for _ in range(N)] for _ in range(N)]  # Creamos el mapa
        self.pos_willard = (0, 0)  # La pos inicial de Willard siempre es (0,0)
        # El resto de posiciones quedan por determinar
        self.pos_kurtz = None
        self.pos_soldado = None
        self.pos_trampas = {FUEGO: None, PINCHOS: None, DARDOS: None}
        self.pos_salida = None
        
        self.colocar_willard()
        self.colocar_trampas()
        self.colocar_m_ck_s()

    def colocar_willard(self):
        """
        Coloca a Willard en la posición inicial del mapa
        """
        self.mapa[self.pos_willard[0]][self.pos_willard[1]].append(WILLARD)  # Colocamos a Willard

    def posiciones_libres(self) ->list:
        """
        Devuelve una lista de posiciones libres (sin Willard) 
        Takes:
        - None
        Returns:
        - list: lista de tuplas con coordenadas libres
        """
        libres = []
        for i in range(N):
            for j in range(N):
                if (i, j) != self.pos_willard:
                    libres.append((i, j))
        return libres

    def colocar_trampas(self):
        """
        Coloca aleatoriamente las trampas (Fuego, Pinchos, Dardos) en el mapa
        """
        posiciones = self.posiciones_libres()

        for trampa in TRAMPAS:
            pos = random.choice(posiciones)
            self.mapa[pos[0]][pos[1]].append(trampa)
            self.pos_trampas[trampa] = pos
            # NO eliminamos la posición porque pueden coincidir

    def colocar_m_ck_s(self):
        """
        Coloca al soldado, al Coronel Kurtz y la salida en posiciones
        libres del mapa (sin trampas)
        """
        posiciones = self.posiciones_libres()

        # Quitamos posiciones con trampas
        posiciones_sin_trampas = []
        for i, j in posiciones:
            hay_trampa = False
            for t in TRAMPAS:
                if t in self.mapa[i][j]:
                    hay_trampa = True
            if not hay_trampa:
                posiciones_sin_trampas.append((i, j))

        # Colocamos al soldado
        self.pos_soldado = random.choice(posiciones_sin_trampas)
        self.mapa[self.pos_soldado[0]][self.pos_soldado[1]].append(SOLDADO)

        # Colocamos al Coronel Kurtz
        self.pos_kurtz = random.choice(posiciones_sin_trampas)
        self.mapa[self.pos_kurtz[0]][self.pos_kurtz[1]].append(KURTZ)

        # Colocamos la salida
        self.pos_salida = random.choice(posiciones_sin_trampas)
        self.mapa[self.pos_salida[0]][self.pos_salida[1]].append(SALIDA)

    def perceptos(self, pos=None, grito=False) ->list:
        """
        Calcula perceptos de una posición dada (trampas, soldado, salida, paredes y grito)
        Takes:
        - pos: tuple, coordenadas (i,j) de la celda. Si None, se usa la posición de Willard.
        - grito: bool, indica si se ha escuchado un grito.
        Returns:
        - list: los perceptos observados
        """
        if pos is None:
            pos = self.pos_willard
        i,j = pos
        eF = eP = eD = eM = eS = False

        # Definimos las condiciones a cumplir cuando haya alguna pared
        pared_arriba = int(i==0)
        pared_abajo = int(i==N-1)
        pared_izqda = int(j==0)
        pared_dcha = int(j==N-1)

        # Definimos los preceptos para cada celda adyacente
        adyacentes = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        for x,y in adyacentes:
            if 0<=x<N and 0<=y<N:  # (dentro de los márgenes del tablero)
                if FUEGO in self.mapa[x][y]:  # (lo miramos de esa manera porque son listas)
                    eF = True
                if PINCHOS in self.mapa[x][y]:
                    eP = True
                if DARDOS in self.mapa[x][y]:
                    eD = True
                if SOLDADO in self.mapa[x][y]:
                    eM = True
                if SALIDA in self.mapa[x][y]:
                    eS = True

        return [eF, eP, eD, eM, eS, pared_arriba, pared_abajo, pared_izqda, pared_dcha, int(grito)]

class Willard:
    def __init__(self, palacio):
        self.palacio = palacio
        self.pos = palacio.pos_willard  # Comienza en la posición inicial de Willard
        
        # Creamos una matriz de booleanos para ir indicando qué celdas hemos visitado y cuáles no
        self.visitados = [[False for _ in range(N)] for _ in range(N)]
        self.visitados[self.pos[0]][self.pos[1]] = True  # Marcamos la celda inicial como visitada, pues es donde se encuentra Willard
        
        self.granada_disponible = True
        self.encontrado_kurtz = False
        self.vivo = True  # Para controlar el flujo del juego
        
        # Inicializamos los mapas de probabilidades de cada elemento, utilizando lo que sabemos a priori
        self.prob_F = prior_uniforme(self.pos)
        self.prob_P = prior_uniforme(self.pos)
        self.prob_D = prior_uniforme(self.pos)
        self.prob_M = prior_uniforme(self.pos)
        self.prob_S = prior_uniforme(self.pos)
        self.prob_CK = prior_uniforme(self.pos)

        eF, eP, eD, eM, eS, *_ = self.palacio.perceptos(self.pos)
        # Actualizamos las probabilidades según los preceptos que percibamos
        self.prob_F = actualizar_probabilidad(self.prob_F, eF, self.pos)
        self.prob_P = actualizar_probabilidad(self.prob_P, eP, self.pos)
        self.prob_D = actualizar_probabilidad(self.prob_D, eD, self.pos)
        self.prob_M = actualizar_probabilidad(self.prob_M, eM, self.pos)
        self.prob_S = actualizar_probabilidad(self.prob_S, eS, self.pos)

    def imprimir_heatmap(self, mapa, titulo:str):
        """
        Imprime un mapa de probabilidades con la posición actual de Willard
        Takes:
        - mapa: lista de listas de floats
        - titulo: str, título del heatmap
        """
        print("\n", titulo)
        for i in range(N):
            fila = ""
            for j in range(N):
                if (i, j) == self.pos:
                    fila += " CW  "
                else:
                    fila += f"{mapa[i][j]:.2f} "
            print(fila)

    def mapa_trampas(self) ->list:
        """
        Calcula un mapa de probabilidades acumuladas de todas las trampas
        Takes:
        - None
        Returns:
        - list: matriz con probabilidades de trampas
        """
        mapa = [[0.0 for _ in range(N)] for _ in range(N)]
        for i in range(N):
            for j in range(N):
                # Suma de las probabilidades de las 3 trampas
                mapa[i][j] = self.prob_F[i][j] + self.prob_P[i][j] + self.prob_D[i][j]
        return mapa

    def moverse(self, direccion):
        """
        Mueve a Willard en la dirección indicada actualizando la posición, visitados y verificando peligros u objetivos
        Takes:
        - direccion: str, una entre 'W', 'A', 'S' o 'D'
        """
        # Cogemos el valor de la dirección deseada mediante "get()", si no lo encuentra en DIRECCIONES no se mueve ((0,0))
        di,dj = DIRECCIONES.get(direccion.upper(), (0,0))  
        ni,nj = self.pos[0]+di, self.pos[1]+dj  # Le sumamos el valor a nuestra posición actual para movernos a donde queremos

        if 0<=ni<N and 0<=nj<N:  # (comprobamos que no se salga del palacio)
            self.pos = (ni,nj)
            self.visitados[ni][nj] = True
            celda = self.palacio.mapa[ni][nj]

            if FUEGO in celda or PINCHOS in celda or DARDOS in celda:
                print("\n---------------------------------------")
                print("¡Has caído en una trampa! Fin del juego")
                self.vivo = False

            if SOLDADO in celda:
                print("\n---------------------------------------")
                print("¡El soldado enemigo te atrapó! Fin del juego")
                self.vivo = False

            if KURTZ in celda:
                print("\n---------------------------------------")
                print("¡Encontraste al Coronel Kurtz! Es hora de salir del palacio")
                self.encontrado_kurtz = True

            elif SALIDA in celda and self.encontrado_kurtz:  # Solo sale si ha encontrado a Kurtz previamente
                print("\n---------------------------------------")
                print("¡Enhorabuena! Has completado la misión y salido del palacio con Kurtz")
                self.vivo = False  # Fin del juego

            # Actualizamos
            eF, eP, eD, eM, eS, *_ = self.palacio.perceptos(self.pos)
            self.prob_F = actualizar_probabilidad(self.prob_F, eF, self.pos)
            self.prob_P = actualizar_probabilidad(self.prob_P, eP, self.pos)
            self.prob_D = actualizar_probabilidad(self.prob_D, eD, self.pos)
            self.prob_M = actualizar_probabilidad(self.prob_M, eM, self.pos)
            self.prob_S = actualizar_probabilidad(self.prob_S, eS, self.pos)
    
        else:  # Si se sale, es porque hay una pared
            print("No puedes moverte en esa dirección porque hay una pared")
    
    def arrojar_granada(self, direccion):
        """
        Lanza una granada a la celda adyacente en la dirección indicada, eliminando al soldado si está 
        Takes:
        - direccion: str, una de 'W', 'A', 'S' o 'D'
        """
        if not self.granada_disponible:
            print("No te quedan granadas disponibles")
            return
        di, dj = DIRECCIONES.get(direccion.upper(), (0,0))
        ni, nj = self.pos[0] + di, self.pos[1] + dj

        if 0<=ni<N and 0<=nj<N:  # Nos aseguramos de que esté dentro de la región del palacio
            celda = self.palacio.mapa[ni][nj]

            if SOLDADO in celda:
                print("¡Has eliminado al soldado enemigo con la granada!")
                celda.remove(SOLDADO)  # Como hemos eliminado al soldado la celda pasa a estar vacía
            else:
                print("La granada no afectó a nada")
            self.granada_disponible = False
        else:
            print("No puedes arrojar la granada fuera del palacio")

    def riesgo_celda(self, i:int, j:int) ->float:  # Riesgo promedio de la celda actual (suma de todos)
        """
        Calcula el riesgo acumulado de una celda sumando las probabilidades de trampas y soldado
        Takes:
        - i: int, fila
        - j: int, columna
        Returns:
        - float: riesgo total de la celda
        """
        return self.prob_F[i][j] + self.prob_P[i][j] + self.prob_D[i][j] + self.prob_M[i][j]

    def heuristica_riesgo(self, pos:tuple, objetivo:tuple) ->float:
        """
        Calcula la heurística de riesgo para A* usando la distancia Manhattan hasta el objetivo
        Takes:
        - pos: tuple, posición actual
        - objetivo: tuple, posición objetivo
        Returns:
        - float: valor heurístico
        """
        # Utilizamos como heurística A* = distancia Manhattan
        i, j = pos
        oi, oj = objetivo

        return abs(i-oi) + abs(j-oj)  # Devolvemos la distancia Manhattan
    
    def busqueda_informada(self, objetivo:tuple) ->list: 
        """
        Busca un camino hasta el objetivo usando el algoritmo A*
        Takes:
        - objetivo: tuple, posición destino
        Returns:
        - list: lista de posiciones del camino seguro o None si no existe
        """ 
        # Aplicamos el algoritmo de búsqueda informada A* donde g(n) es el riesgo acumulado de las celdas visitadas
        # Nuestro objetivo será encontrar a Kurtz o la salida (en caso de haberle encontrado ya)
        inicio = self.pos

        # Creamos una lista para ir guardando los nodos con la siguiente estructura:
        # nodo = {posicion, g: coste acumulado, h: heurística (estimación al objetivo), f: g + h, padre: para poderreconstruir el camino}
        lst_nodos = [{"pos":inicio, "g":0.0, "h":self.heuristica_riesgo(inicio,objetivo), "f":self.heuristica_riesgo(inicio,objetivo), "padre":None}]
        visitados = set()  # (para guardar los nodos que ya hayamos viistado)

        step = 0  # (Iremos imprimiendo la info paso a paso)

        while lst_nodos:  # (mientras queden nodos por explorar)
            print(f"\nSTEP {step}")
        
            print("Frontier:")
            for n in lst_nodos:
                print(f"  Pos:{n['pos']} g:{n['g']:.2f} h:{n['h']} f:{n['f']:.2f}")  # (con dos decimales9)

            # Buscamos el nodo con menor f
            idx_min = 0
            for i in range(len(lst_nodos)):
                if lst_nodos[i]["f"] < lst_nodos[idx_min]["f"]:
                    idx_min = i
            nodo_actual = lst_nodos.pop(idx_min)
            pos_actual = nodo_actual["pos"]

            print("Removed node:", pos_actual)

            if pos_actual == objetivo:  # Si resulta que hemos llegado al objetivo, reconstruimos el camino hasta él
                camino = []
                n = nodo_actual
                while n is not None:  # Vamos recogiendo los padres de los nodos en una lista y le damos la vuelta
                    camino.append(n["pos"])
                    n = n["padre"]
                camino.reverse()
                return camino

            visitados.add(pos_actual)  # (aún no hemos llegado al objetivo)

            acciones = []
            transiciones = []

            i, j = pos_actual
            for di, dj, accion in [(-1,0,"Arriba"), (1,0,"Abajo"), (0,-1,"Izquierda"), (0,1,"Derecha")]:  # Exploramos las posiciones adyacentes
                ni, nj = i + di, j + dj
                if 0 <= ni < N and 0 <= nj < N:  # (que estén dentro del rango)
                    vecino = (ni, nj)
                    if vecino not in visitados:
                        acciones.append(accion)
                        # Actualizamos los costes
                        g_nuevo = nodo_actual["g"] + self.riesgo_celda(ni, nj)
                        h_nuevo = self.heuristica_riesgo(vecino, objetivo)
                        f_nuevo = g_nuevo + h_nuevo

                        transiciones.append({"estado": vecino, "g": round(g_nuevo, 2), "h": h_nuevo, "f": round(f_nuevo, 2)})

                        # Si ya está en la lista de nodos y tiene menor f (mejor camino), no lo añadimos
                        ya_esta = False
                        for n in lst_nodos:
                            if n["pos"] == vecino and n["f"] <= f_nuevo:
                                ya_esta = True

                        if not ya_esta:
                            lst_nodos.append({"pos": vecino, "g": g_nuevo, "h": h_nuevo, "f": f_nuevo, "padre": nodo_actual})
            
            print("Actions:", acciones)

            print("Transitions added:")
            for t in transiciones:
                print(f"  -> {t['estado']} g:{t['g']} h:{t['h']} f:{t['f']}")

            print("Explored:", list(visitados))
            print("-----------------------------")

            step += 1

        return None  # No hay camino seguro
    
    def planificar_mision(self) ->list:
        """
        Planea la misión:
            1. Encontrar el camino hasta Kurtz
            2. Encontrar el camino desde Kurtz hasta la salida
        Takes:
        - None
        Returns:
        - list: camino completo de posiciones o None si no hay camino seguro
        """
        print("Planeando camino hasta Kurtz...")
        camino_kurtz = self.busqueda_informada(self.palacio.pos_kurtz)
        if camino_kurtz is None:
            print("No hay ningún camino seguro hasta Kurtz")
            return

        print("Camino hasta Kurtz encontrado:", camino_kurtz)

        # Actualizamos la posición de Willard como si estuviese recorriendo el camino 
        for pos in camino_kurtz[1:]:
            self.pos = pos
            self.visitados[pos[0]][pos[1]] = True

        self.encontrado_kurtz = True

        print("\nPlaneando camino hasta la salida...")
        camino_salida = self.busqueda_informada(self.palacio.pos_salida)
        if camino_salida is None:
            print("No hay ningún camino seguro hasta la salida")
            return

        print("Camino hasta la salida encontrado:", camino_salida)
        
        return camino_kurtz + camino_salida[1:]  # Devolvemos el camino completo evitando repetir la posición de Kurtz


def prior_uniforme(pos_inicial:tuple) ->list:
    """
    Crea una matriz de probabilidades uniformes para un elemento, excluyendo la posición inicial (segura)
    Takes:
    - pos_inicial: tuple, posición inicial
    Returns:
    - list: matriz de probabilidades uniformes
    """
    prob = [[0.0 for _ in range(N)] for _ in range(N)]  # Creamos un matriz para ir guardando los priors

    for i in range(N):
        for j in range(N):
            if (i, j) != pos_inicial:
                # Como N*N celdas y sabemos que una no contiene nada peligroso (la inicial), el total es N*N - 1
                prob[i][j] = 1 / (N*N - 1)  # (aplicamos la fórmula)
    return prob

def actualizar_probabilidad(prob:list, percepto:bool, pos:tuple) ->list:
    """
    Actualiza la matriz de probabilidades a posteriori según los perceptos que 
    se observen en la posición
    Takes:
    - prob: list, matriz de probabilidades a priori
    - percepto: bool, si se percibe el peligro en la posición
    - pos: tuple, posición actual
    Returns:
    - list: matriz de probabilidades actualizadas
    """
    i, j = pos
    nueva = [[0.0 for _ in range(N)] for _ in range(N)]  # Nueva matriz de probabilidades
    total = 0

    for hi in range(N):
        for hj in range(N):
            # Primero comprobamos si (hi, hj) está en rango Manhattan <= 1 respecto a (i,j)
            if abs(i - hi) + abs(j - hj) <= 1:
                rango = True
            else:
                rango = False

            # Aplicamos la función de verosimilitud dada
            if rango and percepto: 
                p_e = 1
            elif not rango and not percepto:  # Si no estamos en el rango y no percibimos ningun percepto, es normal
                p_e = 1
            else:
                p_e = 0

            # Calculamos la probabilidad a posteriori
            nueva[hi][hj] = p_e * prob[hi][hj]
            total += nueva[hi][hj]

    # Normalizamos las probabilidades para que la suma sea 1
    if total > 0:
        for hi in range(N):
            for hj in range(N):
                nueva[hi][hj] /= total

    return nueva

def juego_manual(willard):
    """
    Función principal que gestiona el flujo del programa en modo manual
    """
    while willard.vivo:  # Bucle principal
        # Imprimimos todos los heatmaps para que el jugador decida a donde quiere ir 
        willard.imprimir_heatmap(willard.mapa_trampas(), "Mapa de PROBABILIDAD de TRAMPAS")
        willard.imprimir_heatmap(willard.prob_M, "Mapa de PROBABILIDAD del SOLDADO")
        willard.imprimir_heatmap(willard.prob_S, "Mapa de PROBABILIDAD de la SALIDA")

        accion = input("\nPulsa W/A/S/D para moverte, G+W/A/S/D para lanzar una granada o E para salir: ").upper()
        
        if accion=="E":
                print("\nHas abandonado la misión")
                willard.vivo = False
        elif accion.startswith("G"):
            willard.arrojar_granada(accion[1])
        else:
            willard.moverse(accion)

if __name__ == "__main__":
    palacio = Palacio()
    willard = Willard(palacio)

    print("Elige en qué modo quieres jugar:")
    modo = input("Automático (A) o Manual (M) ").upper()

    if modo == "M":
        juego_manual(willard)
    
    elif modo == "A":
        camino = willard.planificar_mision()
        print("\nEl camino completo es:", camino)

    else:
        print("¡Error! Elige un modo válido:")
        modo = input("Automático (A) o Manual (M) ").upper()
