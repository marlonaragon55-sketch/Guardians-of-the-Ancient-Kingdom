"""Guardians of the Ancient Kingdom - definición de las clases del sistema.

Este módulo solo define clases: no ejecuta nada al importarse.
"""
from abc import ABC, abstractmethod


class AtaqueInvalidoError(ValueError):
    """Se lanza cuando un ataque no cumple las reglas (atacante o objetivo derrotado, etc.)."""


class Personaje(ABC):
    """Clase abstracta con lo que comparten todos los guardianes."""

    VIDA_MAXIMA = 100

    def __init__(self, nombre, vida, ataque, defensa):
        # Se asignan mediante los setters para reutilizar las validaciones.
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    # ---------- validación auxiliar ----------
    @staticmethod
    def _validar_entero(valor, campo):
        # bool es subclase de int en Python, por eso se excluye de forma explícita.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(f"{campo} debe ser un entero, se recibió {valor!r}")

    # ---------- getters y setters ----------
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise TypeError("El nombre debe ser un texto")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        self.__nombre = valor.strip()

    @property
    def vida(self):
        return self.__vida

    @vida.setter
    def vida(self, valor):
        self._validar_entero(valor, "La vida")
        if not 0 <= valor <= self.VIDA_MAXIMA:
            raise ValueError(f"La vida debe estar entre 0 y {self.VIDA_MAXIMA}, se recibió {valor}")
        self.__vida = valor

    @property
    def ataque(self):
        return self.__ataque

    @ataque.setter
    def ataque(self, valor):
        self._validar_entero(valor, "El ataque")
        if valor <= 0:
            raise ValueError(f"El ataque debe ser un entero positivo, se recibió {valor}")
        self.__ataque = valor

    @property
    def defensa(self):
        return self.__defensa

    @defensa.setter
    def defensa(self, valor):
        self._validar_entero(valor, "La defensa")
        if valor < 0:
            raise ValueError(f"La defensa no puede ser negativa, se recibió {valor}")
        self.__defensa = valor

    # ---------- comportamiento común ----------
    def recibir_danio(self, cantidad):
        """Resta vida (sin pasar de 0) y devuelve el daño efectivamente recibido.

        El daño llega ya calculado: aquí NO se vuelve a descontar la defensa.
        """
        self._validar_entero(cantidad, "El daño")
        if cantidad < 0:
            raise ValueError(f"El daño no puede ser negativo, se recibió {cantidad}")
        efectivo = min(cantidad, self.__vida)
        self.__vida -= efectivo
        return efectivo

    def esta_vivo(self):
        return self.__vida > 0

    def mostrar_estado(self):
        return (f"{self.nombre} ({type(self).__name__}) | "
                f"Vida: {self.vida} | Ataque: {self.ataque} | Defensa: {self.defensa}")

    def _validar_ataque(self, objetivo):
        """Validaciones comunes a los tres tipos de ataque (se escriben una sola vez)."""
        if not isinstance(objetivo, Personaje):
            raise TypeError("El objetivo debe ser un Personaje")
        if objetivo is self:
            raise AtaqueInvalidoError(f"{self.nombre} no puede atacarse a sí mismo")
        if not self.esta_vivo():
            raise AtaqueInvalidoError(f"{self.nombre} está derrotado y no puede atacar")
        if not objetivo.esta_vivo():
            raise AtaqueInvalidoError(f"{objetivo.nombre} ya está derrotado")

    @abstractmethod
    def atacar(self, objetivo):
        """Ataca al objetivo y devuelve el daño efectivamente causado."""


class Guerrero(Personaje):
    """Golpe poderoso: ataque +20 % antes de restar la defensa."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        ataque_potenciado = self.ataque * 120 // 100  # enteros: redondea hacia abajo sin errores de float
        danio = max(0, ataque_potenciado - objetivo.defensa)
        return objetivo.recibir_danio(danio)


class Mago(Personaje):
    """Hechizo penetrante: ignora la defensa del objetivo."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.ataque)


