import numpy as np
import random

N = 6
NUM_PRECIPICIOS = 3
VACIO = " "
WILLARD = "CW"
KURTZ = "CK"
SOLDADO = "S"
PRECIPICIO = "P"
SALIDA = "E"  # Ponemos en la salida una E de (E)xit
DIRECCIONES = {"W": (-1, 0), "A": (0, -1), "S": (1, 0), "D": (0, 1)}
ACCIONES = {"W": "Arriba", "A": "Izquierda", "S": "Abajo", "D": "Derecha"}

class Palacio:
    def __init__(self):
        self.mapa = np.full((N, N), VACIO, dtype=object)  # Creamos el mapa
        self.pos_willard = (0, 0)  # La pos inicial de Willard siempre es (0,0)
        # El resto de posiciones quedan por determinar
        self.pos_kurtz = None
        self.pos_soldado = None
        self.pos_precipicios = []
        self.pos_salida = None
        self.colocar_elementos()
    
    def colocar_elementos(self):
        """ Coloca aleatoriamente los precipicios, soldado, Coronel Kurtz y la salida 
        en el mapa evitando solapamientos
        """
        self.mapa[self.pos_willard] = WILLARD  # Colocamos a Willard
        
        # Hacemos una lista de las posiciones libres
        posiciones = []
        for i in range(N):
            for j in range(N):
                if (i,j) != (0,0):
                    posiciones.append((i,j))
        # Mezclamos la lista para poder ir haciendo .pop() cada vez que necesitemos una posición para colocar
        # un elemento mientras eliminamos dicha posicion de la lista de posibles.
        random.shuffle(posiciones)
        
        # Colocamos los precipicios
        for _ in range(NUM_PRECIPICIOS):
            p = posiciones.pop()
            self.mapa[p] = PRECIPICIO
            self.pos_precipicios.append(p)
        
        # Colocamos al soldado
        s = posiciones.pop()
        self.mapa[s] = SOLDADO
        self.pos_soldado = s
        
        # Colocamos al Coronel Kurtz
        ck = posiciones.pop()
        self.mapa[ck] = KURTZ
        self.pos_kurtz = ck
                
        # Colocamos la salida
        e = posiciones.pop()
        self.mapa[e] = SALIDA
        self.pos_salida = e
    
    def perceptos(self, pos=None, grito=False) ->list:
        """
        Calcula los perceptos en una posición dada (brisa, ronquido, resplandor, paredes adyacentes y grito)
        Takes:
        - pos: tuple, coordenadas (i,j) de la celda. Si None, se usa la posición de Willard.
        - grito: bool, indica si se ha escuchado un grito debido a una granada
        Returns:
        - list: los diferentes perceptos
        """
        if pos is None:
            pos = self.pos_willard
        i,j = pos
        brisa = ronquido = resplandor = 0
        
        # Definimos las condiciones a cumplir cuando haya alguna pared
        pared_arriba = int(i==0)
        pared_abajo = int(i==N-1)
        pared_izqda = int(j==0)
        pared_dcha = int(j==N-1)
        
        # Definimos los preceptos para cada celda adyacente
        adyacentes = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        for x,y in adyacentes:
            if 0<=x<N and 0<=y<N:  # (dentro de los márgenes del tablero)
                if self.mapa[x,y] == PRECIPICIO:
                    brisa = 1
                if self.mapa[x,y] == SOLDADO:
                    ronquido = 1
                if self.mapa[x,y] == SALIDA:
                    resplandor = 1
        
        return [brisa, ronquido, resplandor, pared_arriba, pared_abajo, pared_izqda, pared_dcha, int(grito)]


