import tkinter as tk
from tkinter import ttk, messagebox
import random

# ----------------------------- CONFIGURACIÓN INICIAL -----------------------------
ESTRATEGIAS = ["Aleatoria", "Agresiva", "Defensiva"]

# Tamaño del tablero de damas (8x8)
TAM_TABLERO = 8

# ----------------------------- LÓGICA DEL JUEGO DE DAMAS -----------------------------

class Ficha:
    def __init__(self, color, es_reina=False):
        self.color = color  # 'blanco' o 'negro'
        self.es_reina = es_reina

class JuegoDamas:
    def __init__(self):
        self.tablero = [[None for _ in range(TAM_TABLERO)] for _ in range(TAM_TABLERO)]
        self.turno = 'blanco'
        self.inicializar_fichas()

    def inicializar_fichas(self):
        for fila in range(3):
            for col in range(TAM_TABLERO):
                if (fila + col) % 2 != 0:
                    self.tablero[fila][col] = Ficha('negro')
        for fila in range(5, 8):
            for col in range(TAM_TABLERO):
                if (fila + col) % 2 != 0:
                    self.tablero[fila][col] = Ficha('blanco')

    def obtener_movimientos_validos(self, fila, col):
        movimientos = []
        ficha = self.tablero[fila][col]
        if ficha is None: return []

        direcciones = [(-1, -1), (-1, 1)] if ficha.color == 'blanco' else [(1, -1), (1, 1)]
        if ficha.es_reina:
            direcciones += [(-d[0], -d[1]) for d in direcciones]  # puede ir hacia atrás

        for dr, dc in direcciones:
            r, c = fila + dr, col + dc
            if 0 <= r < TAM_TABLERO and 0 <= c < TAM_TABLERO and self.tablero[r][c] is None:
                movimientos.append((r, c))
        return movimientos

    def mover(self, origen, destino):
        of, oc = origen
        df, dc = destino
        ficha = self.tablero[of][oc]
        self.tablero[of][oc] = None
        self.tablero[df][dc] = ficha

        # Convertir en reina si llega al fondo
        if ficha.color == 'blanco' and df == 0:
            ficha.es_reina = True
        elif ficha.color == 'negro' and df == TAM_TABLERO - 1:
            ficha.es_reina = True

        self.turno = 'negro' if self.turno == 'blanco' else 'blanco'

    def estrategia_maquina(self, estrategia):
        fichas_maquina = [(f, c) for f in range(TAM_TABLERO) for c in range(TAM_TABLERO)
                          if self.tablero[f][c] and self.tablero[f][c].color == self.turno]

        if estrategia == "Aleatoria":
            random.shuffle(fichas_maquina)
        elif estrategia == "Agresiva":
            fichas_maquina.sort(key=lambda x: int(self.tablero[x[0]][x[1]].es_reina), reverse=True)
        elif estrategia == "Defensiva":
            fichas_maquina.sort(key=lambda x: x[0] if self.turno == 'blanco' else TAM_TABLERO - 1 - x[0], reverse=False)

        for ficha_pos in fichas_maquina:
            movimientos = self.obtener_movimientos_validos(*ficha_pos)
            if movimientos:
                self.mover(ficha_pos, random.choice(movimientos))
                return

    def contar_fichas(self):
        blancas, negras = 0, 0
        for fila in self.tablero:
            for ficha in fila:
                if ficha:
                    if ficha.color == 'blanco':
                        blancas += 1
                    else:
                        negras += 1
        return blancas, negras

# ----------------------------- INTERFAZ GRÁFICA -----------------------------

