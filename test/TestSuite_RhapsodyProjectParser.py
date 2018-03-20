import unittest
import sys

sys.path.append('../RhapsodyParser')
from RhapsodyParser import RhapsodyProjectParser

class TestSuite_RhapsodyProjectParser(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test01_parse_rpy(self):
        test_file = "./assets/Project.rpy"
        
        root = None
        
        root = RhapsodyProjectParser.parse(test_file)
            
        
        # run the test
        try:
            pass
        except:
            print(sys.exc_info()[0])
        
        self.failIf(root is None, 'failed to parse Rhapsody project file')
        
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite_RhapsodyProjectParser)
    unittest.TextTestRunner(verbosity=2).run(suite)