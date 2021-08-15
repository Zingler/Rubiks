class IndexedQueue:
    def __init__(self):
        self.heap = [()] # Null element at index 0
        self.index = {}

    def _add(self, priority, object):
        self.heap.append((priority, object))
        index = len(self.heap) - 1
        self.index[object] = index
        self._siftup(index)

    def add_or_update(self, priority, object):
        existing = self.get(object)
        if not existing:
            self._add(priority, object)
        else:
            index = self.index[object]
            self.heap[index] = (priority, object)

            if priority < existing[0]:
                self._siftup(index)
            else:
                self._siftdown(index)


    def get(self, object):
        index = self.index.get(object)
        if index:
            return self.heap[index]
        else:
            return None

    def size(self):
        return len(self.heap) - 1

    def empty(self):
        return self.size() == 0

    def pop(self):
        last_index = len(self.heap) - 1
        self._swap(1, last_index)

        ret_val = self.heap.pop()
        if not self.empty():
            self._siftdown(1)


        del self.index[ret_val[1]]
        return ret_val

    def _swap(self, i, j):
        a = self.heap[i]
        b = self.heap[j]
        self.heap[i], self.heap[j] = b, a
        self.index[a[1]], self.index[b[1]] = j, i


    @staticmethod
    def parent(index):
        return index // 2

    @staticmethod
    def left(index):
        return index * 2
        
    @staticmethod
    def right(index):
        return index * 2 + 1


    def _siftup(self, index):
        if index == 1:
            return
        o = self.heap[index]
        p_i = IndexedQueue.parent(index)
        p = self.heap[p_i]

        if o[0] < p[0]:
            self._swap(index, p_i)
            self._siftup(p_i)

    def _siftdown(self, index):
        left_i = IndexedQueue.left(index)
        right_i = IndexedQueue.right(index)
        left = None
        right = None
        parent = self.heap[index]

        if left_i < len(self.heap):
            left = self.heap[left_i]
        if right_i < len(self.heap):
            right = self.heap[right_i]

        if left == None and right == None:
            return
        elif right == None:
            if left[0] < parent[0]:
                self._swap(index, left_i)
                self._siftdown(left_i)
        else:
            if left[0] < right[0]:
                if left[0] < parent[0]:
                    self._swap(index, left_i)
                    self._siftdown(left_i)
            else:
                if right[0] < parent[0]:
                    self._swap(index, right_i)
                    self._siftdown(right_i)

if __name__ == "__main__":
    q = IndexedQueue()
    q.add_or_update(9, "c")
    q.add_or_update(2, "b")
    q.add_or_update(5, "d")
    q.add_or_update(1, "a")
    q.add_or_update(3, "c")
    q.add_or_update(0, "!")
    q.add_or_update(9, "!")

    while not q.empty():
        print(q.pop())
