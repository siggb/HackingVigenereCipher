# ~*~ coding: utf-8 ~*~
import sys, re, string

regex = re.compile('[%s]' % re.escape(string.punctuation))
ALPHABET = [u'а',u'б',u'в',u'г',u'д',u'е',u'ё',u'ж',u'з',u'и',u'й',u'к',u'л',u'м',u'н',u'о',
            u'п',u'р',u'с',u'т',u'у',u'ф',u'х',u'ц',u'ч',u'ш',u'щ',u'ъ',u'ы',u'ь',u'э',u'ю',u'я']

class VigenereDecode(object):
    """
    Класс, осуществляющий дешифрацию сообщения,
    зашифрованного методом Виженера
    """
    def __init__(self, key, message):
        """
        Базовый конструктор класса
        """
        self.key = key
        self.encodedMessage = message

        self.vigenereSquare = []
        self.message = ""

        self.createVigenereSquare()
        self.doPreparing()

    def createVigenereSquare(self):
        """
        Метод для построения квадрата Виженера
        """
        if not self.vigenereSquare.__len__():
            for row in xrange(0,len(ALPHABET)):
                pos = row
                self.vigenereSquare.append([])
                for col in xrange(0,len(ALPHABET)):
                    if pos == len(ALPHABET):
                        pos = 0
                    self.vigenereSquare[row].append(ALPHABET[pos])
                    pos += 1

    def printVigenereSquare(self):
        """
        Метод для вывода в консоль квадрата Виженера
        """
        for row in xrange(0,len(ALPHABET)):
            for col in xrange(0,len(ALPHABET)):
                sys.stdout.write("%s" % self.vigenereSquare[row][col])
            print('\n')

    def vigenereColumn(self, i):
        """
        Метод для получения i-того столбца
        квадрата Виженера
        """
        return [row[i] for row in self.vigenereSquare]

    def doPreparing(self):
        """
        Метод подготовки строк для дешифрации
        """
        self.encodedMessage = self.encodedMessage.lower()

        # ключ дешифрации избавляется от переносов, пробелов,
        # символов пунктуации и переводится в нижний регистр
        self.key = re.sub("^\s+|\n|\r|\s+$| ", '', self.key)
        self.key = regex.sub('', self.key)
        self.key = self.key.lower()

    def getDecodedText(self):
        """
        Метод непосредственной дешифрации
        """
        i = 0
        for symb in self.encodedMessage:
            # если ключ кончился, то повторяем его
            if i==len(self.key):
                i = 0

            # ищем строку в 0-м столбце квадрата Виженера по символу ключа
            row = None
            try:
                row = self.vigenereColumn(0).index(self.key[i])
            except ValueError:
                return "!!! Ошибка дешифрации : некорректный ключ !!!"

            col = None
            try:
                col = self.vigenereSquare[row].index(symb)
                self.message += self.vigenereSquare[0][col]
                # берем следующий символ ключа
                i += 1
            except ValueError:
                # если символ сообщения не содержится в алфавите шифрования,
                # то он не шифровался, а это значит, что мы пропускаем его
                self.message += symb
                continue

        return self.message