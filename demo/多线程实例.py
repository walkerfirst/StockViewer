import multiprocessing

'''一个进程模拟写数据'''


def data_file(q):
    data = [1, 2, 3, 4]
    '''模拟已经有下载好的数据data'''

    '''向队列中写入数据'''
    for temp in data:
        q.put(temp)

    print("---下载器已经下载完了数据并且存入到队列中---")


'''一个进程模拟处理数据'''


def modify_data(q):
    complete = []
    '''从对列中获取数据'''
    while True:
        data = q.get()
        complete.append(data)
        '''数据处理'''
        if q.empty():
            break

    print(complete)


def main():
    # 创建一个队列、
    q = multiprocessing.Queue()

    '''创建多个进程，将队列的引用当做实参进行传递到里面'''
    p1 = multiprocessing.Process(target=data_file, args=(q,))
    p2 = multiprocessing.Process(target=modify_data, args=(q,))
    p1.start()
    p2.start()


if __name__ == '__main__':
    main()
