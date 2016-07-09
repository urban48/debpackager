from debpackager.packages.general_package import GeneralPackage


class General(GeneralPackage):
    def __init__(self, kwargs):
        super(General, self).__init__(**kwargs)
