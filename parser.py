import xml.etree.ElementTree as etree
import re

# finds index of next quote starting at startInd or
# zero if startInd not given. Ignores escaped
# quote
def findEndQuote(content, startInd=0):
    if (startInd < 0):
        raise Exception("Invalid start index")
    
    content_length = len(content)
    offset = startInd
    
    while (offset < content_length):
        nextQuoteInd = content.find("\"", offset)
        if (0 == nextQuoteInd):
            return nextQuoteInd
        elif (-1 == nextQuoteInd):
            raise Exception("Missing end of double quote")
        elif ("\\" == content[nextQuoteInd-1]):
            # ignore escaped quotes
            offset = nextQuoteInd+1
        else:
            return nextQuoteInd

    raise Exception("Missing end of double quote")        

# find index of next semi-colon starting at startInd or
# zero if startInd not given. Ignore semi-colons
# within quote blocks    
def findLineEnd(content, startInd=0):
    if (startInd < 0):
        raise Exception("Invalid start index")

    content_length = len(content)
    offset = startInd
    
    while (offset < content_length):
        lineEnd = content.find(";", offset)
        
        if (-1 == lineEnd):
            raise Exception("Missing semi-colon line at end of content")
        
        quoteStart = content.find("\"", offset)
        if (-1 == quoteStart):
            quoteStart = content_length
            
        if (lineEnd < quoteStart):
            return lineEnd
        else:
            # ignore semi-colons in quotes
            offset = findEndQuote(content, quoteStart+1) + 1
            
    raise Exception("Missing semi-colon line at end of content")

# regex patterns for parsing rhapsody files
BLOCK_TYPE_PATTERN = re.compile(r"\s*?\{\s+?(\S+)\s*?", re.MULTILINE|re.DOTALL)
CHILD_PATTERN = re.compile(r"\s*-\s+(\S+?)\s*=\s*(\S)", re.MULTILINE|re.DOTALL)
ARRAY_PATTERN = re.compile(r"\s*-\s*size\s*=\s*(\d+?);", re.MULTILINE|re.DOTALL)

# parses string of rhapsody-style content into xml
# returns base xml node and length of content parsed
def parse(content, name):
    # find content block type
    block_type = BLOCK_TYPE_PATTERN.search(content)
    
    if block_type is None:
        raise Exception("Missing block type")

    content_length = len(content)
    offset = block_type.end()
    
    root = etree.Element(name, {'type':block_type.group(1)})
    
    # parse children within block
    while (offset < content_length):
        if content[offset] in "\r\t\n ":
            # ignore formatting whitespace characters
            offset += 1
            continue
        elif '}' == content[offset]:
            # end once terminating brace is found
            offset += 1
            break
        
        # find next child
        child_elem = CHILD_PATTERN.search(content, offset)
        if child_elem is None:
            raise Exception("Missing child element")
        
        # store the name and type of the child
        child_name = child_elem.group(1)
        child_type = child_elem.group(2)
        
        # child with sub-children
        if ('{' == child_type):
            child, num_read = parse(content[offset:], child_name)
            root.append(child)
            offset += num_read
        # child denoting array type content block
        elif ('size' == child_name):
            array_size = ARRAY_PATTERN.search(content, offset)
            if array_size is None:
                raise Exception("Failed to parse size element")
            
            # parse size of array
            size = int(array_size.group(1))
            offset = array_size.end()
            
            # do not include size element in xml
            # further children are only expected if the size is non-zero
            if (0 != size):
                array_elem = CHILD_PATTERN.search(content, offset)
                if array_elem is None:
                    raise Exception("Missing array value element")
                    
                # store name and type of array elements    
                elem_name = array_elem.group(1)
                elem_type = array_elem.group(2)
                offset = array_elem.start(2)
                
                # parse array of children with sub-children
                if ('{' == elem_type):
                    for i in range(0,size):
                        child, num_read = parse(content[offset:], elem_name)
                        root.append(child)
                        offset += num_read
                # parse array of single item children
                else:
                    for i in range(0,size):
                        child_start = offset
                        child_end = findLineEnd(content, child_start)
                        child = etree.SubElement(root, elem_name)
                        child.text = content[child_start:child_end]
                        offset = child_end + 1
        # child element
        else:
            child_end = findLineEnd(content, offset)
            child = etree.SubElement(root, child_elem.group(1))
            child.text = content[child_elem.start(2):child_end]
            offset = child_end + 1
    return root, offset

# parse rhapsody file in xml
# return base xml node    
def parseFile(filename):
    with open(filename, 'r') as f:
        content = f.read()
        if (0 == len(content)):
            raise Exception("Cannot parse empty file")
        root, num_read = parse(content, "root")
        return root
        
    return None
    
filename = "C:/Users/abc/Desktop/Trace/test1.sbs"    

import time
starttime = time.time()
root = parseFile(filename)
endtime = time.time()
elapsed = endtime - starttime
print elapsed
