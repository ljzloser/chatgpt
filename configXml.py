import os
from xml.etree import ElementTree


class Config:
    def __init__(self, config_file='config.xml'):
        self.config_file = config_file
        self.config = ElementTree.Element('config')

        if os.path.exists(config_file):
            self.config = ElementTree.parse(config_file).getroot()
        else:
            self.save()

    def read(self, name, default=None):
        node = self.config.find(name)
        return node.text if node is not None else default

    def write(self, name, value):
        node = self.config.find(name)
        if node is None:
            node = ElementTree.Element(name)
            self.config.append(node)
        node.text = str(value)
        self.save()

    def save(self):
        ElementTree.ElementTree(self.config).write(self.config_file, encoding='utf-8', xml_declaration=True)
