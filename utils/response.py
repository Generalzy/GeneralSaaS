class ApiResponse:
    def __init__(self, code=1, msg='成功'):
        self.__dict__['code'] = code
        self.__dict__['msg'] = msg

    @property
    def data(self):
        return self.__dict__

