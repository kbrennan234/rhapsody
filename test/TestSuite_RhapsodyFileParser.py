import sys
sys.path.append('../..')

import unittest
from rhapsody.RhapsodyParser import RhapsodyFileParser
from lxml import etree

class TestSuite_RhapsodyFileParser(unittest.TestCase):
    
    def setUp(self):
        self._parser = RhapsodyFileParser()
        
    def tearDown(self):
        self._parser = None
    
    def test_parse_rpy(self):
        test_file = "./assets/Project.rpy"
        
        root = None
        
        # run the test
        try:
            root = self._parser.parseFile(test_file)
        except: 
            pass
        
        self.failIf(root is None, 'Failed to parse file')
        
    def test_parse_sbs(self):
        test_file = "./assets/Project_rpy/Application.sbs"
        
        root = None
        
        # run the test
        try:
            root = self._parser.parseFile(test_file)
        except:
            pass
        
        self.failIf(root is None, 'Failed to parse file')
        
    def test_parse_content(self):
        test_content = """I-Logix-RPY-Archive version 8.5.2 C++ 1159120
{ IProject 
	- _id = GUID 4cd0f270-57c7-4035-9363-a8b2b765b5da;
	- _Name = "Browser;";
	- _myState = 8192;
	- _UserColors = { IRPYRawContainer 
		- size = 16;
		- value = 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 16777215; 
	}
	- _properties = { IPropertyContainer 
		- Subjects = { IRPYRawContainer 
			- size = 2;
			- value = 
			{ IPropertySubject 
				- elementList = 2;
				{ CGIClass 
					- _id = GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8;
					- m_name = { CGIText 
						- m_str = "TopLevel";
						- m_style = "Arial" 10 0 0 0 1 ;
					}
				}
				{ CGIClass 
					- _id = GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8;
					- m_name = { CGIText 
						- m_str = "TopLevel";
						- m_style = "Arial" 10 0 0 0 1 ;
					}
				}
			}
			{ IPropertySubject 
				- elementList = 2;
				{ CGIClass 
					- _id = GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8;
					- m_name = { CGIText 
						- m_str = "TopLevel";
						- m_style = "Arial" 10 0 0 0 1 ;
					}
				}
				{ CGIClass 
					- _id = GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8;
					- m_name = { CGIText 
						- m_str = "TopLevel";
						- m_style = "Arial" 10 0 0 0 1 ;
					}
				}
			}
		}
	}
}"""

        expected_output = """<root rhapsody_type="I-Logix-RPY-Archive" rhapsody_version="8.5.2" rhapsody_lang="C++" id="1159120" type="IProject"><_id>GUID 4cd0f270-57c7-4035-9363-a8b2b765b5da</_id><_Name>"Browser;"</_Name><_myState>8192</_myState><_UserColors type="IRPYRawContainer"><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value><value>16777215</value></_UserColors><_properties type="IPropertyContainer"><Subjects type="IRPYRawContainer"><value type="IPropertySubject"><elements><element type="CGIClass"><_id>GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8</_id><m_name type="CGIText"><m_str>"TopLevel"</m_str><m_style>"Arial" 10 0 0 0 1</m_style></m_name></element><element type="CGIClass"><_id>GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8</_id><m_name type="CGIText"><m_str>"TopLevel"</m_str><m_style>"Arial" 10 0 0 0 1</m_style></m_name></element></elements></value><value type="IPropertySubject"><elements><element type="CGIClass"><_id>GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8</_id><m_name type="CGIText"><m_str>"TopLevel"</m_str><m_style>"Arial" 10 0 0 0 1</m_style></m_name></element><element type="CGIClass"><_id>GUID fa98390c-c6b2-4f55-9fd9-38386fb630d8</_id><m_name type="CGIText"><m_str>"TopLevel"</m_str><m_style>"Arial" 10 0 0 0 1</m_style></m_name></element></elements></value></Subjects></_properties></root>"""

        root = None

        # run the test
        try:
            root = self._parser.parse(test_content)
        except:
            pass
        
        self.failIf(root is None, 'Failed to parse string content')
        
        # validate the output
        test_output = etree.tostring(root)
        self.assertEqual(test_output, expected_output, 'Test output does not match expected output')

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite_RhapsodyFileParser)
    unittest.TextTestRunner(verbosity=2).run(suite)