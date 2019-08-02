"""
Test cases for the core modules
"""

import unittest
import qiskit
import os
from src import qclass

class BaseTestQclass(unittest.TestCase):
    """
    Tests the basic methods of the qclass
    """
    def setUp(self):
        qiskit.IBMQ.load_account()
        self.qclass = qclass()
        self.qclass.initialize_quantum_registers()
        
    def tearDown(self):
        try:
            os.remove(self.qclass.qasmDir)
        except:
            print("Couldn't remove compiled OpenQASM at %s location" % self.qclass.qasmDir)

    def test_creates_file(self):
        """
        Tests whether a file is properly created
        """
        self.assertTrue(os.path.exists(self.qclass.qasmDir))
    
    def test_size_backend(self):
        """
        Tests whether the backend size is properly assigned
        """
        self.assertEqual(self.qclass.size, 32) #IBMQ qasm simulator has 32 qubits change this test if that changes or the default changes
        
    def test_will_run(self):
        try:
            qclass.run()
        except:
            raise AssertionError("qclass failed to run without adding anything")


class InitTestQclass(unittest.TestCase):
    """
    Tests corner cases of initializing a qclass
    """
    def setUP(self):
        qiskit.IBMQ.load_account()

    def tearDown(self):
        try:
            self.qclass.run()
            os.remove(self.qclass.qasmDir)
        except:
            os.remove(self.qclass.qasmDir)
            raise AssertionError("qClass no longer runs for this case")

    def test_str_backend(self):
        """
        Tests whether the backend can be changed with a string
        """
        self.qclass = qclass(backend= "ibmqx4")
        self.qclass.initialize_quantum_registers() 
        self.qclass.run()
    
    def test_real_backend(self):
        """
        Tests whether one can pass an IBMQ backend
        """
        provider = qiskit.IBMQ.get_provider()
        backend = provider.backends("ibmqx4")[0]
        self.qclass = qclass(backend= backend)
        self.qclass.initialize_quantum_registers()
        self.qclass.run()

    def test_other_dir(self):
        """
        Tests the ability to specify a DIR for the QASM file
        """
        self.qclass = qclass(qasmDir= "TestDir")
        self.qclass.initialize_quantum_registers()
        self.qclass.run()
    
    