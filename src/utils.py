def words_in_file(f):
    for line in f:
        for word in line.strip().split():
            yield word
