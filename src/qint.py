import qiskit
from . import qclass

class qint(object):
    """
    Quantum integer class
    """

    def __init__(self, qclass, value= 0, size=None, small=False, big=False):
        self.qclass = qclass
        self.initial = value
        self.big = big
        self.small = small
        if not size:
            self.bounds = self.coerce_size()
        else:
            self.bounds = self.qclass.chunk(size)
        strInit = str(bin(self.initial))[2:]
        strInit = reversed(strInit)
        toWrite = ''
        i = 0
        while i < len(strInit):
            currentbit = i + self.bounds[0]
            if strInit[i] == '1':
                toWrite += "x q[%d] \n" % currentbit
            i += 1
        self.qclass.write(toWrite)

    def coerce_size(self):
        """
        Attempts to somewhat intelligently decide
        on a reasonable amount of qubits to be allotted
        """
        maxBits = self.qclass.bitsLeft
        if self.initial > (2**maxBits) - 1:
            #There aren't enough bits left to initialize such a large number
            raise OverflowError("initial value is too large to fit into available qubits")
        elif self.initial < 2**14 and maxBits >= 14 and not self.small and not self.big:
            #14 is currently the largest number of qubits on an IBMQ computer so allot that much memory
            return self.qclass.chunk(14)
        elif self.initial < 2**32 - 1 and maxBits >= 32 and self.big:
            return self.qclass.chunk(32)
        elif self.initial < 2**5 - 1 and maxBits >= 5 and self.small:
            #5 is the smallest amount of qubits available on a backend
            return self.qclass.chunk(5)
        else:
            return self.qclass.chunk(maxBits)
