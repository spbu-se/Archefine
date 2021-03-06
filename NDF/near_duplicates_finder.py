from NDF import simpleAPI2


class Cl:
    def __init__(self, y, z):
        self.nGrams = y
        self.sents = z


class Node:
    def __init__(self, w, f, n):
        self.word = w
        self.forms = f
        self.count = n


def get_hash(word):
    ans = 0
    modulo = int(1e9 + 7)
    power = 239
    for ch in word:
        ans = (ans * power + ord(ch)) % modulo
    return ans


def get_key(item):
    return item[0]


class StatisticCollector:
    def __init__(self, lang):
        self.size = int(1e5 + 7)
        self.table = []
        self.count_form_words = 0
        self.count_different_words = 0
        self.count_words = 0
        self.count_stop_words = 0
        self.language = lang
        self.popular_word = [0, ""]
        for i in range(self.size):
            self.table.append(Node("", set(), 0))

    def set_text(self, text):
        self.text = text

    def update(self):
        if self.count_words * 2 > self.size:
            self.count_stop_words = 0
            self.count_different_words = 0
            self.count_words = 0
            self.count_form_words = 0
            elements = []
            for node in self.table:
                elements.append(node)
            self.table = []
            self.size *= 2
            for i in range(self.size):
                self.table.append(Node("", set(), 0))
            for node in elements:
                if node.count > 0:
                    self.add_word(node.word, node.count)
                    self.add_form(node.word)

    def get_pos(self, word):
        hash = get_hash(word)
        elem = hash % self.size
        while (self.table[elem].word != word) & (self.table[elem].word != ""):
            elem = (elem + 1) % self.size
        return elem

    def get_count(self, word):
        pos = self.get_pos(word)
        return self.table[pos].count

    def add_word(self, word, num):
        pos = self.get_pos(word)
        if self.table[pos].count == 0:
            self.count_different_words += 1
        if self.text.is_stop_word(word):
            self.count_stop_words += num
        self.count_words += num
        self.table[pos].word = word
        self.table[pos].count += num
        if (self.table[pos].count > self.popular_word[0]) and (not self.text.is_stop_word(word)) and (word.isalpha()):
            self.popular_word = [self.table[pos].count, self.table[pos].word]

    def add_form(self, word):
        init_form = self.text.word_to_stemmed(word)
        pos = self.get_pos(init_form)
        if word not in self.table[pos].forms:
            self.table[pos].forms.add(word)
            self.count_form_words += 1

    def get_forms(self, word):
        init_form = self.text.word_to_stemmed(word)
        pos = self.get_pos(init_form)
        return self.table[pos].forms

    def add_sent(self, sent):
        for word in sent.words:
            self.add_word(word, 1)
            self.add_form(word)
            self.update()

    def get_popularity(self):
        popular = []
        for i in range(self.size):
            if not self.table[i].count == 0:
                popular.append([self.table[i].count, self.table[i].word])
        popular.sort()
        return popular

    def list_of_stop_words(self):
        stop_words = []
        for i in range(self.size):
            if (not self.table[i].count == 0) and (self.text.is_stop_word(self.table[i].word)):
                stop_words.append([self.table[i].count, self.table[i].word])
        stop_words.sort()
        return stop_words

    def get_count_form_words(self):
        return self.count_form_words

    def get_most_popular_word(self):
        return self.popular_word

    def get_count_words(self):
        return self.count_words

    def get_count_stop_words(self):
        return self.count_stop_words

    def get_count_diff_words(self):
        return self.count_different_words

    def statistic(self):
        print("Number words: " + str(self.count_words))
        print("Number different words: " + str(self.count_different_words))
        print("Number stopWords " + str(self.count_stop_words))
        print("Most popular word: " + str(self.popular_word[0]) + " " + self.popular_word[1])
        print(self.get_popularity())


class NearDuplicatesFinder:
    def __init__(self):
        self.classes = []

    def add_sent(self, cur_sent):
        best_overlap = 0
        best_class = 0
        for (j, curClass) in enumerate(self.classes):
            cur_intersect = cur_sent.nGrams & curClass.nGrams
            cur_overlap = sum(cur_intersect.values()) / sum(cur_sent.nGrams.values())

            if cur_overlap > best_overlap:
                best_overlap = cur_overlap
                best_class = j

        if best_overlap < 0.5:
            self.classes.append(Cl(cur_sent.nGrams, [cur_sent]))
        else:
            self.classes[best_class].nGrams += cur_sent.nGrams
            self.classes[best_class].sents.append(cur_sent)

    def list_classes(self):
        ans = []
        cur = 0
        for curClass in self.classes:
            if len(curClass.sents) == 1:
                continue
            cur += 1
            ans.append("========================= CLASS #" + str(cur) + " =============================")
            for sent in curClass.sents:
                ans.append(sent.sent)
            ans.append("*****************************************************************")
        return ans

    def print_classes(self, encoding, filename):
        with open(filename, "w", encoding=encoding) as file:
            cur = 0
            for curClass in self.classes:
                if len(curClass.sents) == 1:
                    continue
                cur += 1
                file.write("========================= CLASS #%d =============================\n" % cur)
                file.write('\n'.join(
                    ["(%d) {%d} [%d]: %s" % (sent.index, sent.start, sent.end, sent.sent) for sent in curClass.sents]))
                file.write("\n*****************************************************************\n")


class Analyzer:
    def __init__(self, path, ID, lang):
        self.name = path
        self.progress = 0
        self.stop = False
        self.ID = ID
        self.ndf = NearDuplicatesFinder()
        self.stc = StatisticCollector(lang)
        self.language = lang
        self.state = 0
        self.groups = []
        self.popular = []

    def get_id(self):
        return self.ID

    def get_popularity(self):
        if self.popular == []:
            self.popular = self.stc.get_popularity()
        return self.popular

    def get_groups(self):
        if self.groups == []:
            self.groups = self.ndf.list_classes()
        return self.groups

    def get_count_form_words(self):
        return self.stc.get_count_form_words()

    def set_progress(self, np):
        self.progress = np

    def get_progress(self):
        return self.progress

    def get_most_popular_word(self):
        return self.stc.get_most_popular_word()

    def get_count_diff_words(self):
        return self.stc.get_count_diff_words()

    def get_count_words(self):
        return self.stc.get_count_words()

    def get_count_stop_words(self):
        return self.stc.get_count_stop_words()

    def get_stop_words(self):
        return self.stc.list_of_stop_words()

    def stop_work(self):
        self.stop = True

    def get_state(self):
        return self.state

    def print_groups(self, filename):
        self.ndf.print_classes(self.text.encoding, filename)

    def work(self):
        if self.name == '':
            self.progress = 0
            return 1

        self.state = 1
        self.text = simpleAPI2.Text(self.name, self)
        if self.stop:
            self.state = -1
            return 2
        self.state = 2

        self.stc.set_text(self.text)
        sents = self.text.sents
        sentences_size = len(sents)

        print(sentences_size)
        for (i, curSent) in enumerate(sents):
            self.progress = 20 + 80 * (i + 1) / sentences_size
            if self.stop:
                self.state = -1
                return 2
            self.stc.add_sent(curSent)
            if len(curSent.nGrams) == 0:
                continue
            self.ndf.add_sent(curSent)

        self.state = 3
        return 0
