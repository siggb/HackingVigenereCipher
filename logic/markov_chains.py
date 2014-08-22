# ~*~ coding: utf-8 ~*~
import sys, re, string, math
from logic import pykov
from logic import decoding
from random import choice
from random import randrange

regex = re.compile('[%s]' % re.escape(string.punctuation))
ALPHABET = [u'а',u'б',u'в',u'г',u'д',u'е',u'ё',u'ж',u'з',u'и',u'й',u'к',u'л',u'м',u'н',u'о',u'п',
            u'р',u'с',u'т',u'у',u'ф',u'х',u'ц',u'ч',u'ш',u'щ',u'ъ',u'ы',u'ь',u'э',u'ю',u'я',u' ']


class MarkovChainsAnalysis(object):
    """
    Класс, осуществляющий анализ дешифрованного
    сообщения с помощью цепей Маркова
    """
    def __init__(self, training_text, multiplicity, keys, message):
        """
        Базовый конструктор класса
        """
        self.trainingText = training_text # - обучающий текст
        self.codedMessage = message  # - закодированное сообщение
        self.multiplicity = multiplicity # - степень кратности цепи Маркова
        self.keys = keys.split(", ") # - текст всевозможных ключей

        self.message = "" # - сообщение
        self.ngramms = [] # - массив n-грамм
        self.markovChain = pykov.Chain() # - цепь Маркова
        self.decodedTextsArray = [] # - массив дешифрованных сообщений
        self.textNgramms = [] # - массив n-грамм дешифрованного текста
        self.probabilities = [] # - массив вероятностей для массива n-грамм


    def createMarkovChain(self):
        """
        Метод для формирования цепи Маркова по обучающему тексту
        """
        listOfNodes = []

        # формируем массив пар n-грамм для определения
        # частот появления этих пар
        for i in xrange(0,len(self.ngramms)-1):
            listOfNodes.append(self.ngramms[i] + self.ngramms[i+1])

        # пробегаем по всем парам n-грамм и определяем вероятности дуг
        for i in xrange(0,len(self.ngramms)-1):
            elem = self.ngramms[i] + self.ngramms[i+1]
            freq = float(listOfNodes.count(elem)) / float(len(listOfNodes))
            self.markovChain[(self.ngramms[i],self.ngramms[i+1])] = freq
            #sys.stdout.write("%s-%s : %d / %d\n" % (self.ngramms[i], self.ngramms[i+1],
            #                                       listOfNodes.count(elem),
            #                                       len(listOfNodes)))

        self.message = "Сформированная цепь Маркова:\n\n"
        self.message += chainStringFormat(self.markovChain, False)


    def transformDecodedTextToNgramms(self):
        """
        Метод для дешифрации шифротекста с помощью множества найденных ключей
        и формирования массива N-грамм
        """
        for curr_key in self.keys:
            dec = decoding.VigenereDecode(curr_key, self.codedMessage)
            text = dec.getDecodedText()
            self.decodedTextsArray.append(text)
            self.textNgramms.append(createNgrammList(text, self.multiplicity))


    def processProbability(self):
        """
        Метод для подсчета ln() вероятности соответствия входной строки цепи Маркова
        """
        for curr_ngramm in self.textNgramms:
            # 1) --- вычисляем точную сумму логарифмов
            # ln_sum = self.markovChain.walk_probability(curr_ngramm)
            #
            # 2) --- вычисляем сумму логарифмов с погрешностью в N-недостающих ребер
            ln_sum = self.markovChain.my_walk_probability(curr_ngramm, 10)
            self.probabilities.append(ln_sum)
            print(ln_sum, math.exp(ln_sum))
        # print(len(self.keys), len(self.probabilities))


    def showDecodedTextsForAnalysis(self):
        """
        Метод для вывода в веб-интерфейс текстов с наибольшей
        суммой ln() переходов и пригодных для дальнейшего анализа
        криптоаналитиком
        """
        self.message += "\n\n\n\nТексты, пригодные для дальнейшего анализа:"
        should_show_empty = True
        for i in xrange(0,len(self.probabilities)):
            elem = self.probabilities[i]
            if (abs(elem) > 0) and (elem != -float('Inf')):
                should_show_empty = False
                self.message += "\n\nKEY: %s\nMESSAGE: %s" % \
                                (self.keys[i].encode('utf-8'),self.decodedTextsArray[i].encode('utf-8'))

        if should_show_empty:
            self.message += "  ОТСУТСТВУЮТ"


    def showRandomWalks(self):
        """
        Метод для вывода в веб-интерфейс случайных путей,
        сформированных нашей цепью Маркова
        """
        self.message += "\n\n\n\nТексты, сформированные цепью Маркова самостоятельно:"

        # сколько будет шагов
        lengths = [len(self.ngramms),
                   randrange(len(self.ngramms)),
                   randrange(len(self.ngramms)),
                   randrange(len(self.ngramms)),
                   randrange(len(self.ngramms)),]

        # откуда будем начинать
        starts = {lengths[0]:None,
                  lengths[1]:choice(self.ngramms),
                  lengths[2]:choice(self.ngramms),
                  lengths[3]:choice(self.ngramms),
                  lengths[4]:choice(self.ngramms),}

        # 5 раз подряд формируем псевдо-случайные пути
        for cur_len in lengths:
            try:
                walk = self.markovChain.walk(cur_len, starts[cur_len])
                p = self.markovChain.walk_probability(walk)

                # преобразуем массив N-грамм в корректный текст
                is_first = True
                new_walk = []
                for elem in walk:
                    if is_first:
                        is_first = False
                        new_walk.append(elem)
                        continue
                    elem = elem[self.multiplicity-1:]
                    new_walk.append(elem)

                self.message += "\n\nСумма логарифмов ребер: %10.3f\nTEXT: %s" % \
                                (p,(''.join(new_walk)).encode('utf-8'))
            except Exception:
                pass


    def getAnalysisResult(self):
        """
        Метод для непосредственного анализа
        """
        if len(self.codedMessage) <= self.multiplicity:
            self.message = "Длина шифротекста меньше степени кратности цепи Маркова\n\n"
            self.message += self.codedMessage
            return self.message

        # 1) формируем последовательность n-грамм из обучающего текста
        self.ngramms = createNgrammList(self.trainingText, self.multiplicity)

        # 2) формируем цепь Маркова
        self.createMarkovChain()

        # 3) берем шифротекст, ключи, производим дешифрацию и формируем списки n-грамм
        self.transformDecodedTextToNgramms()

        # 4) определяем вероятность соответствия входной последовательности
        self.processProbability()

        # 5) покажем тексты, которые пригодны для дальнейшего анализа криптоаналитиком
        self.showDecodedTextsForAnalysis()

        # 6) определяем вероятность случайного пути цепи Маркова
        self.showRandomWalks()

        return self.message


