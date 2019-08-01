import qiskit
import uuid

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
        
    def initialize_quantum_registers(self, quantSize= self.size, classSize= self.size):
        toWrite = """
        OPENQASM 2.0; \n
        include "qelib1.inc"; \n
        qreg[$$QSIZE$$]; \n
        creg[$$CSIZE$$]; \n
        """
        toWrite.replace("$$QSIZE$$", str(quantSize))
        toWrite.replace("$$CSIZE$$", str(classSize))
        self.output.write(toWrite)

    def _initialize_backend(self, backend="ibmq_qasm_simulator"):
        self.backend = qiskit.IBMQ.get_provider().backends(backend)[0]

    def run(self):
        self.circuit = qiskit.QuantumCircuit.from_qasm_file(self.qasmDir)
        return qiskit.execute(self.circuit, backend= self.backend)
