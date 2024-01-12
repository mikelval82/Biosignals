# -*- coding: utf-8 -*-
"""
SlotsManager class for managing and triggering callbacks.

@author: Mikel Val Calvo
@email: mikel1982mail@gmail.com
@institution: Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED)
@DOI: 10.5281/zenodo.3759262
"""


class SlotsManager:
    """
    A class for managing and triggering callbacks.
    """

    def __init__(self):
        """
        Initialize an instance of the SlotsManager class.
        """
        self.callbacks = []

    def trigger(self):
        """
        Trigger all registered callbacks.

        :return: None
        """
        [callback() for callback in self.callbacks]

    def append(self, slot):
        """
        Append a callback function to the list of callbacks.

        :param slot: The callback function to append.
        :return: None
        """
        self.callbacks.append(slot)
        print(slot)
