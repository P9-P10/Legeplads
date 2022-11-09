class Structure:
    def copy(self):
        pass

    def transform(self, transformation):
        copy = self.copy()
        transformation(copy)
        return copy
