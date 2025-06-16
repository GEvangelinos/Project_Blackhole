def main():
    with open('video.mpe', 'rb') as fin:
        x = fin.read()
    with open('repl.mp4', 'wb') as fout:
        fout.write(x)

    print(x)
if __name__ == '__main__':
    main()