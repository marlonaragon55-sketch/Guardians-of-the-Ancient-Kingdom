import pytest

from personajes import Personaje, Guerrero, Mago, Arquero, Combate, AtaqueInvalidoError


# ---------- creación y validaciones ----------
@pytest.mark.parametrize("clase", [Guerrero, Mago, Arquero])
def test_creacion_valida(clase):
    p = clase("Heroe", 100, 30, 10)
    assert (p.nombre, p.vida, p.ataque, p.defensa) == ("Heroe", 100, 30, 10)
    assert isinstance(p, Personaje)


def test_personaje_es_abstracto():
    with pytest.raises(TypeError):
        Personaje("Nadie", 100, 10, 10)


@pytest.mark.parametrize("vida", [101, 150, -1])
def test_vida_fuera_de_rango(vida):
    with pytest.raises(ValueError):
        Guerrero("A", vida, 10, 10)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_nombre_vacio(nombre):
    with pytest.raises(ValueError):
        Mago(nombre, 100, 10, 10)


@pytest.mark.parametrize("ataque", [0, -5])
def test_ataque_no_positivo(ataque):
    with pytest.raises(ValueError):
        Arquero("A", 100, ataque, 10)


def test_defensa_negativa():
    with pytest.raises(ValueError):
        Guerrero("A", 100, 10, -1)


@pytest.mark.parametrize("campo,valor", [("ataque", "x"), ("defensa", 1.5), ("vida", True)])
def test_tipos_invalidos(campo, valor):
    p = Guerrero("A", 100, 10, 10)
    with pytest.raises(TypeError):
        setattr(p, campo, valor)


# ---------- cálculo de daño ----------
def test_dano_guerrero():
    assert Guerrero("G", 100, 30, 0).atacar(Guerrero("O", 100, 5, 10)) == 26


def test_dano_guerrero_redondea_hacia_abajo():
    # 31 * 1.2 = 37.2 -> 37; 37 - 10 = 27
    assert Guerrero("G", 100, 31, 0).atacar(Guerrero("O", 100, 5, 10)) == 27


def test_dano_guerrero_nunca_negativo():
    objetivo = Guerrero("O", 100, 5, 50)
    assert Guerrero("G", 100, 10, 0).atacar(objetivo) == 0
    assert objetivo.vida == 100


def test_dano_mago_ignora_defensa():
    assert Mago("M", 100, 40, 0).atacar(Guerrero("O", 100, 5, 20)) == 40


def test_dano_arquero_critico():
    assert Arquero("A", 100, 35, 0).atacar(Guerrero("O", 100, 5, 15)) == 40


def test_arquero_sin_critico_si_no_supera_defensa():
    assert Arquero("A", 100, 15, 0).atacar(Guerrero("O", 100, 5, 15)) == 0


# ---------- vida y estado ----------
def test_vida_nunca_negativa():
    p = Guerrero("P", 20, 10, 0)
    assert p.recibir_danio(50) == 20
    assert p.vida == 0
    assert not p.esta_vivo()


def test_danio_negativo_rechazado():
    with pytest.raises(ValueError):
        Guerrero("P", 50, 10, 0).recibir_danio(-1)


def test_recibir_danio_no_descuenta_defensa_otra_vez():
    p = Guerrero("P", 100, 10, 50)
    p.recibir_danio(10)
    assert p.vida == 90


def test_derrotado_no_puede_atacar():
    muerto = Mago("M", 0, 10, 0)
    with pytest.raises(AtaqueInvalidoError):
        muerto.atacar(Guerrero("O", 100, 10, 0))


def test_no_se_puede_atacar_a_derrotado():
    with pytest.raises(AtaqueInvalidoError):
        Mago("M", 100, 10, 0).atacar(Guerrero("O", 0, 10, 0))


def test_objetivo_invalido():
    with pytest.raises(TypeError):
        Mago("M", 100, 10, 0).atacar("dragón")


# ---------- combate ----------
def test_combate_arthas_vs_gandalf():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    combate.iniciar(silencioso=True)
    assert combate.resultado == Combate.VICTORIA
    assert combate.ganador is gandalf
    assert [t["danio"] for t in combate.historial] == [26, 40, 26, 40, 26, 20]
    assert (arthas.vida, gandalf.vida) == (0, 2)


def test_combate_empate_tecnico():
    c = Combate(Guerrero("A", 100, 10, 20), Guerrero("B", 100, 10, 20))
    c.iniciar(silencioso=True)
    assert c.resultado == Combate.EMPATE_TECNICO
    assert c.ganador is None


def test_combate_empate_por_50_rondas():
    c = Combate(Guerrero("A", 100, 1, 0), Guerrero("B", 100, 1, 0))
    c.iniciar(silencioso=True)
    assert c.resultado == Combate.EMPATE_RONDAS
    assert c.rondas == 50


def test_combate_rechaza_participantes_invalidos():
    with pytest.raises(TypeError):
        Combate(Guerrero("A", 100, 10, 0), "no soy personaje")
    p = Guerrero("A", 100, 10, 0)
    with pytest.raises(ValueError):
        Combate(p, p)


def test_combate_no_se_reinicia():
    c = Combate(Guerrero("A", 100, 10, 20), Guerrero("B", 100, 10, 20))
    c.iniciar(silencioso=True)
    with pytest.raises(RuntimeError):
        c.iniciar(silencioso=True)
