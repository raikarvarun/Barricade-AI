from collections import deque
import random

class ReplayBuffer:

    def __init__(self,size=100000):

        self.buffer = deque(maxlen=size)

    def push(self,s,a,r,ns,d):

        self.buffer.append(
            (s,a,r,ns,d)
        )

    def sample(self,batch_size):

        batch = random.sample(
            self.buffer,
            batch_size
        )

        s,a,r,ns,d = zip(*batch)

        return s,a,r,ns,d

    def __len__(self):
        return len(self.buffer)