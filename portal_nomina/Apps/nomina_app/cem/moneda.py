#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'efrenfuentes'

#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'efrenfuentes'

from ..models_choices import MONEDA_SINGULAR, MONEDA_PLURAL, CENTIMOS_SINGULAR, CENTIMOS_PLURAL, MAX_NUMERO, UNIDADES, DECENAS, DIEZ_DIEZ, CIENTOS


def numero_a_letras(numero):
    numero_entero = int(numero)
    if numero_entero > MAX_NUMERO:
        raise OverflowError('Número demasiado alto')
    if numero_entero < 0:
        return 'menos %s' % numero_a_letras(abs(numero))
    
    parte_entera, parte_decimal = str(numero).split('.') if '.' in str(numero) else (str(numero), '00')
    letras_decimal = '%s/100 M.N.' % parte_decimal.zfill(2)

    if numero_entero <= 999:
        resultado = leer_centenas(numero_entero)
    elif numero_entero <= 999999:
        resultado = leer_miles(numero_entero)
    elif numero_entero <= 999999999:
        resultado = leer_millones(numero_entero)
    else:
        resultado = leer_millardos(numero_entero)

    resultado = resultado.replace('UNO MIL', 'UN MIL').strip().replace(' _ ', ' ').replace('  ', ' ')
    resultado = '%s PESOS %s' % (resultado, letras_decimal)
    return resultado

def numero_a_moneda(numero):
    numero_entero = int(numero)
    parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
    centimos = CENTIMOS_SINGULAR if parte_decimal == 1 else CENTIMOS_PLURAL
    moneda = MONEDA_SINGULAR if numero_entero == 1 else MONEDA_PLURAL
    letras = numero_a_letras(numero_entero).replace('UNO', 'UN')
    letras_decimal = 'CON %s %s' % (numero_a_letras(parte_decimal).replace('UNO', 'UN'), centimos)
    resultado = '%s %s %s' % (letras, moneda, letras_decimal)
    return resultado

def leer_decenas(numero):
    if numero < 10:
        return UNIDADES[numero]
    decena, unidad = divmod(numero, 10)
    if numero <= 19:
        return DIEZ_DIEZ[unidad] if decena == 1 else DECENAS[unidad]
    elif numero <= 29:
        return 'VEINTI%s' % UNIDADES[unidad] if unidad > 0 else 'VEINTE'
    else:
        resultado = DECENAS[decena]
        if unidad > 0:
            resultado = '%s Y %s' % (resultado, UNIDADES[unidad])
        return resultado

def leer_centenas(numero):
    centena, decena = divmod(numero, 100)
    resultado = CIENTOS[centena] if centena > 0 else ''
    if decena > 0:
        resultado = '%s %s' % (resultado, leer_decenas(decena))
    return resultado

def leer_miles(numero):
    millar, centena = divmod(numero, 1000)
    resultado = UNIDADES[millar] if 1 <= millar <= 9 else leer_decenas(millar) if 10 <= millar <= 99 else ''
    resultado = '%s MIL' % resultado if millar > 1 else 'MIL' if millar == 1 else ''
    if centena > 0:
        resultado = '%s %s' % (resultado, leer_centenas(centena))
    return resultado

def leer_millones(numero):
    millon, millar = divmod(numero, 1000000)
    resultado = UNIDADES[millon] if 1 <= millon <= 9 else leer_decenas(millon) if 10 <= millon <= 99 else ''
    resultado = '%s MILLONES' % resultado if millon > 1 else 'UN MILLON' if millon == 1 else ''
    if 1 <= millar <= 999:
        resultado = '%s %s' % (resultado, leer_centenas(millar))
    elif 1000 <= millar <= 999999:
        resultado = '%s %s' % (resultado, leer_miles(millar))
    return resultado

def leer_millardos(numero):
  millardo, millon = divmod(numero, 1000000)
  resultado = '%s MILLONES %s' % (leer_miles(millardo), leer_millones(millon)) if millardo > 0 else leer_millones(millon)
  return resultado
