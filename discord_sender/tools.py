def ziplist(list1, list2, checkeq=lambda x, y: x == y):
    zipped = []
    for i in list1:
        for j in list2:
            if checkeq(i, j):
                zipped.append((i, j))
    return zipped
