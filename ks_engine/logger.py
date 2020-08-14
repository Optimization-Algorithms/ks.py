#! /usr/bin/python

import csv


class Logger:

    def log_data(self, *data):
        pass

    def save(self):
        pass

class MockLogger(Logger):
    pass

class CSVFeatureLogger(Logger):

    def __init__(self, file_name):
        super().__init__()
        self.log = []
        self.file_name = file_name

    def log_data(self, iter_count, var_count, result):
        if result:
            _, result = result
        data = (iter_count, var_count, result)
        self.log.append(data)

    def save(self):
        with open(self.file_name, "w") as file:
            csv_writer = csv.writer(file)
            for entry in self.log:
                csv_writer.writerow(entry)
    

def feature_logger_factory(file_name):
    if file_name:
        return CSVFeatureLogger(file_name)
    else:
        return MockLogger()
                





