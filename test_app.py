from app import sumar, restar, multiplicar, dividir


def test_sumar_enteros_positivos():
    assert sumar(2, 3) == 5


def test_sumar_negativos():
    assert sumar(-1, -1) == -2


def test_sumar_con_cero():
    assert sumar(10, 0) == 10


def test_restar():
    assert restar(10, 5) == 5


def test_multiplicar():
    assert multiplicar(3, 4) == 12


def test_dividir_normal():
    assert dividir(10, 2) == 5


def test_dividir_con_resultado_flotante():
    assert dividir(5, 2) == 2.5


def test_dividir_por_cero():
    assert dividir(10, 0) == "Error: División por cero"