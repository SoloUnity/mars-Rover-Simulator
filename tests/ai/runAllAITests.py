# Author: Gordon Ng
import unittest
import sys

from tests.ai.heuristicsTests import heuristicsTests
from tests.ai.bfsTests import BFSAlgorithmTests
from tests.ai.aStarTests import TestAStarAlgorithm

"""
To run (from project root): python3 -m tests.ai.runAllAITests
"""

def runAllTests():
    testSuite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # testSuite.addTest(loader.loadTestsFromTestCase(heuristicsTests))
    # testSuite.addTest(loader.loadTestsFromTestCase(BFSAlgorithmTests))
    testSuite.addTest(loader.loadTestsFromTestCase(TestAStarAlgorithm))
    # testSuite.addTest(loader.loadTestsFromTestCase(DFSAlgorithmTests))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(testSuite)
    
    print("Summary")
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    print("Running all tests...\n")
    runAllTests()