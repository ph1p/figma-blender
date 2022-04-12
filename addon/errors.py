def element_not_found(self, context):
    self.layout.label(
        text="TThe item you are asking for seems to be no longer available!")


def folder_not_writeable(self, context):
    self.layout.label(
        text="The folder is not writeable or does not exist")


def cannot_start_server(self, context):
    self.layout.label(
        text="Cannot start server. This could have the following causes: server already started or port is busy")
