import abc


class Rephraser(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def process(input_data):
        ''' Returns processed question. '''
