import sys
sys.path.append('../../RhapsodyParser')

import unittest
from rhapsody.RhapsodyParser import RhapsodyProjectParser

class TestSuite_RhapsodyProjectParser(unittest.TestCase):
    
    def setUp(self):
        self._parser = RhapsodyProjectParser()
        
    def tearDown(self):
        self._parser = None
        
    def test_parse_rpy(self):
        test_file = "./assets/Project.rpy"
        
        root = None
        
        # run the test
        try:
            root = self._parser.parse(test_file)
        except:
            pass
        
        self.failIf(root is None, 'failed to parse Rhapsody project file')
        
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite_RhapsodyProjectParser)
    unittest.TextTestRunner(verbosity=2).run(suite)