
import random


class Interface(object):
    def __init__(self, Model):
        self.property_name = 'custom1'
        self.property_description = 'This is a custom classifier test.'
        self.property_type = 'int'
        self.model = Model

    def compute_label(self, Param):
        return random.randint(0,10)
