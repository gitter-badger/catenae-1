#!/usr/bin/env python
# -*- coding: utf-8 -*-

from catenae import Link, Electron, util
import logging
import random

class MiddleLinkSync(Link):
    def setup(self):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(f'{self.__class__.__name__} -> setup()')
        logging.debug(f'{self.__class__.__name__} -> input_topics: {self.input_topics}')
        logging.debug(f'{self.__class__.__name__} -> output_topics: {self.output_topics}')

    def transform(self, electron):
        logging.debug(f'{self.__class__.__name__} -> transform()')
        logging.debug(f'{self.__class__.__name__} -> received key: {electron.key}, value: {electron.value}')
        electron.key = electron.key + '_transformed_sync'
        electron.value = electron.value + '_transformed_sync'
        logging.debug(f'{self.__class__.__name__} -> previous topic: {electron.previous_topic}')

        if random.randint(0,10) == 7:
            if "input2" not in self.input_topics:
                self.add_input_topic("input2")
                logging.debug(f'{self.__class__.__name__} -> INPUT CHANGED {self.input_topics}')
            else:
                self.remove_input_topic("input2")
                logging.debug(f'{self.__class__.__name__} -> INPUT CHANGED {self.input_topics}')

        return electron

if __name__ == "__main__":
    MiddleLinkSync().start(consumer_group='custom_group_2', sync=True)