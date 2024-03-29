from __future__ import annotations
from qiskit import QuantumCircuit, QuantumRegister, execute, IBMQ
from qiskit.aqua.circuits.gates import mct
import uuid
import random
import math
import re

class qclass(object):
    """
    Abstract class used as a backend for quantum data structures
    Keeping a set of quantum registers and qubits
    One qclass compiles to a single quantum circuit
    """
    def __init__(self, backend= None, qasmDir= uuid.uuid4().hex):
        """
        Initialize a qasm file and choose a backend
        """
        if not backend:
            self._initialize_backend()
        elif type(backend) == str:
            self._initialize_backend(backend)
        else:
            self.backend = backend
        self.size = self.backend.configuration().n_qubits
        self.qasmDir = qasmDir
        self.qasmDir += '.txt' #TO DO tests and change to .qasm
        self.output = open(self.qasmDir, 'a+')
        self.collapsed = False

    @property
    def bitsLeft(self):
        if self._nextQubit is not None:
            return len(self._availableQubits) + 1
        else:
            return 0

    def write(self, toWrite):
        self.output.write(toWrite)

    def chunk_class(self, bits: int):
        """
        Returns a list of available classical registers
        """
        if bits <= 0:
            raise ValueError("bits must be a positive integer")
        if bits > len(self._availableClassBits) + 1:
            raise OverflowError("Insufficient classical bits on the chosen backend")
        toReturn = []
        while len(toReturn) < bits:
            toReturn.append(self._nextClassBit)
            self._nextClassBit = self._availableClassBits.pop(0)
        return toReturn

    def chunk(self, bits: int):
        """
        Allots qubits from memory
        Returns a list of qubit indices  
        """
        if bits <= 0:
            raise ValueError("bits must be a positive integer")
        if bits > len(self._availableQubits) + 1:
            raise OverflowError("Insufficient qubits on the chosen backend")
        toReturn = []
        while len(toReturn) < bits:
            try:
                toReturn.append(self._nextQubit)
                self._nextQubit = self._availableQubits.pop(0)
            except IndexError:
                self._nextQubit = None
        return toReturn

    def return_chunk(self, bits: list):
        """
        Returns a list of temporary qubits to available qubits
        Be sure to reset these qubits to be 0 before returning them
        """
        self._availableQubits += bits
        if self._nextQubit is None and bits:
            self._nextQubit = self._availableQubits.pop(0)

    def start(self, quantSize= None, classSize= None):
        """
        provides the starting point for the qasm file
        """
        if quantSize is None:
            quantSize = self.size
        if classSize is None:
            classSize = self.size  
        if quantSize > self.size: #size is currently assigned to the max possible size for the backend
            raise ValueError("given quantsize is larger than the number of available qubits")
        self._initialize_quantum_registers(quantSize= quantSize, classSize= classSize)

    def _initialize_quantum_registers(self, quantSize= None, classSize= None):
        if quantSize is None:
            quantSize = self.size
        if classSize is None:
            classSize = self.size 
        toWrite = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[$$QSIZE$$]; 
        creg c[$$CSIZE$$]; \n
        """
        toWrite = toWrite.replace("$$QSIZE$$", str(quantSize))
        toWrite = toWrite.replace("$$CSIZE$$", str(classSize))
        self.output.write(toWrite)
        self.size = quantSize
        self._availableQubits = [x for x in range(0, self.size)]
        self._nextQubit = self._availableQubits.pop(0)
        self._availableClassBits = [x for x in range(0, classSize)]
        self._nextClassBit = self._availableClassBits.pop(0)

    def _initialize_backend(self, backend="ibmq_qasm_simulator"):
        #self.backend = IBMQ.get_backend(backend)
        #TO-DO once IBMQ.get_provider() actually works use that
        self.backend = IBMQ.get_provider().get_backend(backend)


    def run(self):
        """
        Runs the compiled circuit
        returns a qiskit results object
        Use get_result to get a single result
        """
        self.output.close()
        self.circuit = QuantumCircuit.from_qasm_file(self.qasmDir)
        self.collapsed = True
        return execute(self.circuit, backend= self.backend)
    
    def get_result(self):
        """
        Returns the result that occurred
        the most times during runs
        randomly breaking ties
        """
        result = self.run()
        counts = result.result().get_counts()
        maxVal = max(counts.values())
        choices = [x for x, y in counts.items() if y == maxVal]
        return random.choice(choices)[::-1] #Reverse the string so that the index matches that assigned by chunk 

    def ccx(self, a: int, b: int, c: int):
        """
        Applies the ccx gate with a and b as control qubits
        and c as the bit to be flipped
        """
        self.write("ccx q[%d]," % a, + " q[%d]," % b + " q[%d]; \n" % c)

    def cx(self, a: int, b: int):
        """
        Applies the controled bit flip
        gate to b using a as a control qubit
        """
        self.write("cx q[%d]," % a + " q[%d]; \n" % b)

    def ugate(self, gate, a: int):
        """
        Applies a unary gate represented by a string
        to qubit a
        """
        self.write(gate + " q[%d]; \n" % a)

    def request_chunk(self, size: int):
        """
        Checkes if enough available qubits exist to 
        serve a chunk and returns the bits if so or False
        if not
        """
        if size <= 0:
            return []
        if size > self.bitsLeft:
            return False
        else:
            toReturn = []
            while len(toReturn) < size:
                toReturn.append(self._nextQubit)
                self._nextQubit = self._availableQubits.pop()
        return toReturn

    def mct(self, control: list, target: int, ancillary= []):
        """
        A controlled not gate with an arbritrary number
        of qubits
        """
        if not ancillary:
            q = QuantumRegister(len(control) + 1)
            qc = QuantumCircuit(q)
            controls = [q[i] for i in range(len(control))]
            qc.mct(controls, q[len(controls)], None, mode='noancilla')
            toWrite = qc.qasm()
            qreg = toWrite.index("qreg ") + 5
            regI = toWrite[qreg:toWrite.index("]", start=qreg)]
            toWrite.replace(regI, 'q')
            for i in range(len(control)):
                toWrite.replace('q[' + i + ']', 'q[' + control[i] + ']')
            toWrite.replace('q[' + len(control) + ']', 'q[' + target + ']')
        else:
            q = QuantumRegister(len(control) + len(ancillary) + 1)
            qc = QuantumCircuit(q)
            controls = [q[i] for i in range(len(control))]
            ancillaries = [q[i + len(control)] for i in range(len(ancillary))]
            qc.mct(controls, q[len(controls) + len(ancillaries)], ancillaries, mode='basic')
            toWrite = qc.qasm()
            qreg = toWrite.index("qreg ") + 5
            regI = toWrite[qreg:toWrite.index("]", start=qreg)]
            toWrite.replace(regI, 'q')
            for i in range(len(control)):
                toWrite.replace('q[' + i + ']', 'q[' + control[i] + ']')
            for i in range(len(ancillary)):
                currentI = i + len(control)
                toWrite.replace('q[' + currentI + ']', 'q[' + ancillary[i] + ']')
            toWrite.replace('q[' + (len(control) + len(ancillary)) + ']', 'q[' + target + ']')
        toWrite = toWrite[toWrite.index("h q["):]
        self.write(toWrite)

    def q_prob(self, target: int, prob: float):
        """
        Places a qubit in a state that has a 
        probability of prob of observing a 1
        Assumes the qubit begins in a |"0"> state
        """
        theta = math.asin(math.sqrt(prob))
        self.write("rx(%d) " % 2*theta + "q[%d]; \n" % target)

    def cprob(self, control: int, target: int, prob: float):
        """
        Places a qubit into a probability if the control gate 
        Assumes the target begins in a |"0"> state
        """
        theta = math.asin(math.sqrt(prob))
        self.ugate("h", target)
        self.write("crz(%d) " % 2*theta + "q[%d] " % control + "q[%d]; \n" % target)
        self.ugate("h", target)

    def get_counts(self):
        """
        Returns the counts for each result
        """
        result = self.run()
        counts = result.result().get_counts()
        return counts

        