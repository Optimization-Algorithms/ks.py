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
        """
        Insert into the log list a new record.

        :param iter_count: the number of the iteration.
        :param var_count: the number of variable.
        :param result: the result.
        """
        if result:
            _, result = result
        data = (iter_count, var_count, result)
        self.log.append(data)

    def save(self):
        with open(self.file_name, "w") as file:
            csv_writer = csv.writer(file)
            for entry in self.log:
                csv_writer.writerow(entry)


def feature_logger_factory(file_name=None):
    """
    Construct a logger.

    If a file_name is provided than will be able to save in a CSV file.

    :param file_name: the name of the CSV file to use for saving, defaults to None
    :type file_name: str, optional
    :return: a logger object
    :rtype: :class:`~Logger`
    """
    if file_name:
        return CSVFeatureLogger(file_name)
    else:
        return MockLogger()