class Arquero(Personaje):
    """Disparo crítico: duplica el daño si el ataque supera la defensa."""

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        if self.ataque > objetivo.defensa:
            danio = (self.ataque - objetivo.defensa) * 2
        else:
            danio = 0
        return objetivo.recibir_danio(danio)


class Combate:
    """Administra el enfrentamiento por turnos entre dos personajes ya creados (agregación)."""

    MAX_RONDAS = 50
    VICTORIA = "VICTORIA"
    EMPATE_TECNICO = "EMPATE_TECNICO"
    EMPATE_RONDAS = "EMPATE_RONDAS"

    def __init__(self, personaje1, personaje2):
        for p in (personaje1, personaje2):
            if not isinstance(p, Personaje):
                raise TypeError("Los participantes deben ser Personajes")
            if not p.esta_vivo():
                raise ValueError(f"{p.nombre} está derrotado y no puede combatir")
        if personaje1 is personaje2:
            raise ValueError("Un personaje no puede combatir contra sí mismo")
        self.__participantes = [personaje1, personaje2]
        self.__turno_actual = 0
        self.__rondas = 0
        self.__ganador = None
        self.__resultado = None
        self.__historial = []

    # ---------- consulta ----------
    @property
    def ganador(self):
        return self.__ganador

    @property
    def resultado(self):
        return self.__resultado

    @property
    def rondas(self):
        return self.__rondas

    @property
    def historial(self):
        return list(self.__historial)

    # ---------- lógica ----------
    def cambiar_turno(self):
        self.__turno_actual = 1 - self.__turno_actual

    def verificar_ganador(self):
        """Devuelve el Personaje vencedor o None si aún nadie ha caído."""
        for i, participante in enumerate(self.__participantes):
            if not participante.esta_vivo():
                return self.__participantes[1 - i]
        return None

    def _mostrar_estados(self, silencioso):
        if not silencioso:
            for p in self.__participantes:
                print(f"    {p.mostrar_estado()}")

    def iniciar(self, silencioso=False):
        if self.__resultado is not None:
            raise RuntimeError("Este combate ya finalizó")
        if not silencioso:
            print("--- Inicio del combate ---")
        self._mostrar_estados(silencioso)

        while self.__resultado is None:
            self.__rondas += 1
            danio_ronda = 0
            for _ in range(2):  # cada personaje ataca una vez por ronda
                atacante = self.__participantes[self.__turno_actual]
                defensor = self.__participantes[1 - self.__turno_actual]
                danio = atacante.atacar(defensor)  # polimorfismo: no se pregunta el tipo
                danio_ronda += danio
                self.__historial.append(
                    {"ronda": self.__rondas, "atacante": atacante.nombre,
                     "defensor": defensor.nombre, "danio": danio})
                if not silencioso:
                    print(f"Ronda {self.__rondas} | {atacante.nombre} ataca a "
                          f"{defensor.nombre} y causa {danio} de daño")
                self._mostrar_estados(silencioso)

                ganador = self.verificar_ganador()
                if ganador is not None:
                    self.__ganador = ganador
                    self.__resultado = self.VICTORIA
                    break
                self.cambiar_turno()

            if self.__resultado is None:
                if danio_ronda == 0:
                    self.__resultado = self.EMPATE_TECNICO
                elif self.__rondas >= self.MAX_RONDAS:
                    self.__resultado = self.EMPATE_RONDAS

        if not silencioso:
            self.mostrar_resultado()
        return self.__resultado

    def mostrar_resultado(self):
        if self.__resultado is None:
            print("El combate aún no ha terminado")
        elif self.__resultado == self.VICTORIA:
            print(f"Ganador: {self.__ganador.nombre}")
        elif self.__resultado == self.EMPATE_TECNICO:
            print("Empate técnico: ninguno causó daño en una ronda completa")
        else:
            print(f"Empate: se completaron {self.MAX_RONDAS} rondas sin ganador")
