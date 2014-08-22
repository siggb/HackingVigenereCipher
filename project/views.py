# ~*~ coding: utf-8 ~*~
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from logic import encoding
from logic import decoding
from logic import hacking
from logic import markov_chains


def encryption_view(request):
    """
    Метод для формирования страницы шифрования
    """
    return render_to_response("encryption.html", RequestContext(request))


def decryption_view(request):
    """
    Метод для формирования страницы дешифрования/взлома шифра
    """
    return render_to_response("decryption.html")


def markov_chains_view(request):
    """
    Метод для формирования страницы анализа
    дешифрованного текста с помощью цепей Маркова
    """
    return render_to_response("markov.html", RequestContext(request))


def encryption_final_view(request):
    """
    Метод для формирования страницы результатов шифрования
    """
    message = request.POST.get('message', '')
    key = request.POST.get('key', '')

    # если сообщение или ключ отсутствуют
    # - делаем редирект на ту же страницу
    if not message or not key:
        return HttpResponseRedirect("/")

    # основная бизнес-логика
    enc = encoding.VigenereEncode(key, message)
    return render_to_response("result.html", {'type': 'шифрования', 'message': enc.getEncodedText()})


def decryption_final_view(request):
    """
    Метод для формирования страницы результатов дешифрования/взлома
    """
    message = request.POST.get('message', '')
    key = request.POST.get('key', '')

    # если сообщение отсутствует
    # - делаем редирект на ту же страницу
    if not message:
        return HttpResponseRedirect("/decryption/")

    if not key:
        # если ключ отсутствует - запускаем механизмы взлома шифра
        hack = hacking.VigenereHack(message)
        return render_to_response("result.html", {'type': 'взлома шифра', 'message': hack.getOriginText()})
    else:
        # если ключ присутствует - запускаем механизмы дешифрации шифра
        dec = decoding.VigenereDecode(key, message)
        return render_to_response("result.html", {'type': 'дешифрования', 'message': dec.getDecodedText()})


def markov_chains_final_view(request):
    """
    Метод для формирования страницы результатов анализа
    дешифрованного текста с помощью цепей Маркова
    """
    training_text = request.POST.get('training_text', '')
    keys = request.POST.get('keys', '')
    message = request.POST.get('message', '')

    try:
        multiplicity = int(request.POST.get('multiplicity', ''))
    except ValueError:
        return HttpResponseRedirect("/markov/")

    # если сообщение или ключ отсутствуют
    # - делаем редирект на ту же страницу
    if not training_text or not message or not multiplicity or not keys:
        return HttpResponseRedirect("/markov/")
    elif multiplicity > 5 or multiplicity < 1:
        return HttpResponseRedirect("/markov/")

    # основная бизнес-логика
    m_ch = markov_chains.MarkovChainsAnalysis(training_text, multiplicity, keys, message)
    return render_to_response("result.html", {'type': 'анализа дешифрованного текста с помощью цепей Маркова',
                                              'message':m_ch.getAnalysisResult()})