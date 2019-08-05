import qiskit
from . import qclass
import math

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
            self.qubits = self.coerce_size()
        else:
            self.qubits = self.qclass.chunk(size)
        strInit = str(bin(self.initial))[2:]
        strInit = reversed(strInit)
        toWrite = ''
        i = 0
        while i < len(strInit):
            if strInit[i] == '1':
                toWrite += "x q[%d]; \n" % self.qubits[i]
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
        elif self.small and self.initial > 2**5 -1:
            raise OverflowError("initial value is too large to fit in a small int")
        elif self.big and self.initial > 2**32 -1:
            raise OverflowError("initial value is too large to fit in a big int")
        elif self.small:
            return self.qclass.chunk(5)
        elif self.big:
            return self.qclass.chunk(32)
        elif self.initial < 2**14 and maxBits >= 14 and not self.small and not self.big:
            #14 is currently the largest number of qubits on an IBMQ computer so allot that much memory
            return self.qclass.chunk(14)
        elif self.initial < 2**32 - 1 and maxBits >= 32:
            return self.qclass.chunk(32)
        elif self.initial < 2**5 - 1 and maxBits >= 5:
            #5 is the smallest amount of qubits available on a backend
            return self.qclass.chunk(5)
        else:
            return self.qclass.chunk(maxBits)

    def all_vals(self):
        """
        When called on a pure int places the qint into
        a superposition of all possible values
        Applies an h gate to all qubits
        """
        for i in range(len(self.qubits)):
            self.qclass.write("h q[%d]; \n" % self.qubits[i])
        
    def measure(self):
        """
        Measures the stored qint
        returning the list of indices of 
        classical bits the measurements are stored in
        """
        self.classBits = self.qclass.chunk_class(len(self.qubits))
        for i in range(len(self.classBits)):
            self.qclass.write("measure q[%d] " % self.qubits[i] + "-> c[%d]; \n" % self.classBits[i])
    

    def extract_result(self, result):
        """
        Extracts and returns the int from the 
        qclass result
        """
        binaryStr = ''
        for i in self.classBits:
                binaryStr = result[i] + binaryStr
        val = int(binaryStr, 2)
        return val

    def increment(self):
        """
        Increments a qint
        """
        if len(self.qubits) > 3:
            ancqubits = self.qclass.request_chunk(len(self.qubits)-2)
            if ancqubits:
                i = len(self.qubits) - 1
                while i > 2:
                    self.qclass.mct(self.qubits[:i], self.qubits[i], ancillary = ancqubits)
                    i -= 1
                self.qclass.return_chunk(ancqubits)
            else:
                i = len(self.qubits) - 1
                while i > 2:
                    self.qclass.mct(self.qubits[:i], self.qubits[i], ancillary = [])
                    i -= 1
            self.qclass.ccx(self.qubits[0], self.qubits[1], self.qubits[2])
            self.qclass.cx(self.qubits[0], self.qubits[1])
            self.qclass.ugate("x", self.qubits[0])
        elif len(self.qubits) == 3:
            self.qclass.ccx(self.qubits[0], self.qubits[1], self.qubits[2])
            self.qclass.cx(self.qubits[0], self.qubits[1])
            self.qclass.ugate("x", self.qubits[0])
        elif len(self.qubits) == 2:
            self.qclass.cx(self.qubits[0], self.qubits[1])
            self.qclass.ugate("x", self.qubits[0])
        elif len(self.qubits) == 1:
            self.qclass.ugate("x", self.qubits[0])
        else:
            raise ValueError("Can not increment qint which has no qubits (Did you accidently make size=0?)")

    @classmethod
    def quantrand(cls, start, stop, step=1, simulator= False):
        """
        Returns a random quantum integer within the 
        range [start, stop). Utilizes the smallest 
        possible quantum backend unless simulator is set
        to be true
        """
        while True:
            randRange = int(math.ceil((stop - start)/step))
            if simulator:
                backend = "ibmq_qasm_simulator"
            else:
                #Figure out the smallest backend possible
                if randRange > 2**14:
                    raise OverflowError("Currently a quantum random number must have at most 2^14 values")
                elif randRange > 2**5:
                    backend = "ibmq_16_melbourne"
                else:
                    backend = "ibmqx4"
            thisQclass = qclass(backend= backend)
            thisQclass.start()
            thisSize = int(math.ceil(math.log(randRange, 2)))
            thisInt = cls(thisQclass, size=thisSize)
            thisInt.all_vals()
            thisInt.measure()
            result = thisQclass.get_result()
            val = thisInt.extract_result(result)
            val = (val + start) * step
            if val < stop:
                return val
            else:
                continue
