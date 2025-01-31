#!/usr/bin/env python3
from lxml import etree
import itertools
import sys
import io
import shutil

def isEmptyTag(element):
    """
    Check if an XML element is empty (has no children).
    """
    return not element.getchildren()

def isComment(element):
    """
    Check if the given element is an XML comment.
    """
    return isinstance(element, etree._Comment)

def attribLength(element):
    """
    Calculate the total length of the attributes in an element.
    For each attribute, count the key, quotes, equals sign, and value.
    """
    total = 0
    for k, v in element.items():
        # Format: key="value"
        total += len(k) + 2 + len(v) + 1
    # Add spaces between attributes (if more than one attribute exists)
    total += len(element.attrib) - 1
    return total

def elementLen(element):
    """
    Estimate the length of an element's start tag (including its attributes).
    This is used to decide whether to print attributes inline or vertically.
    """
    total = 2  # For the angle brackets "<" and ">"
    total += len(element.tag)
    if element.attrib:
        total += 1 + attribLength(element)
    if isEmptyTag(element):
        total += 2  # For the space and slash in an empty tag "<tag />"
    return total

class PrettyPrinter():
    """
    Class to handle the prettification of XML content.
    This class not only provides methods for printing XML elements
    in a prettified format, but also methods to parse and reformat
    an XML file directly.
    """
    def __init__(self, stream=sys.stdout, indent='  ', maxwidth=100, maxgrouplevel=1):
        self.stream = stream      # Output stream (can be a file, StringIO, etc.)
        self.indent = indent      # String used for indentation
        self.maxwidth = maxwidth  # Maximum width for a single line
        self.maxgrouplevel = maxgrouplevel  # Maximum depth to group elements on one line

    def print(self, text=''):
        """
        Write text to the output stream followed by a newline.
        """
        self.stream.write(text + '\n')

    def fmtAttrH(self, element):
        """
        Format element attributes for inline (horizontal) display.
        """
        return " ".join(['{}="{}"'.format(k, v) for k, v in element.items()])

    def fmtAttrV(self, element, level):
        """
        Format element attributes for vertical display, with indentation.
        """
        prefix = self.indent * (level + 1)
        return "\n".join(['{}{}="{}"'.format(prefix, k, v) for k, v in element.items()])

    def printXMLDeclaration(self, root):
        """
        Print the XML declaration at the beginning of the file.
        """
        self.print('<?xml version="{}" encoding="{}" ?>'.format(
            root.docinfo.xml_version, root.docinfo.encoding))

    def printRoot(self, root):
        """
        Print the entire XML document starting from the root element.
        """
        self.printXMLDeclaration(root)
        self.printElement(root.getroot(), level=0)

    def printTagStart(self, element, level):
        """
        Print the start tag of an element.
        If the element has attributes, decide whether to print them inline or vertically.
        """
        assert isinstance(element, etree._Element)
        if element.attrib:
            # If the estimated length is within maxwidth, print inline.
            if elementLen(element) + len(self.indent) * level <= self.maxwidth:
                self.print("{}<{} {}>".format(self.indent * level, element.tag, self.fmtAttrH(element)))
            else:
                # Otherwise, print the tag name on one line and attributes on subsequent lines.
                self.print("{}<{}".format(self.indent * level, element.tag))
                self.print("{}>".format(self.fmtAttrV(element, level)))
        else:
            self.print("{}<{}>".format(self.indent * level, element.tag))

    def printTagEnd(self, element, level):
        """
        Print the end tag of an element.
        """
        assert isinstance(element, etree._Element)
        self.print("{}</{}>".format(self.indent * level, element.tag))

    def printTagEmpty(self, element, level):
        """
        Print an empty element (no children) with a self-closing tag.
        """
        assert isinstance(element, etree._Element)
        if element.attrib:
            if elementLen(element) + len(self.indent) * level <= self.maxwidth:
                self.print("{}<{} {} />".format(self.indent * level, element.tag, self.fmtAttrH(element)))
            else:
                self.print("{}<{}".format(self.indent * level, element.tag))
                self.print("{} />".format(self.fmtAttrV(element, level)))
        else:
            self.print("{}<{} />".format(self.indent * level, element.tag))

    def printComment(self, element, level):
        """
        Print an XML comment.
        """
        assert isinstance(element, etree._Comment)
        self.print(self.indent * level + str(element))

    def printElement(self, element, level):
        """
        Recursively print an XML element and its children in prettified format.
        """
        # If the element is a comment, print it and return.
        if isinstance(element, etree._Comment):
            self.printComment(element, level=level)
            return

        if isEmptyTag(element):
            self.printTagEmpty(element, level=level)
        else:
            self.printTagStart(element, level=level)
            self.printChildren(element, level=level + 1)
            self.printTagEnd(element, level=level)

    def printChildren(self, element, level):
        """
        Print all child elements, grouping them if applicable.
        """
        if level > self.maxgrouplevel:
            for child in element.getchildren():
                self.printElement(child, level=level)
            return

        groups1 = itertools.groupby(element.getchildren(), lambda e: str(e.tag).split(':')[0])
        groups = []
        for _, group in groups1:
            group = list(group)
            if isEmptyTag(group[0]):
                groups.append(group)
            else:
                groups += [[e] for e in group]

        last = len(groups)
        for i, group in enumerate(groups, start=1):
            for child in group:
                self.printElement(child, level=level)
            # Add an extra newline between groups (except after comments or the last group)
            if not (isComment(group[0]) or (i == last)):
                self.print()

    @staticmethod
    def parse_xml(content):
        """
        Parse XML content into an lxml ElementTree, with recovery and whitespace cleanup.
        
        Parameters:
          content (bytes): The XML content in bytes.
        
        Returns:
          An lxml ElementTree object.
        """
        parser = etree.XMLParser(recover=True, remove_comments=False, remove_blank_text=True)
        return etree.fromstring(content, parser).getroottree()

    def prettify_file(self, file_path):
        """
        Prettify the XML file at the given path and overwrite the file with the prettified content.

        Parameters:
          file_path (str): Path to the XML file.
        
        Returns:
          bool: True if the file was processed (even if no changes were made), False if an error occurred.
        """
        try:
            # Open and read the file as bytes.
            with open(file_path, 'rb') as xml_file:
                content = xml_file.read()
        except Exception as e:
            print(f"Unable to open file: \"{file_path}\"")
            print(e)
            return False

        try:
            # Parse the XML content using the static method.
            xml_tree = PrettyPrinter.parse_xml(content)
        except Exception as e:
            print(f"Error occurred while parsing file: \"{file_path}\"")
            print(e)
            return False

        # Create an in-memory text stream to hold the prettified XML.
        buffer = io.StringIO()
        # Use a temporary PrettyPrinter instance with the buffer as output.
        temp_printer = PrettyPrinter(stream=buffer, indent=self.indent,
                                     maxwidth=self.maxwidth, maxgrouplevel=self.maxgrouplevel)
        temp_printer.printRoot(xml_tree)

        # Get the prettified content from the buffer.
        new_content = buffer.getvalue()
        # Compare with the original content (decoded from bytes).
        if new_content != content.decode("utf-8"):
            try:
                # Overwrite the original file with the prettified content.
                with open(file_path, "w") as xml_file:
                    buffer.seek(0)
                    shutil.copyfileobj(buffer, xml_file)
            except Exception as e:
                print(f"Failed to write prettified content to file: \"{file_path}\"")
                print(e)
                return False
        else:
            print(f"No changes required for file: \"{file_path}\"")
        return True
