import os
import re
import time

from lxml import etree

class RhapsodyProjectParser:
    """RhapsodyProjectParser
    Utility class for translating rhapsody style project into a dictionary of xml files.
    """
    __slots__ = ['_project']

    def __init__(self, file=None):
        """ Constructor """
        
        self._project = None
        if file:
            self.parse(file)
            
    def parse(self, file, parseDependencies=True):
        """ Translates a rhapsody style project into a dictionary of xml trees per project file"""
        
        if not isinstance(file, str):
            raise ValueError('Expected filename of type string')
            
        basepath, filename = os.path.split(file)
        basename, ext = os.path.splitext(filename)
        basepath = os.path.join(basepath, basename + '_rpy')
                
        if ext.lower() != ".rpy":
            raise ValueError('Invalid project file (Expected rpy type file):\n\t%s' % (file))
        elif True != os.path.isdir(basepath):
            raise ValueError('Missing project directory:\n\t%s' % (basepath))
    
        self._project = {}
        root = RhapsodyFileParser.parseFile(file)
        self._project[file] = root
        
        if parseDependencies:
            self._parseDependencies(root, basepath)
            
        return self._project
    
    def _parseDependencies(self, node, basepath):
        """ Searches for any files linked to by the given xml tree and adds any found to the dictionary"""
        
        # find linked subsystem files
        for filenameNode in node.xpath("//*[@type='ISubsystem']/fileName"):
            if (2 >= len(filenameNode.text)):
                continue
                
            filename = os.path.join(basepath, filenameNode.text[1:-1] + ".sbs")
            
            if (True != os.path.isfile(filename)):
                continue
            elif filename not in self._project:
                link_path,_ = os.path.split(filename)
                linked_node = RhapsodyFileParser.parseFile(filename)
                self._project[filename] = linked_node
                self._parseDependencies(linked_node, link_path)
        
        # find linked class files
        for filenameNode in node.xpath("//*[@type='IClass']/fileName"):
            if (2 >= len(filenameNode.text)):
                continue
                
            filename = os.path.join(basepath, filenameNode.text[1:-1] + ".cls")

            if (True != os.path.isfile(filename)):
                continue
            elif filename not in self._project:
                link_path,_ = os.path.split(filename)
                linked_node = RhapsodyFileParser.parseFile(filename)
                self._project[filename] = linked_node
                self._parseDependencies(linked_node, link_path)
         
        # find linked component files
        for filenameNode in node.xpath("//*[@type='IComponent']/fileName"):
            if (2 >= len(filenameNode.text)):
                continue
                
            filename = os.path.join(basepath, filenameNode.text[1:-1] + ".cmp")

            if (True != os.path.isfile(filename)):
                continue
            elif filename not in self._project:
                link_path,_ = os.path.split(filename)
                linked_node = RhapsodyFileParser.parseFile(filename)
                self._project[filename] = linked_node
                self._parseDependencies(linked_node, link_path)

