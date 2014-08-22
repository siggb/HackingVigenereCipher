# ~*~ coding: utf-8 ~*~
import sys, re, string, collections, math
from fractions import gcd

regex = re.compile('[%s]' % re.escape(string.punctuation))
ALPHABET = [u'а',u'б',u'в',u'г',u'д',u'е',u'ё',u'ж',u'з',u'и',u'й',u'к',u'л',u'м',u'н',u'о',
            u'п',u'р',u'с',u'т',u'у',u'ф',u'х',u'ц',u'ч',u'ш',u'щ',u'ъ',u'ы',u'ь',u'э',u'ю',u'я']
ALPHABET_HALF = 16

class VigenereHack(object):
    """
    Класс, осуществляющий взлом сообщения,
    зашифрованного методом Виженера
    """
    def __init__(self, message):
        """
        Базовый конструктор класса
        """
        self.codedMessage = message # - закодированное сообщение
        self.message = "" # - то, куда выводим результат

        # метод Фридмана
        # //- Уильям Фредерик Фридман (1891—1969) -//
        # //- Американский криптограф -//
        self.shiftMatrix = [] # - матрица сдвинутых строк
        self.overlapCounts = [] # - количество совпадений по столбцам
        self.keyLengths = [] # - вычисленные длины ключей

        # метод Казиски
        # //- Фридрих Вильгельм Казиски (1805 –1881) -//
        # //- Майор прусской армии, криптограф -//
        self.bigramms = [] # - последовательность уникальных биграмм текста
        self.bigrammsPositions = [] # - матрица позиций биграмм (1 и более)
        self.keyLengthsByBigramms = [] # - вычисленные длины ключей

        # тест Казиски
        self.gcdLengths = [] # - возможные длины ключей
        self.keyLengthsGcd = [] # - вычисленные длины ключей

        # объединенные в порядке приоритета длины ключей
        self.finalKeyLengths = [] # - финальные вычисленные длины ключей

        # определение индексов совпадений
        self.messMatrix = [] # - матрица из N-столбцов, в которую поместили шифротекст
        self.alphabetMatrix = [] # - матрица частот букв
        self.indexesOfAgreements = [] # - индексы совпадений(ИС) для матрицы частот букв
        self.icKeyLengths = [] # - длины ключей, для которых ИС хороший

        # статистический анализ ключа
        self.shiftValuesMatrix = [] # - матрица величины сдвигов алфавита от 1-вой колонки
        self.keyWords = [] # - полученный массив ключей

        # анализ ключа на основе частот букв русского алфавита
        self.statMatrix = [] # - матрица частот
        self.statMatrixShifts = [] # - матрица сдвигов
        self.statKeyWords = [] # - полученный массив ключей


    def findKeyLength_byFridman(self):
        """
        Метод для определения длины ключа зашифрованного сообщения,
        основанный на нахождении максимума автокорелляционной функции
        (распространенное название - "Метод Фридмана")
        """
        self.codedMessage = self.codedMessage.lower()
        self.codedMessage = re.sub("^\s+|\n|\r|\s+$| ", '', self.codedMessage)
        self.codedMessage = regex.sub('', self.codedMessage)

        # поскольку при шифровании символы, не входящие в алфавит,
        # остаются без изменений и не "используют" символы ключа,
        # то на этапе взлома мы исключим их из шифра
        i = 0
        while i < len(self.codedMessage):
            try:
                symb = self.codedMessage[i]
                ALPHABET.index(symb)
            except ValueError:
                if i+1 == len(self.codedMessage):
                    self.codedMessage = self.codedMessage[:i-1]
                else:
                    self.codedMessage = self.codedMessage[:i] + self.codedMessage[i+1:]
            finally:
                i += 1

        # print(self.codedMessage)

        # теперь запишем шифр, циклически сдвигая его на 1 позицию влево
        # m/2 раз (тоесть 33/2 ~ 16)
        # for row in xrange(0,len(self.codedMessage)):
        for row in xrange(0,ALPHABET_HALF):
            pos = row
            self.shiftMatrix.append([])
            for col in xrange(0,len(self.codedMessage)):
                if pos == len(self.codedMessage):
                    pos = 0
                self.shiftMatrix[row].append(self.codedMessage[pos])
                pos += 1

        # теперь пробегая по всем строкам матрицы определим количество
        # совпавших букв в верхней и i-той строках
        self.overlapCounts.append(0)
        for row in xrange(1,len(self.shiftMatrix)):
            overlaps = 0
            for col in xrange(0,len(self.shiftMatrix[0])):
                if self.shiftMatrix[row][col] == self.shiftMatrix[0][col]:
                    overlaps += 1
            self.overlapCounts.append(overlaps)

        # берем максимальные значения из полученных
        m = max(self.overlapCounts)
        self.keyLengths = [i for i, j in enumerate(self.overlapCounts) if j == m]


    def printMatrix(self, matrix):
        """
        Метод для вывода в консоль матрицы
        """
        for row in xrange(0,len(matrix)):
            for col in xrange(0,len(matrix[row])):
                sys.stdout.write("%s " % matrix[row][col])
            print('\n')


    def columnOfMatrix(self, matrix, i):
        """
        Метод для получения i-го столбца матрицы
        """
        return [row[i] for row in matrix]


    def findKeyLength_byKazisky(self):
        """
        Метод для определения длины ключа зашифрованного сообщения,
        основанный на нахождении повторяющихся биграмм
        (распространенное название - "Метод Казиски")
        """
        self.codedMessage = self.codedMessage.lower()
        self.codedMessage = re.sub("^\s+|\n|\r|\s+$| ", '', self.codedMessage)
        self.codedMessage = regex.sub('', self.codedMessage)

        # поскольку при шифровании символы, не входящие в алфавит,
        # остаются без изменений и не "используют" символы ключа,
        # то на этапе взлома мы исключим их из шифра
        i = 0
        while i < len(self.codedMessage):
            try:
                symb = self.codedMessage[i]
                ALPHABET.index(symb)
            except ValueError:
                if i+1 == len(self.codedMessage):
                    self.codedMessage = self.codedMessage[:i-1]
                else:
                    self.codedMessage = self.codedMessage[:i] + self.codedMessage[i+1:]
            finally:
                i += 1

        # print(self.codedMessage)

        # циклически проходим по закодированному сообщению
        # и формируем массив всевозможных уникальных биграмм
        pos = 0
        for i in xrange(0,len(self.codedMessage)-1):
            curr_bigramm = self.codedMessage[i] + self.codedMessage[i+1]
            if curr_bigramm not in self.bigramms:
                self.bigramms.append(curr_bigramm)
                self.bigrammsPositions.append([])
                self.bigrammsPositions[pos].append(i+1)
                pos += 1
            else:
                # если биграмма повторяется - запоминаем только позицию
                bigramm_pos = None
                try:
                    bigramm_pos = self.bigramms.index(curr_bigramm)
                    self.bigrammsPositions[bigramm_pos].append(i+1)
                except ValueError:
                    print('Ошибка при нахождении позиции биграммы в списке')
                    continue

        # self.printMatrix(self.bigrammsPositions)

        # формируем массив повторений биграмм (не учитывая единичные появления)
        bigramm_counts = []
        for row in xrange(0,len(self.bigrammsPositions)):
            if len(self.bigrammsPositions[row]) > 1:
                bigramm_counts.append(len(self.bigrammsPositions[row]))

        # находим 5 наиболее частых повторений биграмм одного количества
        max_freq_len_arr = []
        counter = collections.Counter(bigramm_counts)
        for row_len,row_count in counter.most_common(5):
            max_freq_len_arr.append(row_len)

        # print(max_freq_len_arr)

        # пробегаем по всем строкам матрицы биграмм нужной длины
        # и определяем возможную длину ключа как разность
        # между следующей и предыдущей позициями
        for row in xrange(0,len(self.bigrammsPositions)):
            if len(self.bigrammsPositions[row]) in max_freq_len_arr:
                for col in xrange(0,len(self.bigrammsPositions[row])-1):
                    diff = self.bigrammsPositions[row][col+1] - self.bigrammsPositions[row][col]
                    self.keyLengthsByBigramms.append(diff)
                    # добавляем Наиб-Общ-Делитель (greatest common divisor)
                    # в список для последующего теста Казиски
                    t = gcd(self.bigrammsPositions[row][col+1], self.bigrammsPositions[row][col])
                    if t > 2:
                        self.gcdLengths.append(t)
        # print(self.keyLengthsByBigramms)

        # находим 5 наиболее частых длин ключа среди возможных
        counter = collections.Counter(self.keyLengthsByBigramms)
        # print(counter.most_common(5))
        self.keyLengthsByBigramms = []
        for key_len,key_count in counter.most_common(5):
            self.keyLengthsByBigramms.append(key_len)


    def findKeyLength_byKaziskyTest(self):
        """
        Метод для определения длины ключа зашифрованного сообщения,
        основанный на нахождении наибольшего ОД позиций биграмм
        (распространенное название - "Тест Казиски")
        """
        counter = collections.Counter(self.gcdLengths)

        # берем 5 наиболее частых НОД длины ключа
        temp = counter.most_common(5)
        for key, value in temp:
            self.keyLengthsGcd.append(key)


    def processKeyLengths(self):
        """
        Метод для анализа и определения длин ключа шифротекста
        в порядке их приоритета для криптоанализа
        """
        print(self.codedMessage)
        print(len(self.codedMessage))
        print(self.keyLengths)
        print(self.keyLengthsByBigramms)
        print(self.keyLengthsGcd)

        # если списки имеют одни и те же длины ключей,
        # то помещаем их в начало финального списка ключей
        temp_set_1 = set(self.keyLengths).intersection(self.keyLengthsByBigramms)
        temp_set_2 = set(self.keyLengths).intersection(self.keyLengthsGcd)
        temp_set_3 = set(self.keyLengthsByBigramms).intersection(self.keyLengthsGcd)
        final_set = set.union(temp_set_1, temp_set_2, temp_set_3)
        self.finalKeyLengths = list(final_set)

        # добавляем остальные длины ключей в порядке возрастания
        temp_arr = []
        for t_len in self.keyLengths:
            if t_len not in self.finalKeyLengths:
                temp_arr.append(t_len)

        for t_len in self.keyLengthsByBigramms:
            if t_len not in self.finalKeyLengths:
                temp_arr.append(t_len)

        for t_len in self.keyLengthsGcd:
            if t_len not in self.finalKeyLengths:
                temp_arr.append(t_len)

        # сортируем массив длин по возрастанию,
        # т.к. анализ проще начинать с наименьшей длины ключа
        temp_arr.sort()

        # пробегаем по низкоприоритетным длинам ключа
        # и помещаем в высокоприоритетный список те длины ключа,
        # которые кратны элементам из него
        pos_to_add = []
        for t_len in self.finalKeyLengths:
            for t_len_2 in temp_arr:
                t = -1
                if t_len > t_len_2:
                    t = t_len % t_len_2
                else:
                    t = t_len_2 % t_len

                if t == 0:
                    pos_to_add.append(t_len_2)

        pos_to_add = list(set(pos_to_add))

        if len(pos_to_add) > 0:
            for t_len in pos_to_add:
                self.finalKeyLengths.append(t_len)
                temp_arr.remove(t_len)

        # сортируем высокоприоритетный список по возрастанию длины ключа,
        # а затем конкатенируем с низкоприоритетным списком
        self.finalKeyLengths.sort()
        self.finalKeyLengths = self.finalKeyLengths + temp_arr

        self.message = "Возможные длины ключа в порядке приоритета: "
        for num in self.finalKeyLengths:
            self.message += str(num)
            self.message += ", "
        self.message = self.message[:len(self.message)-2]


    def checkIndexes(self, key_length):
        """
        Метод для определения корректности найденных длин ключей
        посредством индексов совпадений
        """
        # определяем число строк в матрице
        row_count = len(self.codedMessage)/key_length
        if (float(len(self.codedMessage)) % float(key_length)) > 0.0:
            row_count += 1

        pos = 0
        self.messMatrix = []
        self.alphabetMatrix = []
        self.indexesOfAgreements = []

        # записываем шифротекст в матрицу из N-столбцов,
        # где N - это предполагаемая длина ключа
        for row in xrange(0, row_count):
            self.messMatrix.append([])
            for col in xrange(0,key_length):
                if pos < len(self.codedMessage):
                    self.messMatrix[row].append(self.codedMessage[pos])
                    pos += 1
                else:
                    self.messMatrix[row].append("")

        # self.printMatrix(self.messMatrix)

        # определяем статистику букв по каждому столбцу
        for i in xrange(0,key_length):
            curr_col = self.columnOfMatrix(self.messMatrix, i)
            try:
                curr_col.remove("")
            except ValueError:
                pass

            # считаем статистику и заносим результаты в матрицу
            counter = collections.Counter(curr_col)
            self.alphabetMatrix.append([])
            for elem in ALPHABET:
                try:
                    counts_pos = counter.keys().index(elem)
                    self.alphabetMatrix[i].append(counter.values()[counts_pos])
                except ValueError:
                    self.alphabetMatrix[i].append(0)

        # self.printMatrix(self.alphabetMatrix)

        # определяем сдвиги для каждой строки (кроме первой)
        # матрицы статистики букв для каждого ключа из списка
        self.shiftValuesMatrix.append([])
        is_first = True
        for row in self.alphabetMatrix:
            if is_first:
                is_first = False
                continue
            half_of_row = [row[i] for i in xrange(ALPHABET_HALF+1,len(row))]
            max_value = max(half_of_row)
            max_value_arr = [i for i, j in enumerate(half_of_row) if j == max_value]
            for i in xrange(0, len(max_value_arr)):
                max_value_arr[i] += ALPHABET_HALF + 1

            # если максимальных элементов несколько -
            # рассчитаем взаимный индекс совпадения и выберем нужный
            max_value_pos = 0
            if len(max_value_arr) == 1:
                max_value_pos = max_value_arr[0]
            else:
                max_value_pos = self.getShiftByFirstAndCurrColumns(self.alphabetMatrix[0],
                                                                   row,
                                                                   max_value_arr)
            self.shiftValuesMatrix[len(self.shiftValuesMatrix)-1].append(len(row)-max_value_pos)

        # запоминаем позиции букв с максимальной частотой повторения
        self.statMatrix.append([])
        for row in self.alphabetMatrix:
            max_value = max(row)
            max_value_arr = [i for i, j in enumerate(row) if j == max_value]
            for i in xrange(0, len(max_value_arr)):
                max_value_arr[i] += 1

            # если максимальных элементов несколько -
            # рассчитаем взаимный индекс совпадения и выберем нужный
            max_value_pos = 0
            if len(max_value_arr) == 1:
                max_value_pos = max_value_arr[0]
            else:
                max_value_pos = self.getShiftByFirstAndCurrColumns(self.alphabetMatrix[0],
                                                                   row,
                                                                   max_value_arr)
            self.statMatrix[len(self.statMatrix)-1].append(max_value_pos)

        # определяем индексы совпадений букв по каждому столбцу
        for row in xrange(0,len(self.alphabetMatrix)):
            sum = 0
            for col in xrange(0,len(self.alphabetMatrix[0])):
                sum += self.alphabetMatrix[row][col] * (self.alphabetMatrix[row][col]-1)

            curr_col = self.columnOfMatrix(self.messMatrix, row)
            try:
                curr_col.remove("")
            except ValueError:
                pass
            denominator = len(curr_col) * (len(curr_col)-1)

            # если в колонке 1 строка - алгоритм будет делить на нуль
            try:
                self.indexesOfAgreements.append(float(sum) / float(denominator))
            except ZeroDivisionError:
                self.indexesOfAgreements.append(0)


        # print(self.indexesOfAgreements)

        # пробегаем по найденным индексам, проверяя их значения с 0,0553
        should_add_keylength = True
        for elem in self.indexesOfAgreements:
            if elem < 0.0553:
                should_add_keylength = False
                break

        # если все индексы совпадений для данного ключа удовлетворяют условию,
        # то добавляем его в финальный массив
        if should_add_keylength:
            self.icKeyLengths.append(key_length)


    def getShiftByFirstAndCurrColumns(self, firstCol, currCol, maxValuePos):
        """
        Метод для вычисления взаимных индексов совпадения
        для первой и сдвигаемой колонок
        """
        for curr_pos in maxValuePos:
            # вычисляем сдвиг и сдвигаем статистику букв текущей колонки
            curr_shift = len(ALPHABET) - curr_pos
            deq = collections.deque(currCol)
            deq.rotate(curr_shift)
            currCol_shifted = list(deq)

            # высчитываем взаимный индекс совпадения (mutual IC)
            denominator = sum(firstCol) * sum(currCol)
            s = 0
            for i in xrange(0,len(firstCol)):
                s += firstCol[i] * currCol_shifted[i]
            MIC = float(s) / float(denominator)

            if (MIC >= 0.0249) and (MIC <= 0.0553):
                return curr_pos
            elif maxValuePos.index(curr_pos) == (len(maxValuePos)-1):
                return curr_pos

        return maxValuePos[0]


    def statisticalAnalysis(self):
        """
        Метод для статистического анализа шифротекста
        на основе таблицы частот букв
        """
        if len(self.finalKeyLengths) < 0:
            self.message = "Длину ключа не удалось определить!"
            return

        # пробегаем по всем возможным ключам и исключаем те,
        # для которых индекс совпадений по столбцам ниже
        for key_length in self.finalKeyLengths:
            self.checkIndexes(key_length)

        # выводим результаты обработки по индексам совпадений
        # index of coincidence
        print(self.icKeyLengths)
        self.message += "\n\nДлины ключей, для которых IC допустимый: "
        if len(self.icKeyLengths) > 0:
            for num in self.icKeyLengths:
                self.message += str(num)
                self.message += ", "
            self.message = self.message[:len(self.message)-2]
        else:
            self.message += "таковые отсутствуют"

        # на основе полученных сдвигов вычисляем значение ключа
        for row in self.shiftValuesMatrix:
            self.keyWords.append([])
            for i in xrange(0,len(ALPHABET)):
                keyword = ""
                is_first = True
                for col in row:
                    if is_first:
                        is_first = False
                        keyword = ALPHABET[i]

                    if i >= col:
                        keyword += ALPHABET[i-col]
                    else:
                        k_pos = len(ALPHABET) - (col-i)
                        keyword += ALPHABET[k_pos]
                self.keyWords[len(self.keyWords)-1].append(keyword)

        # выводим результаты в веб-форму
        self.message += "\n\nВычисленные значения ключей:\n\n"
        for row in self.keyWords:
            for keyword in row:
                self.message += keyword.encode('utf-8')
                self.message += ", "
            self.message += "\n\n"


    def statisticalAnalysis_ByFrequency(self):
        """
        Метод для статистического анализа шифротекста
        на основе статистики частот букв русского языка
        """
        # по полученным всплескам частот определяем сдвиги относительно буквы O
        for row in self.statMatrix:
            self.statMatrixShifts.append([])
            for col in row:
                self.statMatrixShifts[len(self.statMatrixShifts)-1].append(col-ALPHABET_HALF)

        # self.printMatrix(self.statMatrixShifts)

        # по вычисленным сдвигам сформируем выражения ключей
        for row in self.statMatrixShifts:
            self.statKeyWords.append([])
            keyword = ""
            for col in row:
                deq = collections.deque(ALPHABET)
                deq.rotate(-col)
                alphabet_shifted = list(deq)
                keyword += alphabet_shifted[0]

            self.statKeyWords[len(self.statKeyWords)-1].append(keyword)

        # выводим результаты в веб-форму
        self.message += "\n\n\n\nПовторно вычисленные значения ключей:\n\n"
        for row in self.statKeyWords:
            for keyword in row:
                self.message += keyword.encode('utf-8')
                self.message += ", "
            self.message += "\n\n"


    def getOriginText(self):
        """
        Метод для непосредственного взлома шифрованного сообщения
        """
        self.findKeyLength_byFridman()
        self.findKeyLength_byKazisky()
        self.findKeyLength_byKaziskyTest()

        # анализ полученных ключей
        self.processKeyLengths()

        # стадия криптоанализа
        self.statisticalAnalysis()
        self.statisticalAnalysis_ByFrequency()

        return self.message