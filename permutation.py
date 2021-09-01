# Uses Heap's algorithm to produce all permutations of a given array
# Produces a one time use generator and does not modify original array
def permutations(array):
    copy = array[:]
    def generate(k, vals):
        if k==1:
            yield vals
        else:
            for g in generate(k-1, vals):
                yield g
            for i in range(k-1):
                if k % 2 == 0:
                    vals[i], vals[k-1] = vals[k-1], vals[i]
                else:
                    vals[0], vals[k-1] = vals[k-1], vals[0]
                for g in generate(k-1, vals):
                    yield g
    return generate(len(copy), copy)