class InterfazDamas:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Damas")
        self.juego = JuegoDamas()
        self.estrategia_blanco = tk.StringVar(value=ESTRATEGIAS[0])
        self.estrategia_negro = tk.StringVar(value=ESTRATEGIAS[0])
        self.num_simulaciones = tk.IntVar(value=10)

        self.crear_interfaz()

    def crear_interfaz(self):
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        # FRAME CONFIGURACIÓN
        frame_config = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20, relief="raised", bd=2)
        frame_config.pack(side="left", fill="y", padx=20, pady=20)

        # Estrategia Blanco
        tk.Label(frame_config, text="Estrategia Blanco:", bg="#ffffff", font=("Arial", 12)).pack()
        cb_blanco = ttk.Combobox(frame_config, textvariable=self.estrategia_blanco, values=ESTRATEGIAS, font=("Arial", 12))
        cb_blanco.pack(pady=10)

        # Estrategia Negro
        tk.Label(frame_config, text="Estrategia Negro:", bg="#ffffff", font=("Arial", 12)).pack()
        cb_negro = ttk.Combobox(frame_config, textvariable=self.estrategia_negro, values=ESTRATEGIAS, font=("Arial", 12))
        cb_negro.pack(pady=10)

        # Número de simulaciones
        tk.Label(frame_config, text="N° Simulaciones:", bg="#ffffff", font=("Arial", 12)).pack()
        tk.Entry(frame_config, textvariable=self.num_simulaciones, width=5, font=("Arial", 12)).pack(pady=10)

        # Botón de inicio de simulación
        tk.Button(frame_config, text="Iniciar Simulación", command=self.iniciar_simulacion,
                  bg="#4CAF50", fg="white", relief="flat", font=("Arial", 14),
                  activebackground="#45a049", padx=20, pady=10).pack(pady=20)

        # CANVAS DEL TABLERO
        self.canvas = tk.Canvas(self.root, width=480, height=480, bg="white", bd=2, relief="solid")
        self.canvas.pack(side="right", padx=20, pady=20)
        self.dibujar_tablero()

    def dibujar_tablero(self):
        self.canvas.delete("all")
        size = 60
        for f in range(TAM_TABLERO):
            for c in range(TAM_TABLERO):
                x1, y1 = c * size, f * size
                x2, y2 = x1 + size, y1 + size
                color = "#D18B47" if (f + c) % 2 == 0 else "#FFCE9E"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                ficha = self.juego.tablero[f][c]
                if ficha:
                    fill = "black" if ficha.color == "negro" else "white"
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=fill)
                    if ficha.es_reina:
                        self.canvas.create_text((x1 + x2)//2, (y1 + y2)//2,
                                                text="♕", font=("Arial", 20), fill="gold")

    def reiniciar_juego(self):
        self.juego = JuegoDamas()
        self.dibujar_tablero()

    def iniciar_simulacion(self):
        self.reiniciar_juego()

        estrategia1 = self.estrategia_blanco.get()
        estrategia2 = self.estrategia_negro.get()
        cantidad = self.num_simulaciones.get()

        resultados = {"blanco": 0, "negro": 0, "detalles": []}

        for i in range(cantidad):
            juego = JuegoDamas()
            turnos = 0
            while True:
                if juego.turno == "blanco":
                    juego.estrategia_maquina(estrategia1)
                else:
                    juego.estrategia_maquina(estrategia2)

                blancas, negras = juego.contar_fichas()
                if blancas == 0 or negras == 0 or turnos > 150:
                    ganador = "blanco" if blancas > negras else "negro"
                    resultados[ganador] += 1
                    detalles_partida = f"Simulación {i+1}: {ganador} ganó. "
                    detalles_partida += f"Turnos jugados: {turnos}. Fichas Blancas: {blancas}, Fichas Negras: {negras}"
                    resultados["detalles"].append(detalles_partida)
                    break

                turnos += 1

        # Mostrar resultados
        messagebox.showinfo("Resultados", f"Blanco: {resultados['blanco']} victorias\n"
                                         f"Negro: {resultados['negro']} victorias\n"
                                         f"Detalles:\n" + "\n".join(resultados['detalles']))

# ----------------------------- EJECUCIÓN -----------------------------

def main():
    root = tk.Tk()
    app = InterfazDamas(root)
    root.mainloop()

if __name__ == "__main__":
    main()
