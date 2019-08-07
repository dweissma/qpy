"""
Test cases for the core modules
"""

import unittest
import qiskit
import os
from src.qclass import qclass
from src.qint import qint

class BaseTestQclass(unittest.TestCase):
    """
    Tests the basic methods of the qclass
    """
    def setUp(self):
        qiskit.IBMQ.load_account()
        self.qclass = qclass()
        self.qclass.start()
        
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

    def test_chunk(self):
        """
        tests whether the chunk method 
        """
        chunk = self.qclass.chunk(3)
        self.assertEqual([0, 1, 2], chunk)

    def test_chunk_overlap(self):
        """
        tests whether chunks overlap
        """
        chunk1 = self.qclass.chunk(8)
        chunk2 = self.qclass.chunk(8)
        for bits in chunk1:
            self.assertFalse(bits in chunk2)
    
    def test_chunk_error(self):
        """
        tests whether chunk properly errors
        """
        chunk1 = self.qclass.chunk(20)
        self.assertRaises(OverflowError, self.qclass.chunk(20))

    def test_request_chunk(self):
        """
        tests whether request chunk works as intended
        """
        chunk = self.qclass.request_chunk(10)
        while chunk:
            self.assertTrue(len(chunk) == 10)
            chunk = self.qclass.request_chunk(10)
        self.assertFalse(chunk)

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
        self.qclass.start() 
        self.qclass.run()
    
    def test_real_backend(self):
        """
        Tests whether one can pass an IBMQ backend
        """
        provider = qiskit.IBMQ.get_provider()
        backend = provider.backends("ibmqx4")[0]
        self.qclass = qclass(backend= backend)
        self.qclass.start()
        self.qclass.run()

    def test_other_dir(self):
        """
        Tests the ability to specify a DIR for the QASM file
        """
        self.qclass = qclass(qasmDir= "TestDir")
        self.qclass.start()
        self.qclass.run()
    

class TestBasicQint(unittest.TestCase):
    """
    Tests a qint with a standard
    qclass and tests the class methods
    """
    def setUp(self):
        qiskit.IBMQ.load_account()
        self.qclass = qclass()
        self.qclass.start()
    
    def tearDown(self):
        try:
            os.remove(self.qclass.qasmDir)
        except:
            print("Couldn't remove compiled OpenQASM at %s location" % self.qclass.qasmDir)

    def test_nothing(self):
        """
        Tests that qint works with no arguements
        """
        thisInt = qint(self.qclass)
        thisInt.measure()
        result = self.qclass.get_result()
        self.assertEqual(thisInt.extract_result(result), 0)

    def test_initial(self):
        """
        Tests that qint appropriately assigns an intial value
        """
        thisInt = qint(self.qclass, value= 9)
        thisInt.measure()
        result = self.qclass.get_result()
        self.assertEqual(thisInt.extract_result(result), 9)

    def test_small_size(self):
        """
        Tests that a small qint holds a values from 0-31
        """
        thisInt = qint(self.qclass, value= 31, small= True)
        thisInt.measure()
        result = self.qclass.get_result()
        self.assertEqual(thisInt.extract_result(result), 31)

    def test_small_overflow(self):
        self.assertRaises(OverflowError, qint(self.qclass, value= 32, small= True))

    def test_large_size(self):
        """
        Tests whether a large qint can hold extra large values
        """
        thisInt = qint(self.qclass, value= 2**31, big= True)
        thisInt.measure()
        result = self.qclass.get_result()
        self.assertEqual(thisInt.extract_result(result), 2**31)
    
    def test_overflow(self):
        """
        Tests whether a qint properly overflows
        """
        thisInt = qint(self.qclass, value= 2**14)
        self.assertEqual(len(thisInt.qubits), 32)

    def test_specify_size(self):
        """
        Tests whether custom sizes are properly alloted
        """
        thisInt = qint(self.qclass, size= 4)
        self.assertEqual(len(thisInt.qubits), 4)

    def test_rand_small(self):
        """
        Tests whether quantrand stays within a small range
        """
        iterations = 100
        for i in range(iterations):
            self.assertIn(qint.quantrand(0, 16), range(0, 16))

    def test_rand_big(self):
        """
        Tests whether quantrand stays within a large range
        """
        iterations = 100
        for i in range(iterations):
            self.assertIn(qint.quantrand(0, 1000), range(0, 1000))

    def test_rand_big_w_step(self):
        """
        Tests whether quantrand stays within a big range
        with a step
        """
        iterations = 100
        for i in range(iterations):
            self.assertIn(qint.quantrand(0, 1000, step= 10), range(0, 1000))

    def test_increment(self):
        """
        Tests whether qint increments pure values
        """
        a = qint(self.qclass, value= 68)
        a.increment()
        a.increment()
        a.measure()
        result = self.qclass.get_result()
        self.assertEqual(a.extract_result(result), 68+2)

    def test_sp_1(self):
        """
        Tests whether qint properly makes
        a qint with 1 int
        """
        s = qint.super_position([7], self.qclass)
        s.measure_sup()
        counts = self.qclass.get_counts()
        counts = s.extract_counts(counts)
        self.assertTrue(len(counts.items()) == 1 and 7 in counts.keys())

    def test_sp_2(self):
        """
        Tests whether both vals in a superposition qint
        are both measured and the probs are about equal
        """
        s = qint.super_position([7, 8], self.qclass)
        s.measure_sup()
        counts = self.qclass.get_counts()
        counts = s.extract_counts(counts)
        self.assertTrue(len(counts.items()) == 2 and 7 in counts.keys() and 8 in counts.keys())

    def test_sp_8(self):
        """
        Tests whether superposition works with 8 nums
        """
        s = qint.super_position([31, 30, 29, 28, 27, 26, 25, 24], self.qclass)
        s.measure_sup()
        counts = self.qclass.get_counts()
        counts = s.extract_counts(counts)
        self.assertTrue(len(counts.items()) == 8 and all([x in counts.keys() for x in range(24, 32)]))

    def test_increment_sup(self):
        """
        Tests whether increment works on super position
        """
        s = qint.super_position([7, 8], self.qclass)
        s.increment()
        s.measure_sup()
        counts = self.qclass.get_counts()
        counts = s.extract_counts(counts)
        self.assertTrue(len(counts.items()) == 2 and 9 in counts.keys() and 8 in counts.keys())