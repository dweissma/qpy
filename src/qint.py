import qiskit
from . import qclass
import math
from warnings import warn

class qint(object):
    """
    Quantum integer class
    """
    def __init__(self, qclass, value= 0, size=None, small=False, big=False):
        self.qclass = qclass
        self.initial = value
        self.big = big
        self.small = small
        self.firstQubit = None #The qubit that should be measured first if applicable
        if not size:
            self.qubits = self.smart_chunk()
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

    def smart_chunk(self):
        """
        Attempts to somewhat intelligently decide
        on a reasonable amount of qubits to be allotted
        Returns the properly sized chunk
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

    @classmethod
    def coerce_size(cls, qclass, intial, small=False, big=False):
        """
        Attempts to somewhat intelligently decide
        on a reasonable amount of qubits to be allotted
        Returns the number
        """
        maxBits = qclass.bitsLeft
        if initial > (2**maxBits) - 1:
            #There aren't enough bits left to initialize such a large number
            raise OverflowError("initial value is too large to fit into available qubits")
        elif small and initial > 2**5 -1:
            raise OverflowError("initial value is too large to fit in a small int")
        elif big and initial > 2**32 -1:
            raise OverflowError("initial value is too large to fit in a big int")
        elif small:
            return 5
        elif big:
            return 32
        elif initial < 2**14 and maxBits >= 14 and not small and not big:
            #14 is currently the largest number of qubits on an IBMQ computer so allot that much memory
            return 14
        elif initial < 2**32 - 1 and maxBits >= 32:
            return 32
        elif initial < 2**5 - 1 and maxBits >= 5:
            #5 is the smallest amount of qubits available on a backend
            return 5
        else:
            return maxBits

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
        self.qclass.collapsed = True
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


    @classmethod
    def super_position(cls, nums, qclass, size=None, small=False, big=False):
        """
        Returns a qint object which is a 
        superposition of each number
        """
        largest = max(nums)
        size = cls.coerce_size(qclass, largest, small=small, big=big)
        thisQint = cls(qclass, size=size)
        bnums = [bin(x)[-1:2:-1] for x in nums]
        i = len(bnums) - 1
        tempChunk = qclass.chunk(1)
        tempBit = tempChunk[0]
        while i > 0:
            mem = []
            if all([x[i] == '0' for x in bnums]):
                #This state can be a pure 0 entangled to nothing
                pass
            elif all([x[i] == '1' for x in bnums]):
                #This state can be a pure 1 entangled to nothing
                thisQint.qclass.ugate("x", thisQint.qubits[i])
            else:
                #The state is not pure so we have to do some entangling
                for k in range(i):
                    thisQint.qclass.ugate("h", thisQint.qubits[k]) #Place all the previous qubits in a superposition
                for strings in bnums:
                    substring = strings[:i]
                    if substring not in mem:
                        mem.append(substring)
                        toEntangle = [x for x in bnums if x.startswith(substring)] #All strings with the prefix
                        if all([x[i] == '0' for x in toEntangle]):
                            #We don't have to do anything here either
                            pass
                        elif all([x[i] == '1' for x in toEntangle]):
                            #Controlled not this position
                            for pos in range(len(substring)):
                                if substring[pos] == '0':
                                    thisQint.qclass.ugate('x', thisQint.qubits[pos])
                            ancillary = thisQint.qclass.request_chunk(i-2)
                            thisQint.qclass.mct(thisQint.qubits[:i], tempBit, ancillary = ancillary)
                            thisQint.qclass.cx(tempBit, thisQint[i])
                            thisQint.qclass.mct(thisQint.qubits[:i], tempBit, ancillary = ancillary)
                            for pos in range(len(substring)):
                                if substring[pos] == '0':
                                    thisQint.qclass.ugate('x', thisQint.qubits[pos])
                            if ancillary:
                                qclass.return_chunk(ancillary)
                        else:
                            #Controlled q_prob at this position
                            for pos in range(len(substring)):
                                if substring[pos] == '0':
                                    thisQint.qclass.ugate('x', thisQint.qubits[pos])
                            prob = len([x for x in toEntangle if x[i] == '1'])/len(toEntangle) #Probability that this pos is 1 with the current substring
                            ancillary = thisQint.qclass.request_chunk(i-2)
                            thisQint.qclass.mct(thisQint.qubits[:i], tempBit, ancillary = ancillary)
                            thisQint.qclass.cprob(tempBit, thisQint[i], prob)
                            thisQint.qclass.mct(thisQint.qubits[:i], tempBit, ancillary = ancillary)
                            for pos in range(len(substring)):
                                if substring[pos] == '0':
                                    thisQint.qclass.ugate('x', thisQint.qubits[pos])
                            if ancillary:
                                qclass.return_chunk(ancillary)
                for k in range(i):
                    thisQint.qclass.ugate("h", thisQint.qubits[k])
            i -= 1
        prob = len([x for x in bnums if x[0] == '1'])/len(bnums)
        thisQint.qclass.q_prob(thisQint[0], prob)
        thisQint.firstQubit = thisQint.qubits[0]
        qclass.return_chunk(tempChunk)

    def measure_sup(self):
        """
        Special measurement technique for insuring 
        superpositions have the proper probabilities
        """
        self.measure_safe(self.firstQubit)

    def measure_safe(self, first):
        """
        Measures qints
        also warns the user if measurements on other qubits
        have already been made which may affect the current measurement
        """
        if self.qclass.collapsed:
            warn("Warning: qubits on this qclass have collapsed if qubits were entangled it could effect measurements", RuntimeWarning)
        self.classBits = self.qclass.chunk_class(len(self.qubits))
        firstI = self.qubits.index(first)
        self.qclass.write("measure q[%d] " % first + "-> c[%d]; \n" % self.classBits[firstI])
        for i in range(len(self.classBits)):
            if i != firstI:
                self.qclass.write("measure q[%d] " % self.qubits[i] + "-> c[%d]; \n" % self.classBits[i])

    def extract_counts(self, counts: dict):
        """
        Extract the counts from a counts dict
        returns a dict with the observed values as
        the keys and the counts as values
        """
        toReturn = {}
        for string, count in counts.items():
            result = self.extract_result(string)
            toReturn[result] = count
        return toReturn