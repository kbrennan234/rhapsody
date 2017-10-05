import sys
sys.path.append('../..')

import unittest
from rhapsody.RhapsodyParser import RhapsodyProjectParser

class TestSuite_RhapsodyProjectParser(unittest.TestCase):
    
    def setUp(self):
        self._parser = RhapsodyProjectParser()
        
    def tearDown(self):
        self._parser = None
        
    def test_parse_rpy(self):
        test_file = "./assets/Project.rpy"
        
        # run the test
        root = self._parser.parse(test_file)
    
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite_RhapsodyProjectParser)
    unittest.TextTestRunner(verbosity=2).run(suite)