import unittest
from lxml import etree
import sys

sys.path.append('../RhapsodyParser')
from RhapsodyParser import RhapsodyFileParser

class TestSuite_RhapsodyFileParser(unittest.TestCase):
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test01_parse_rpy(self):
        test_file = "./assets/Project.rpy"
        
        root = None
        
        # run the test
        
        try:
            root = RhapsodyFileParser.parse(test_file)
        except:
            print(sys.exc_info()[0])
        
        self.failIf(root is None, 'Failed to parse file')
        
    def test02_parse_sbs(self):
        test_file = "./assets/Project_rpy/Application.sbs"
        
        root = None
        
        # run the test
        try:
            root = RhapsodyFileParser.parse(test_file)
        except:
            print(sys.exc_info()[0])
        
        self.failIf(root is None, 'Failed to parse file')
        
    def test03_parse_content(self):
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
        expected_tree = etree.ElementTree(etree.fromstring(expected_output))
        
        root = None
        
        # run the test
        try:
            root = RhapsodyFileParser.fromString(test_content)
        except:
            print(sys.exc_info()[0])
        
        # validate the output
        self.failIf(root is None, 'Failed to parse string content')
        self.elements_equal(root, expected_tree.getroot())

    def elements_equal(self, e1, e2):
        self.failIf(e1.tag != e2.tag)
        self.failIf(e1.tag != e2.tag)
        self.failIf(e1.text != e2.text)
        self.failIf(e1.tail != e2.tail)
        self.failIf(e1.attrib != e2.attrib)
        self.failIf(len(e1) != len(e2))
        all(self.elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite_RhapsodyFileParser)
    unittest.TextTestRunner(verbosity=2).run(suite)