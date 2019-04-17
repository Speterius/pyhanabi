def find_missing(full_set, partial_set):
    for f in full_set:
        if f in partial_set:
            full_set.remove(f)
    return full_set