class Willard:
    def __init__(self, palacio):
        self.palacio = palacio
        self.pos = palacio.pos_willard  # Comienza en la posición inicial de Willard
        
        # Creamos una matriz de booleanos para ir indicando qué celdas son seguras y cuáles no
        # La inicializamos entera a None porque aún no sabemos nada sobre las celdas
        self.seguros = np.full((N,N), None)  
        self.seguros[self.pos] = True  # Marcamos la celda inicial como segura, pues es donde se encuentra Willard
        # Creamos una matriz de booleanos para ir indicando qué celdas hemos visitado y cuáles no
        self.visitados = np.full((N, N), False)
        self.visitados[self.pos] = True  # Marcamos la celda inicial como visitada, pues es donde se encuentra Willard
        
        self.granada_disponible = True
        self.encontrado_kurtz = False
        self.vivo = True  # Para controlar el flujo del juego
        
        # Historial de perceptos y posiciones visitadas
        self.historial = []  # De la forma: (posición, percepto)
        self.posibles_precipicios = set()
        self.posibles_soldados = set()

    def mostrar_mapa(self):
        """
        Muestra el mapa conocido por Willard, indicando celdas seguras, peligrosas y desconocidas
        """
        print("\nMapa conocido:")
        for i in range(N):
            fila = ""
            for j in range(N):
                if (i, j) == self.pos:
                    fila += "[CW]"
                elif (i, j) == self.palacio.pos_salida and (i, j) == self.pos and not self.encontrado_kurtz:
                    # Mostramos E solo si Willard está en la casilla de salida y aún no encontró a Kurtz
                    fila += "[E]"
                elif self.seguros[i, j] is True:
                    fila += "[·]"
                elif self.seguros[i, j] is False:
                    fila += "[!]"
                else:
                    fila += "[?]"
            print(fila)
        print("\nLEYENDA:")
        print("  . : Seguro")
        print("  ! : Peligroso")
        print("  ? : Desconocido")

    def moverse(self, direccion:str):
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
            self.visitados[ni, nj] = True
            celda = self.palacio.mapa[ni,nj]
            if celda == PRECIPICIO:
                print("\n---------------------------------------")
                print("¡Caíste en un precipicio! Fin del juego")
                self.vivo = False
            elif celda == SOLDADO:
                print("\n---------------------------------------")
                print("¡El soldado enemigo te atrapó! Fin del juego")
                self.vivo = False
            elif celda == KURTZ:
                print("\n---------------------------------------")
                print("¡Encontraste al Coronel Kurtz! Es hora de salir del palacio")
                self.encontrado_kurtz = True
            elif celda == SALIDA and self.encontrado_kurtz:  # Solo sale si ha encontrado a Kurtz previamente
                print("\n---------------------------------------")
                print("¡Enhorabuena! Has completado la misión y salido del palacio con Kurtz")
                self.vivo = False  # Fin del juego
            else:
                self.seguros[ni,nj] = True  # Si no ha encontrado nada, asumimos que es una celda segura
        
        else:  # Si se sale, es porque hay una pared
            print("No puedes moverte en esa dirección porque hay una pared")
    
    def arrojar_granada(self, direccion:str):
        """
        Lanza una granada a la celda adyacente en la dirección indicada, eliminando al soldado si está 
        Takes:
        - direccion: str, una de 'W', 'A', 'S' o 'D'
        """
        if not self.granada_disponible:
            print("No te quedan granadas disponibles")
            return
        di,dj = DIRECCIONES.get(direccion.upper(), (0,0))
        ni,nj = self.pos[0]+di, self.pos[1]+dj
        if 0<=ni<N and 0<=nj<N:  # Nos aseguramos de que esté dentro de la región del palacio
            if self.palacio.mapa[ni,nj] == SOLDADO:
                print("¡Has eliminado al soldado enemigo con la granada!")
                self.palacio.mapa[ni,nj] = VACIO  # Como hemos eliminado al soldado la celda pasa a estar vacía
            else:
                print("La granada no afectó a nada")
            self.granada_disponible = False
        else:
            print("No puedes arrojar la granada fuera las celdas del palacio")

    def deducciones(self):
        """
        Actualiza las celdas seguras, peligrosas y posibles peligros usando perceptos y 
        el historial acumulado
        """
        # Llamamos a la función de palacio que nos devuelve la lista de preceptos (booleanos) en esa posición
        percepto = self.palacio.perceptos(self.pos)
        brisa, ronquido, resplandor = percepto[0], percepto[1], percepto[2]
        print(f"\nPerceptos: Brisa={brisa}, Ronquido={ronquido}, Resplandor={resplandor}")

        # Actualizamos
        self.seguros[self.pos] = True
        self.visitados[self.pos] = True
        self.historial.append((self.pos, percepto))

        x0, y0 = self.pos  # (posición actual)
        # Seleccionamos las celdas adyacentes a la posición actual
        adyacentes = [(x0 - 1, y0), (x0 + 1, y0), (x0, y0 - 1), (x0, y0 + 1)]
        adyacentes = [(x, y) for x, y in adyacentes if 0 <= x < N and 0 <= y < N]  # (cogemos solo las que estén dentro de los límites)

        # Si no hay perceptos de peligro, marcamos las adyacentes como seguras
        if brisa == 0 and ronquido == 0:
            for x, y in adyacentes:
                if self.seguros[x, y] is None:
                    self.seguros[x, y] = True
                    self.posibles_precipicios.discard((x, y))
                    self.posibles_soldados.discard((x, y))
        else:  # Posibles celdas peligrosas según los perceptos
            for x, y in adyacentes:
                if self.seguros[x, y] is None:
                    if brisa == 1:
                        self.posibles_precipicios.add((x, y))
                    if ronquido == 1:
                        self.posibles_soldados.add((x, y))

        for x in range(N):
            for y in range(N):
                # Inicializamos ambas a True hasta que probemos lo contrario
                puede_precipicio = True
                puede_soldado = True

                # Comprobamos contradicciones analizando todo lo que sabemos hasta ahora (con el historial)
                for (hx, hy), hpercepto in self.historial:
                    hbrisa, hronquido = hpercepto[0], hpercepto[1]
                    if abs(x - hx) + abs(y - hy) == 1:  # Para comprobar si es adyacente aplicamos la fórmula de la distancia Manhattan
                        if hbrisa == 0:
                            puede_precipicio = False
                        if hronquido == 0:
                            puede_soldado = False

                if not puede_precipicio and not puede_soldado:  # Como no puede ser ninguna de las dos, será segura
                    self.seguros[x, y] = True
                    self.posibles_precipicios.discard((x, y))
                    self.posibles_soldados.discard((x, y))

                elif puede_precipicio and not puede_soldado:
                    self.seguros[x, y] = False
                    self.posibles_precipicios.add((x, y))
                    self.posibles_soldados.discard((x, y))

                elif puede_soldado and not puede_precipicio:
                    self.seguros[x, y] = False
                    self.posibles_soldados.add((x, y))
                    self.posibles_precipicios.discard((x, y))

    def bfs(self, objetivos) ->list:
        """
        Algoritmo BFS mostrando la frontera, transiciones y explorados
        Takes:
        - objetivos: set o list de tuplas con posiciones destino
        Returns:
        - list: secuencia de acciones (direcciones) hacia el objetivo o None si no existe camino.
        """
        # En BFS utilizamos colas, definimos cada elemento de ella como (posición actual, camino hasta ella)
        cola = [(self.pos, [])]  # Inicialmente: (posición inicial, lista vacía)
        
        visitados = np.full((N, N), False)  # Nos creamos una matriz de visitados para no repetir celdas
        visitados[self.pos] = True  # Marcamos la posición en la que estamos como visitada

        step = 0  # (Iremos imprimiendo la info paso a paso)

        while len(cola) > 0:  # (mientras la cola no esté vacía)
            print(f"\nSTEP {step}")
            print("Frontier:", [nodo for nodo, _ in cola])
            (x,y), camino = cola.pop(0)  # Como las colas son FIFO, sacamos la primera que entró
            print("Removed state:", (x, y))

            if (x,y) in objetivos:
                return camino  # Si llegamos a una celda objetivo devolvemos el camino hasta ella
            
            acciones = []
            transiciones = []

            for d, (di,dj) in DIRECCIONES.items():  # Exploramos los vecinos (arriba, abajo, dcha. e izqda.)
                nx, ny = x + di, y + dj
                if 0 <= nx < N and 0 <= ny < N:  # (que no nos salgamos del palacio)
                    # SI Y SOLO SI es segura y aún no la hemos visitado
                    if self.seguros[nx, ny] and not visitados[nx, ny]:  
                        acciones.append(d)
                        transiciones.append((nx, ny))

                        visitados[nx, ny] = True
                        cola.append(((nx, ny), camino + [d])) # La guardamos en la cola con el camino actualizado
            
            print("Actions:", acciones)
            print("Transitions added:", transiciones)

            explorados = []
            for i in range(N):
                for j in range(N):
                    if visitados[i, j]:
                        explorados.append((i, j))
            print("Explored:", explorados)

            print("---------------------------")
            step += 1

        print("No se encontró ningún camino mediante BFS")
        return None  # En el caso de no haber camino posible
    
    def decidir_accion(self):
        """
        Decide la siguiente acción de Willard en modo automático basándose en 
        perceptos, celdas seguras y objetivos.
        Returns:
        - str o None: dirección ('W','A','S','D') a seguir o None si no hay
        """
        # Recogemos todos los preceptos percibidos por Willard
        percepto = self.palacio.perceptos(self.pos)
        resplandor = percepto[2]

        # Si hay un resplandor y ya hemos encontrado a Kurtz, vamos directos a la salida
        if self.encontrado_kurtz and resplandor == 1:
            camino = self.bfs({self.palacio.pos_salida})
            if camino:
                return camino[0]

        objetivos = []
        if not self.encontrado_kurtz:  # Si aún no hemos encontrado a Kurtz lo añadimos como objetivo
            objetivos.append(self.palacio.pos_kurtz)
        
        for i in range(N):
            for j in range(N):
                # Exploramos las celdas que sabemos que son seguras sin incluir en la que nos encontramos
                if self.seguros[i, j] and not self.visitados[i, j]:
                    objetivos.append((i, j))
        # Calculamos un camino seguro hasta una de esas celdas mediante bfs y devolvemos solo el primer paso
        camino = self.bfs(objetivos)
        if camino:
            return camino[0]

        # Si no hay celdas seguras no visitadas, volvemos a una segura ya visitada (backtracking)
        if not objetivos:
            for i in range(N):
                for j in range(N):
                    if self.seguros[i, j]:
                        objetivos.append((i, j))

        return None  # No podemos realizar ninguna acción


def main():
    """
    Función principal que gestiona el flujo del programa
    """
    palacio = Palacio()
    willard = Willard(palacio)

    print("Elige en qué modo quieres jugar:")
    modo = input("Automático (A) o Manual (M) ").upper()
    
    while willard.vivo:
        willard.mostrar_mapa()
        willard.deducciones()
        
        if modo == "A":
            accion = willard.decidir_accion()
            if accion is None:
                print("Willard no puede tomar más decisiones. Fin del juego")
                willard.vivo = False
            else:
                print("Willard ha decidido:", ACCIONES[accion])
                willard.moverse(accion)
        
        elif modo == "M":
            accion = input("Pulsa W/A/S/D para moverte, G+W/A/S/D para lanzar una granada o E para salir: ").upper()
            if accion=="E":
                print("Has abandonado la misión")
                willard.vivo = False
            elif accion.startswith("G"):
                willard.arrojar_granada(accion[1])
            else:
                willard.moverse(accion)
        
        else:
            print("¡Error! Elige un modo válido:")
            modo = input("Automático (A) o Manual (M) ").upper()


if __name__=="__main__":
    main()