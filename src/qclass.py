import qiskit
import uuid
import random

class qclass(object):
    """
    Abstract class used as a starting point for quantum data structures
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
        self.qasmDir += '.txt'
        self.output = open(self.qasmDir, 'a+')
        self.ran = False

    @property
    def bitsLeft(self):
        return len(self._availableQubits) + 1

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
            self._nextClassBit = self._availableClassBits.pop()
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
            toReturn.append(self._nextQubit)
            self._nextQubit = self._availableQubits.pop()
        return toReturn

    def return_chunk(self, bits: list):
        """
        Returns a list of temporary qubits to available qubits
        Be sure to reset these qubits to be 0 before returning them
        """
        self._availableQubits += bits

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
        OPENQASM 2.0; \n
        include "qelib1.inc"; \n
        qreg q[$$QSIZE$$]; \n
        creg c[$$CSIZE$$]; \n
        """
        toWrite.replace("$$QSIZE$$", str(quantSize))
        toWrite.replace("$$CSIZE$$", str(classSize))
        self.output.write(toWrite)
        self.size = quantSize
        self._availableQubits = [x for x in range(0, self.size)]
        self._nextQubit = self._availableQubits.pop()
        self._availableClassBits = [x for x in range(0, classSize)]
        self._nextClassBit = self._availableClassBits.pop()

    def _initialize_backend(self, backend="ibmq_qasm_simulator"):
        self.backend = qiskit.IBMQ.get_provider().backends(backend)[0]

    def run(self):
        """
        Runs the compiled circuit
        returns a qiskit results object
        Use get_result to get a single result
        """
        self.circuit = qiskit.QuantumCircuit.from_qasm_file(self.qasmDir)
        self.ran = True
        return qiskit.execute(self.circuit, backend= self.backend)
    
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