# =====================================================================
#       Глобальные методы
# =====================================================================

def createNgrammList(sourceText, multiplicity):
    """
    Метод для формирования списка N-грамм входного текста
    """
    sourceText = sourceText.lower()
    sourceText = re.sub("^\s+|\n|\r|\s+$", ' ', sourceText)
    sourceText = regex.sub('', sourceText)

    # удаляем из текста символы, не входящие в наш алфавит
    for symb in sourceText:
        try:
            ALPHABET.index(symb)
        except ValueError:
            sourceText = sourceText.replace(symb, "")

    # заменяем повторяющиеся пробелы на единичные
    sourceText = re.sub("    ", ' ', sourceText)
    sourceText = re.sub("   ", ' ', sourceText)
    sourceText = re.sub("  ", ' ', sourceText)

    # print(sourceText)

    # циклически проходим по обучающему тексту
    # и формируем массив n-грамм в порядке их следования
    ngramms = []
    for i in xrange(0,len(sourceText)-multiplicity):
        curr_ngramm = sourceText[i:(i+multiplicity)]
        ngramms.append(curr_ngramm)
        # print(curr_ngramm)

    return ngramms


def printMatrix(matrix):
    """
    Метод для вывода в консоль матрицы
    """
    for row in xrange(0,len(matrix)):
        for col in xrange(0,len(matrix[row])):
            sys.stdout.write("%s " % matrix[row][col])
        print('\n')


def chainStringFormat(chain, shouldPrint):
    """
    Метод для преобразования цепи к виду строки
    и для вывода ее в консоль по желанию
    """
    str_output_rv = ""
    for key in chain.keys():
        str_key_output = ""
        for i in xrange(0,len(key)):
            str_output = "%s -> " % key[i]
            if i == (len(key)-1):
                str_output = str_output[:len(str_output)-4]
            if shouldPrint:
                sys.stdout.write(str_output) # <=
            str_key_output += str_output
        str_output = ": %s" % str(chain[key])
        if shouldPrint:
            sys.stdout.write(str_output) # <=
        str_key_output += str_output
        str_output_rv += str_key_output
        str_output_rv += "\n"
        if shouldPrint:
            print('\n')
    return str_output_rv.encode('utf-8')


def columnOfMatrix(matrix, i):
    """
    Метод для получения i-го столбца матрицы
    """
    return [row[i] for row in matrix]