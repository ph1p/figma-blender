def element_not_found(self, context):
    self.layout.label(
        text="The element you're asking for seems not to be available anymore!")

def folder_not_writeable(self, context):
    self.layout.label(
        text="The folder is not writeable or does not exist")