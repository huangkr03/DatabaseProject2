# _*_ coding : utf-8 _*_
# @Time : 2022/5/3 17:45
# @Author : 黄柯睿
# @File : Test
# @Project : Database

def get(i):
    return i


if __name__ == '__main__':
    result = [[1, 2, 3], [5, 2, 3], [6, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], ]
    a = [i[0] for i in result]
    m = [(max(a[i] for a in result) + 1) for i in range(len(result[0]))]
    s = [('%-' + str(i) + 's') for i in m]
    print(s)
    print('%-30s %-20s' % ('300000000000000', '40'))

    a = [2, 3, 4]
    tuple(a)
    print('%d %d %d' % tuple(a))

    a = {1: 3}
    print(a.get(2))
