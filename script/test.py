
if __name__ == '__main__':
    print("\n".join(" ".join([f"{y}X{x}={x * y}" for y in range(1, x + 1)]) for x in range(1, 10)))

    for x in range(1, 10):
        for y in range(1, x + 1):
            print(f'{y}X{x}={x * y:2}', end=' ')
            if y == x:
                print()  # 相当于\n
