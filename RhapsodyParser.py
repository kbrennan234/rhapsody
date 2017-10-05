import os
import re
from lxml import etree
import six

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
        root = RhapsodyFileParser().parseFile(file)
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
                linked_node = RhapsodyFileParser().parseFile(filename)
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
                linked_node = RhapsodyFileParser().parseFile(filename)
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
                linked_node = RhapsodyFileParser().parseFile(filename)
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
    
    __slots__ = ['_content', '_contentOffset', '_contentLength']
    
    def __init__(self, file=None):
        """ Constructor """
        
        self._content = ""
        self._contentOffset = 0
            
    def parseFile(self, source):
        """ Translate rhapsody file into xml. Takes in either a file object or filename. """
        
        if isinstance(source, str):
            if not os.path.isfile(source):
                raise ValueError('Invalid filename (Path does not exist or not a file):\n\t%s' % (source))
            
            with open(source, 'r') as f:
                root = self.parse(f.read())
        elif isinstance(source, file):
            root = self.parse(f.read())
        else:
            raise ValueError('Invalid source (Expected file object or filename)')
            
        return root
            
    def parse(self, content):
        """ Translate rhapsody file into xml. Takes in a string in rhapsody style formatting"""
        
        if not isinstance(content, str):
            raise ValueError('Invalid source (Expected string)')
    
        self._content = content
        self._content = ''.join(c for c in self._content if self._valid_xml_char_ordinal(c))
        self._contentOffset = 0
        self._contentLength = len(self._content)
        
        match = self.FILE_INFO_RE.match(self._content)
        if match is None:
            raise ValueError('Expected file information at line %d' % (self._getLineNum()))
        
        root = etree.Element('root')
        root.set('rhapsody_type', match.group(1))
        root.set('rhapsody_version', match.group(2))
        root.set('rhapsody_lang', match.group(3))
        root.set('id', match.group(4))
        self._contentOffset = match.end()
        
        root = self._parseBlock(root)

        return root
        
    def _parseBlock(self, node):
        match = self.BLOCK_START_RE.match(self._content, self._contentOffset)
        if match is None:
            raise ValueError("Invalid block at line %d" % (self._getLineNum()))
        
        node.set('type', match.group(1))
        self._contentOffset = match.end()
        
        while (True):
            match =  self.BLOCK_END_RE.match(self._content, self._contentOffset)
            if match:
                self._contentOffset = match.end()
                break
            else:
                match =  self.CHILD_RE.match(self._content, self._contentOffset)
                if match:
                    self._contentOffset = match.end()
                    if 'size' == match.group(1):
                        match =  self.SIZE_RE.match(self._content, self._contentOffset)
                        if match is None:
                            raise ValueError('Invalid size attribute at line %d' % (self._getLineNum()))
                        count = int(match.group(1))
                        self._contentOffset = match.end()
                        
                        if 0 != count:
                            match =  self.VALUE_RE.match(self._content, self._contentOffset)
                            if match is None:
                                raise ValueError('Invalid value attribute at line %d' % (self._getLineNum()))
                            self._contentOffset = match.end()
                            
                            for i in xrange(0, count):
                                child = etree.SubElement(node, 'value')
                                child = self._parseChildContent(child)
                                
                    elif 'elementList' == match.group(1):
                        elemListNode = etree.SubElement(node, 'elements')
                        match = self.SIZE_RE.match(self._content, self._contentOffset)
                        if match is None:
                            raise ValueError('Invalid elementList attribute at line %d' % (self._getLineNum()))
                        count = int(match.group(1))
                        self._contentOffset = match.end()
                        if 0 < count:
                            for i in xrange(0, count):
                                child = etree.SubElement(elemListNode, 'element')
                                child = self._parseChildContent(child)
                                
                    else:
                        child = etree.SubElement(node, match.group(1))
                        child = self._parseChildContent(child)
                else:
                    raise ValueError('Expected } at line %d' % (self._getLineNum()))
        
        return node
    
    def _parseChildContent(self, node):
        match =  self.BLOCK_START_RE.match(self._content, self._contentOffset)
        if match:
            node = self._parseBlock(node)
        else:
            contentStart = self._contentOffset
            self._findLineEnd()
            node.text = self._content[contentStart:self._contentOffset-1].strip()
        return node
    
    def _findLineEnd(self):
        isInQuote = False
        
        endStartInd = self._content.find(';', self._contentOffset)
        if -1 == endStartInd:
            raise ValueError('Missing ; at line %d' % (self._getLineNum()))
        
        quoteStartInd = self._content.find('"', self._contentOffset)
        if -1 == quoteStartInd:
            quoteStartInd = self._contentLength
        
        while (1):
            if (endStartInd < quoteStartInd):
                self._contentOffset = endStartInd + 1
                if ~isInQuote:
                    break
                else:
                    endStartInd = self._content.find(';', self._contentOffset)
                    if -1 == endStartInd:
                        raise ValueError('Missing ; at line %d' % (self._getLineNum()))
            else:
                self._contentOffset = quoteStartInd + 1
                isInQuote = ~isInQuote;
                quoteStartInd = self._content.find('"', self._contentOffset)
                if -1 == quoteStartInd:
                    quoteStartInd = self._contentLength
    
    def _getLineNum(self):
        return self._content.count('\n', 0, self._contentOffset);

    def _valid_xml_char_ordinal(self, c):
        codepoint = ord(c)
        # conditions ordered by presumed frequency
        return (
            0x20 <= codepoint <= 0xD7FF or
            codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or
            0x10000 <= codepoint <= 0x10FFFF
            )
