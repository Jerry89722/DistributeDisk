#带有参数的装饰器
import time


class DECO:
    mm = 3

    def deco(self, fun):
        def wrapper(self, a, b):
            startTime = time.time()
            fun(self, a, b)
            endTime = time.time()
            msecs = (endTime - startTime)*1000
            print("time is %d ms" % msecs)
            print("self mm:", self.mm)
        return wrapper

    @deco
    def func(self, a, b):
        print("hello，here is a func for add :")
        time.sleep(1)
        print("result is %d" % (a+b))


if __name__ == '__main__':
    d = DECO()
    d.func(3, 4)
    #func()
