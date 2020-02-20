from lmfit import models


class PolynomialModel(models.PolynomialModel):
    def __init__(self, *args, **kwargs):
        models.PolynomialModel.__init__(self, *args, **kwargs)

    def make_params(self, verbose=False, **kwargs):
        result = models.PolynomialModel.make_params(self, verbose, **kwargs)
        for k in result.keys():
            result[k].value = 0.0
        print(result)
        return result

