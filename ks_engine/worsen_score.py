#! /usr/bin/python


class AbstractWorsenScore:
    def __init__(self, total):
        self.score = 0
        self.total = total

    def get_probability(self):
        raise NotImplemented

    def increase_total(self):
        self.total += 1

    def increase_score(self):
        self.score += 1


class WorsenScore(AbstractWorsenScore):
    def __init__(self, total):
        super().__init__(total)

    def get_probability(self):
        prob = self.score / self.total
        return prob


class MockWorsenScore(AbstractWorsenScore):
    def __init__(self, total):
        super().__init__(total)

    def get_probability(self):
        return 0
