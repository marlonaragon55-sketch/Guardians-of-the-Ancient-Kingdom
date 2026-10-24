"""Creación de objetos, ejecución del programa y casos de prueba obligatorios."""
from personajes import Personaje, Guerrero, Mago, Arquero, Combate, AtaqueInvalidoError

resultados = []


def titulo(texto):
    print(f"\n=== {texto} ===")


def comprobar(descripcion, condicion):
    resultados.append(bool(condicion))
    print(f"  [{'OK' if condicion else 'FALLO'}] {descripcion}")


def debe_fallar(descripcion, funcion, excepcion):
    try:
        funcion()
    except excepcion as error:
        comprobar(f"{descripcion} -> {type(error).__name__}: {error}", True)
    else:
        comprobar(f"{descripcion} (no lanzó excepción)", False)


def main():
    titulo("1. Creación correcta de los tres tipos de personajes")
    guerrero = Guerrero("Arthas", 100, 30, 20)
    mago = Mago("Gandalf", 80, 40, 10)
    arquero = Arquero("Legolas", 90, 35, 15)
    for p in (guerrero, mago, arquero):
        print(f"    {p.mostrar_estado()}")
    comprobar("Se crearon Guerrero, Mago y Arquero",
              all(isinstance(p, Personaje) for p in (guerrero, mago, arquero)))

    titulo("2. Rechazo de vida superior a 100 o negativa")
    debe_fallar("Vida 150", lambda: Guerrero("Tank", 150, 30, 10), ValueError)
    debe_fallar("Vida 101", lambda: Mago("Merlin", 101, 30, 10), ValueError)
    debe_fallar("Vida -5", lambda: Arquero("Robin", -5, 30, 10), ValueError)

    titulo("3. Rechazo de nombres vacíos")
    debe_fallar("Nombre ''", lambda: Guerrero("", 100, 30, 10), ValueError)
    debe_fallar("Nombre '   '", lambda: Mago("   ", 100, 30, 10), ValueError)
    debe_fallar("Nombre numérico", lambda: Arquero(123, 100, 30, 10), TypeError)

    titulo("4. Rechazo de ataques y defensas inválidos")
    debe_fallar("Ataque 0", lambda: Guerrero("A", 100, 0, 10), ValueError)
    debe_fallar("Ataque -10", lambda: Mago("B", 100, -10, 10), ValueError)
    debe_fallar("Ataque texto", lambda: Arquero("C", 100, "fuerte", 10), TypeError)
    debe_fallar("Defensa -1", lambda: Guerrero("D", 100, 30, -1), ValueError)
    debe_fallar("Defensa decimal", lambda: Mago("E", 100, 30, 2.5), TypeError)

    titulo("5. Habilidad del Guerrero (30 de ataque vs 10 de defensa -> 26)")
    g = Guerrero("Guerrero", 100, 30, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 10)
    danio = g.atacar(objetivo)
    comprobar(f"Daño causado = {danio} (esperado 26)", danio == 26)
    comprobar(f"Vida del objetivo = {objetivo.vida} (esperado 74)", objetivo.vida == 74)

    titulo("6. Ataque del Mago ignora la defensa (40 vs defensa 20 -> 40)")
    m = Mago("Mago", 100, 40, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 20)
    danio = m.atacar(objetivo)
    comprobar(f"Daño causado = {danio} (esperado 40)", danio == 40)

    titulo("7. Disparo crítico del Arquero (35 vs 15 -> 40)")
    a = Arquero("Arquero", 100, 35, 5)
    objetivo = Guerrero("Objetivo", 100, 10, 15)
    danio = a.atacar(objetivo)
    comprobar(f"Daño causado = {danio} (esperado 40)", danio == 40)
    objetivo_fuerte = Guerrero("Muro", 100, 10, 35)
    danio = a.atacar(objetivo_fuerte)
    comprobar(f"Ataque no supera la defensa -> daño {danio} (esperado 0)", danio == 0)

    titulo("8. Imposibilidad de tener vida negativa")
    debil = Guerrero("Débil", 20, 10, 0)
    efectivo = debil.recibir_danio(50)
    comprobar(f"Recibe 50 con 20 de vida: daño efectivo {efectivo}, vida {debil.vida}",
              efectivo == 20 and debil.vida == 0)
    debe_fallar("Daño negativo", lambda: Guerrero("X", 50, 10, 0).recibir_danio(-5), ValueError)
    debe_fallar("Asignar vida -1 con el setter", lambda: setattr(debil, "vida", -1), ValueError)

    titulo("9. Imposibilidad de atacar estando derrotado")
    sano = Mago("Sano", 100, 30, 10)
    debe_fallar("Derrotado intenta atacar", lambda: debil.atacar(sano), AtaqueInvalidoError)
    debe_fallar("Atacar a un derrotado", lambda: sano.atacar(debil), AtaqueInvalidoError)
    debe_fallar("Objetivo que no es Personaje", lambda: sano.atacar("un dragón"), TypeError)

    titulo("10 y 11. Combate completo e identificación del ganador")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    combate.iniciar()
    danios = [t["danio"] for t in combate.historial]
    comprobar(f"Daños por turno {danios} (esperado [26, 40, 26, 40, 26, 20])",
              danios == [26, 40, 26, 40, 26, 20])
    comprobar("El ganador es Gandalf con 2 de vida",
              combate.ganador is gandalf and gandalf.vida == 2 and arthas.vida == 0)

    titulo("12. Combate sin daño: empate técnico")
    torpe1 = Guerrero("Torpe1", 100, 10, 20)
    torpe2 = Guerrero("Torpe2", 100, 10, 20)
    empate = Combate(torpe1, torpe2)
    empate.iniciar()
    comprobar("Resultado EMPATE_TECNICO en 1 ronda",
              empate.resultado == Combate.EMPATE_TECNICO and empate.rondas == 1)

    titulo("Extra: empate por 50 rondas sin ganador")
    lento1 = Guerrero("Lento1", 100, 1, 0)
    lento2 = Guerrero("Lento2", 100, 1, 0)
    largo = Combate(lento1, lento2)
    largo.iniciar(silencioso=True)
    largo.mostrar_resultado()
    comprobar("Resultado EMPATE_RONDAS tras 50 rondas",
              largo.resultado == Combate.EMPATE_RONDAS and largo.rondas == 50)

    titulo("RESUMEN")
    print(f"  {sum(resultados)} de {len(resultados)} comprobaciones superadas")


if __name__ == "__main__":
    main()