class RhapsodyFileParser:
    """RhapsodyFileParser
    Utility class for translating rhapsody style files into xml.
    """
    FILE_INFO_RE = re.compile(r'\s*(\S+)\s+version\s+([0-9.]+)\s+(\S+)\s+(\S+)\s+', re.MULTILINE|re.DOTALL) #<archive> version <rhapsody version> <project type> <project id>
    BLOCK_START_RE = re.compile(r'\s*\{\s*(\S+)\s+', re.MULTILINE|re.DOTALL) #{ <block type>
    BLOCK_END_RE = re.compile(r'\s*\}\s*', re.MULTILINE|re.DOTALL)
    CHILD_RE = re.compile(r'\s*-\s+(\S+)\s+=\s*', re.MULTILINE|re.DOTALL) # - <name> =
    SIZE_RE = re.compile(r'\s*(\d+)\s*;\s', re.MULTILINE|re.DOTALL)
    VALUE_RE = re.compile(r'\s*-\s+value\s+=\s*', re.MULTILINE|re.DOTALL)
    CHILD_QUOTE_RE = re.compile(r'\s*(\"(?<!\\)\")\s*;', re.MULTILINE|re.DOTALL)
    CHILD_VALUE_RE = re.compile(r'(?=[^"]*"[^"]*(?:"[^"]*"[^"]*)*$);', re.MULTILINE|re.DOTALL) #re.compile(r'\s*(.*?);\s*', re.MULTILINE|re.DOTALL)
    
    @staticmethod
    def parse(source):
        """ Translate rhapsody file into xml. Takes in file descriptor or a string in rhapsody style formatting"""
        
        content = None
        if isinstance(source, file):
            content = source.read()
        elif isinstance(content, str):
            content = source
        else:
            raise ValueError('Invalid source (Expected file object or filename)')
        
        content = ''.join(c for c in content if RhapsodyFileParser._valid_xml_char_ordinal(c))
        contentLength = len(content)
        
        match = RhapsodyFileParser.FILE_INFO_RE.match(content)
        if match is None:
            raise ValueError('Expected file information at line %d' % (RhapsodyFileParser._getLineNum(content, 0)))
        
        root = etree.Element('root')
        root.set('rhapsody_type', match.group(1))
        root.set('rhapsody_version', match.group(2))
        root.set('rhapsody_lang', match.group(3))
        root.set('id', match.group(4))
        contentOffset = match.end()
        
        root, _ = RhapsodyFileParser._parseBlock(root, content, contentLength, contentOffset)

        return root
    
    @staticmethod
    def toString(root):
        file_type = root.get('rhapsody_type', '')
        rhapsody_version = root.get('rhapsody_version', '')
        file_lang = root.get('rhapsody_lang', '')
        file_id = root.get('id', '')
        
        content = '%s version %s %s %s\n' % (file_type, rhapsody_version, file_lang, file_id)
        content += RhapsodyFileParser._toChildString(root, 0)
        content += '\n'
        
        return content
    
    @staticmethod
    def getGuidDict(root):
        guid_dict = {}
        
        # find all model elements with a GUID
        for node in root.xpath("//_id/.."):
            # ignore dependencies
            if ('_dependsOn' != node.tag): 
                id_node = node.find('_id')
                if id_node is not None:
                    guid_dict[id_node.text] = node

        return guid_dict
    
    @staticmethod
    def _toChildString(node, level):
        content = ''
    
        if (0 == len(node)):
            content += node.text + ';'
        else:
            content += '{ %s \n' % (node.get('type', ''))
            
            isValueNode = False
            
            for child in node:
                if (True == isValueNode):
                    if (0 == len(child)):
                        RhapsodyFileParser._toChildString(child, level + 1)
                    else:
                        content += '\n' + '\t'*(level + 1)
                        content += RhapsodyFileParser._toChildString(child, level + 1)
                elif ('size' == child.tag):
                    content += '\t'*(level + 1) + '- size = %s;\n' % (child.text)
                    if (0 != int(child.text)):
                        content += '\t'*(level + 1) + '- value = '
                        isValueNode = True
                elif ('elementList' == child.tag):
                    content += '\t'*(level + 1) + '- elementList = %d;\n' % (len(child))
                    for granChild in child:
                        content += '\t'*(level + 1)
                        content += RhapsodyFileParser._toChildString(granChild, (level + 1))
                        content += '\n'
                    content += '\t'*(level + 1) + '\n'
                else:
                    content += '\t'*(level + 1) + '- %s = ' % (child.tag)
                    content += RhapsodyFileParser._toChildString(child, level + 1)
                    content += '\n'

            if (True == isValueNode):
                content += '\n'
                    
            content += '\t'*level + '}'
            
        return content
    
    @staticmethod
    def _parseBlock(node, content, contentLength, contentOffset):
        match = RhapsodyFileParser.BLOCK_START_RE.match(content, contentOffset)
        if match is None:
            raise ValueError("Invalid block at line %d" % (RhapsodyFileParser._getLineNum(content, contentOffset)))
        
        node.set('type', match.group(1))
        contentOffset = match.end()
        
        while (True):
            match = RhapsodyFileParser.BLOCK_END_RE.match(content, contentOffset)
            if match:
                contentOffset = match.end()
                break
            else:
                match = RhapsodyFileParser.CHILD_RE.match(content, contentOffset)
                if match:
                    contentOffset = match.end()
                    if ('size' == match.group(1)):
                        match = RhapsodyFileParser.SIZE_RE.match(content, contentOffset)
                        if match is None:
                            raise ValueError('Invalid size attribute at line %d' % (RhapsodyFileParser._getLineNum(content, contentOffset)))
                        count = int(match.group(1))
                        contentOffset = match.end()
                        
                        child = etree.SubElement(node, 'size')
                        child.text = match.group(1)
                        
                        if (0 != count):
                            match = RhapsodyFileParser.VALUE_RE.match(content, contentOffset)
                            if match is None:
                                raise ValueError('Invalid value attribute at line %d' % (RhapsodyFileParser._getLineNum(content, contentOffset)))
                            contentOffset = match.end()
                            
                            for _ in range(0, count):
                                child = etree.SubElement(node, 'value')
                                child, contentOffset = RhapsodyFileParser._parseChildContent(child, content, contentLength, contentOffset)
                                
                    elif ('elementList' == match.group(1)):
                        elemListNode = etree.SubElement(node, 'elementList')
                        match = RhapsodyFileParser.SIZE_RE.match(content, contentOffset)
                        if match is None:
                            raise ValueError('Invalid elementList attribute at line %d' % (RhapsodyFileParser._getLineNum(content, contentOffset)))
                        count = int(match.group(1))
                        contentOffset = match.end()
                        
                        if (0 < count):
                            for _ in range(0, count):
                                child = etree.SubElement(elemListNode, 'element')
                                child, contentOffset = RhapsodyFileParser._parseChildContent(child, content, contentLength, contentOffset)
                                
                    else:
                        child = etree.SubElement(node, match.group(1))
                        child, contentOffset = RhapsodyFileParser._parseChildContent(child, content, contentLength, contentOffset)
                else:
                    raise ValueError('Expected } at line %d' % (RhapsodyFileParser._getLineNum(content, contentOffset)))
        
        return node, contentOffset
    
    @staticmethod
    def _parseChildContent(node, content, contentLength, contentOffset):
        match = RhapsodyFileParser.BLOCK_START_RE.match(content, contentOffset)
        if match:
            node, contentOffset = RhapsodyFileParser._parseBlock(node, content, contentLength, contentOffset)
        else:
            contentStart = contentOffset
            contentOffset = RhapsodyFileParser._findLineEnd(content, contentLength, contentOffset)
            node.text = content[contentStart:contentOffset-1]
        return node, contentOffset
    
    @staticmethod
    def _findLineEnd(content, contentLength, contentOffset):
        isInQuote = False
        
        endStartInd = content.find(';', contentOffset)
        if -1 == endStartInd:
            raise ValueError('Missing ; at line %d' % (RhapsodyFileParser._getLineNum(content, contentOffset)))
        
        quoteStartInd = content.find('"', contentOffset)
        if -1 == quoteStartInd:
            quoteStartInd = contentLength
        
        while (True):
            if (endStartInd < quoteStartInd):
                contentOffset = endStartInd + 1
                if ~isInQuote:
                    break
                else:
                    endStartInd = content.find(';', contentOffset)
                    if -1 == endStartInd:
                        raise ValueError('Missing ; at line %d' % (RhapsodyFileParser._getLineNum(content, contentOffset)))
            else:
                contentOffset = quoteStartInd + 1
                isInQuote = ~isInQuote;
                quoteStartInd = content.find('"', contentOffset)
                if (-1 == quoteStartInd):
                    quoteStartInd = contentLength
        
        return contentOffset
        
    @staticmethod
    def _getLineNum(content, contentOffset):
        return content.count('\n', 0, contentOffset);

    @staticmethod
    def _valid_xml_char_ordinal(c):
        codepoint = ord(c)
        # conditions ordered by presumed frequency
        return (
            0x20 <= codepoint <= 0xD7FF or
            codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or
            0x10000 <= codepoint <= 0x10FFFF
            )
    
    @staticmethod
    def get_modified_time(date_time=time.localtime()):
        return '%d.%d%d::%d.%d.%d' % (date_time.tm_mon, \
                                      date_time.tm_mday, \
                                      date_time.tm_year, \
                                      date_time.tm_hour, \
                                      date_time.tm_min, \
                                      date_time.tm_sec)
    
    @staticmethod
    def add_requirement_dependency(node, guid, req_guid, req_name, req_subsystem):
        dependencies = node.find('Dependencies')
        if dependencies is None:
            dependencies = etree.SubElement(node, 'Dependencies')
            dependencies.set('type', 'IRPYContainer')
        
        size = dependencies.find('size')
        if size is None:
            size = etree.SubElement(dependencies, 'size')
            size.text = '0'
        
        dependencyExists = False
        for value in dependencies.findall('value'):
            value_guid = value.find('_id')
            if value_guid is not None:
                if (guid == value_guid.text):
                    dependencyExists = True
                    break
        
        if not dependencyExists:
            # increment size
            size.text = str(int(size.text) + 1)
            # add new value node
            value = etree.SubElement(dependencies, 'value')
            value.set('type', 'IDependency')
            
            etree.SubElement(value, '_id').text = guid
            etree.SubElement(value, '_myState').text = '2048'
            etree.SubElement(value, '_name').text = req_name
            etree.SubElement(value, '_modifiedTimeWeak').text = RhapsodyFileParser.get_modified_time()
            dependsOn = etree.SubElement(value, '_dependsOn')
            dependsOn.set('type', 'INObjectHandle')
            etree.SubElement(dependsOn, '_m2Class').text = '"IRequirement"'
            etree.SubElement(dependsOn, '_filename').text = '""'
            etree.SubElement(dependsOn, '_subsystem').text = req_subsystem
            etree.SubElement(dependsOn, '_class').text = '""'
            etree.SubElement(dependsOn, '_name').text = req_name
            etree.SubElement(dependsOn, '_id').text = req_guid
