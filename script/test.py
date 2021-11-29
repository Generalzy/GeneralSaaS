li = [1, ]

for i in li:
    if len(li) > 100:
        break
    for j in range(10):
        li.append(j)
    print(li)
