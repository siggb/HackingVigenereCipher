# ~*~ coding: utf-8 ~*~
import sys, re, string

regex = re.compile('[%s]' % re.escape(string.punctuation))
ALPHABET = [u'а',u'б',u'в',u'г',u'д',u'е',u'ё',u'ж',u'з',u'и',u'й',u'к',u'л',u'м',u'н',u'о',
            u'п',u'р',u'с',u'т',u'у',u'ф',u'х',u'ц',u'ч',u'ш',u'щ',u'ъ',u'ы',u'ь',u'э',u'ю',u'я']

class VigenereEncode(object):
    """
    Класс, осуществляющий шифрацию указанного сообщения
    методом Виженера
    """
    def __init__(self, key, message):
        """
        Базовый конструктор класса
        """
        self.key = key
        self.message = message

        self.vigenereSquare = []
        self.encodedMessage = ""

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
        Метод подготовки строк для шифрования
        """
        self.message = self.message.lower()

        # ключ шифрования избавляется от переносов, пробелов,
        # символов пунктуации и переводится в нижний регистр
        self.key = re.sub("^\s+|\n|\r|\s+$| ", '', self.key)
        self.key = regex.sub('', self.key)
        self.key = self.key.lower()

    def getEncodedText(self):
        """
        Метод непосредственного шифрования
        """
        i = 0
        for symb in self.message:
            col = None
            try:
                col = self.vigenereSquare[0].index(symb)
            except ValueError:
                # если символ сообщения не содержится в алфавите шифрования,
                # то он не шифруется, а текущий символ ключа используется дальше
                self.encodedMessage += symb
                continue

            # если ключ кончился, то повторяем его
            if i==len(self.key):
                i = 0

            # ищем строку в 0-м столбце квадрата Виженера по символу ключа
            row = None
            try:
                row = self.vigenereColumn(0).index(self.key[i])
            except ValueError:
                return "!!! Ошибка шифрования : некорректный ключ !!!"

            i += 1
            self.encodedMessage += self.vigenereSquare[row][col]

        return self.encodedMessage