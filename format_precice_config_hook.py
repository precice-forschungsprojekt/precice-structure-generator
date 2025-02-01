#! /usr/bin/env python3

from lxml import etree
import itertools
import argparse
import sys
import io
import shutil


def isEmptyTag(element):
    return not element.getchildren()


def isComment(element):
    return isinstance(element, etree._Comment)


def attribLength(element):
    total = 0
    for k, v in element.items():
        # KEY="VALUE"
        total += len(k) + 2 + len(v) + 1
    # spaces in between
    total += len(element.attrib) - 1
    return total


def elementLen(element):
    total = 2  # Open close
    total += len(element.tag)
    if element.attrib:
        total += 1 + attribLength(element)
    if isEmptyTag(element):
        total += 2  # space and slash
    return total


class PrettyPrinter():
    def __init__(self,
                 stream=sys.stdout,
                 indent='  ',
                 maxwidth=100,
                 maxgrouplevel=1):
        self.stream = stream
        self.indent = indent
        self.maxwidth = maxwidth
        self.maxgrouplevel = maxgrouplevel

    def print(self, text=''):
        self.stream.write(text + '\n')

    def fmtAttrH(self, element):
        return " ".join(['{}="{}"'.format(k, v) for k, v in element.items()])

    def fmtAttrV(self, element, level):
        prefix = self.indent * (level + 1)
        return "\n".join(
            ['{}{}="{}"'.format(prefix, k, v) for k, v in element.items()])

    def printXMLDeclaration(self, root):
        self.print('<?xml version="{}" encoding="{}" ?>'.format(
            root.docinfo.xml_version, root.docinfo.encoding))

    def printRoot(self, root):
        self.printXMLDeclaration(root)
        self.printElement(root.getroot(), level=0)

    def printTagStart(self, element, level):
        assert (isinstance(element, etree._Element))
        if element.attrib:
            if elementLen(element) + len(self.indent) * level <= self.maxwidth:
                self.print("{}<{} {}>".format(self.indent * level, element.tag,
                                              self.fmtAttrH(element)))
            else:
                self.print("{}<{}".format(self.indent * level, element.tag))
                self.print("{}>".format(self.fmtAttrV(element, level)))
        else:
            self.print("{}<{}>".format(self.indent * level, element.tag))

    def printTagEnd(self, element, level):
        assert (isinstance(element, etree._Element))
        self.print("{}</{}>".format(self.indent * level, element.tag))

    def printTagEmpty(self, element, level):
        assert (isinstance(element, etree._Element))
        if element.attrib:
            if elementLen(element) + len(self.indent) * level <= self.maxwidth:
                self.print("{}<{} {} />".format(self.indent * level,
                                                element.tag,
                                                self.fmtAttrH(element)))
            else:
                self.print("{}<{}".format(self.indent * level, element.tag))
                self.print("{} />".format(self.fmtAttrV(element, level)))
        else:
            self.print("{}<{} />".format(self.indent * level, element.tag))

    def printComment(self, element, level):
        assert (isinstance(element, etree._Comment))
        self.print(self.indent * level + str(element))

    def printElement(self, element, level):
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
        if level > self.maxgrouplevel:
            for child in element.getchildren():
                self.printElement(child, level=level)
            return

        # Custom sorting for top-level elements
        def custom_sort_key(elem):
            tag = str(elem.tag)
            # Predefined order for top-level elements with prefix matching
            order = {
                'data:': 1,  # Matches data:vector, data:scalar, etc.
                'mesh': 2,
                'participant': 3,
                'm2n:': 4,
                'coupling-scheme:': 5
            }
            # Find the first matching key
            for prefix, rank in order.items():
                if tag.startswith(prefix):
                    return rank
            return 6  # Unknown elements appear last

        # Sort children based on the predefined order
        sorted_children = sorted(element.getchildren(), key=custom_sort_key)

        last = len(sorted_children)
        for i, group in enumerate(sorted_children, start=1):
            # Special handling for participants to reorder child elements
            if 'participant' in str(group.tag):
                # Define order for participant child elements with more generalized matching
                participant_order = {
                    'provide-mesh': 1,
                    'receive-mesh': 2,
                    'write-data': 3,
                    'read-data': 4,
                    'mapping:': 5  # Matches mapping:nearest-neighbor, mapping:rbf, etc.
                }
                
                # Sort participant's children based on the defined order
                sorted_participant_children = sorted(
                    group.getchildren(), 
                    key=lambda child: next(
                        (rank for prefix, rank in participant_order.items() 
                         if str(child.tag).startswith(prefix)), 
                        6  # Unknown elements appear last
                    )
                )
                
                # Print participant with reordered children
                self.printTagStart(group, level=level)
                for child in sorted_participant_children:
                    self.printElement(child, level=level + 1)
                    # Add a newline after read/write mesh elements
                    if str(child.tag) in ['write-mesh', 'read-mesh']:
                        self.print()
                self.printTagEnd(group, level=level)
                self.print()
            
            # Special handling for coupling-scheme to pair relative-convergence-measure and exchange
            elif 'coupling-scheme' in str(group.tag):
                # Sort children of coupling-scheme
                sorted_scheme_children = sorted(
                    group.getchildren(),
                    key=lambda child: 0 if str(child.tag) == 'relative-convergence-measure' else 
                                      1 if str(child.tag) == 'exchange' else 2
                )
                
                # Print coupling-scheme with reordered children
                self.printTagStart(group, level=level)
                for child in sorted_scheme_children:
                    self.printElement(child, level=level + 1)
                self.printTagEnd(group, level=level)
                self.print()
            
            # Default handling for other elements
            else:
                self.printElement(group, level=level)
                self.print()
            
            # Add a newline between groups, except for the last group or comments
            if not (isComment(group) or (i == last)):
                self.print()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'files',
        nargs='+',
        type=str,
        help="The XML configuration files."
    )
    return parser.parse_args()


def parseXML(content):
    p = etree.XMLParser(recover=True,
                        remove_comments=False,
                        remove_blank_text=True)
    return etree.fromstring(content, p).getroottree()


def example():
    return parseXML(open('./BB-sockets-explicit-twoway.xml', 'r').read())


def main():
    args = parse_args()

    modified = False
    failed = False
    for filename in args.files:
        content = None
        try:
            with open(filename, 'rb') as xml_file:
                content = xml_file.read()
        except Exception as e:
            print(f"Unable to open file: \"{filename}\"")
            print(e)
            failed = True
            continue

        xml = None
        try:
            xml = parseXML(content)
        except Exception as e:
            print(f"Error occured while parsing file: \"{filename}\"")
            print(e)
            failed = True
            continue

        buffer = io.StringIO()
        printer = PrettyPrinter(stream=buffer)
        printer.printRoot(xml)

        if buffer.getvalue() != content.decode("utf-8"):
            print(f"Reformatting file: \"{filename}\"")
            modified = True
            with open(filename, "w") as xml_file:
                buffer.seek(0)
                shutil.copyfileobj(buffer, xml_file)

    if failed: return 1

    if modified: return 2

    return 0

if __name__ == '__main__':
    sys.exit(main())