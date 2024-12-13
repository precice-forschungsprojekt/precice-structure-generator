import re

class XMLTag:
    def __init__(self, tag_name, attributes, text_content, children=None):
        self.tag_name = tag_name
        self.attributes = attributes
        self.text_content = text_content
        self.children = children if children is not None else []

    def __repr__(self):
        return f"XMLTag(tag_name={self.tag_name}, attributes={self.attributes}, text_content={self.text_content}, children={self.children})"

class XMLReader:
    def __init__(self, xml_string: str):
        """
        Initialize the XMLReader with an XML string
        
        Args:
            xml_string (str): Input XML string to read
        """
        self.xml_string = xml_string
        self.root = self.parse_xml()

    def parse_xml(self):
        """Parse the entire XML string and create the root XMLTag"""
        pattern = r'<(\??[\w:\-]+)([^>]*)>(.*?)</\1>|<([^/>]+)([^>]*)/?>'
        matches = re.findall(pattern, self.xml_string, re.DOTALL)
        root = None
        stack = []

        for match in matches:
            tag_name = match[0] if match[0] else match[3]
            attributes = self.parse_attributes(match[1] if match[0] else match[4])
            text_content = match[2].strip() if match[0] else ''
            new_tag = XMLTag(tag_name, attributes, text_content)

            if stack:
                parent_tag = stack[-1]
                parent_tag.children.append(new_tag)

            if match[0] or not match[2].strip():
                stack.append(new_tag)

            if not root:
                root = new_tag

            if not match[0] or match[2].strip():
                stack.pop()

        return root

    def parse_attributes(self, attr_string):
        """Parse attribute string into a dictionary"""
        attributes = {}
        pattern = r'(\w+)=["\']?([^"\']+)["\']?'
        matches = re.findall(pattern, attr_string)
        for key, value in matches:
            attributes[key] = value
        return attributes

# Example usage:
xml_string = """<?xml version="1.0" ?>
<precice-configuration>
   <log/>
   <profiling synchronize="on" mode="fundamental"/>
   <data:vector name="Calculix-SU2_CFD-Mesh-Displacement"/>
   <data:vector name="SU2_CFD-Calculix-Mesh-Force"/>
   <mesh name="SU2_CFD-Calculix-Mesh" dimensions="3">
      <user-data name="Calculix-SU2_CFD-Mesh-Displacement"/>
      <user-data name="SU2_CFD-Calculix-Mesh-Force"/>
   </mesh>
   <mesh name="Calculix-SU2_CFD-Mesh" dimensions="3">
      <user-data name="SU2_CFD-Calculix-Mesh-Force"/>
      <user-data name="Calculix-SU2_CFD-Mesh-Displacement"/>
   </mesh>
   <participant name="SU2_CFD">
      <provide-mesh name="SU2_CFD-Calculix-Mesh"/>
      <read-data name="Calculix-SU2_CFD-Mesh-Displacement" mesh_name="SU2_CFD-Calculix-Mesh"/>
      <receive-mesh name="Calculix-SU2_CFD-Mesh" from="Calculix"/>
      <write-data name="SU2_CFD-Calculix-Mesh-Force" mesh_name="SU2_CFD-Calculix-Mesh"/>
      <mapping:nearest-neighbor direction="read" from_="Calculix-SU2_CFD-Mesh" to="SU2_CFD-Calculix-Mesh" constraint="consistent"/>
      <mapping:nearest-neighbor direction="write" from="SU2_CFD-Calculix-Mesh" to="Calculix-SU2_CFD-Mesh" constraint="conservative"/>
   </participant>
   <m2n:sockets connector="Calculix" acceptor="SU2_CFD" exchange-directory="../"/>
   <participant name="Calculix">
      <provide-mesh name="Calculix-SU2_CFD-Mesh"/>
      <read-data name="SU2_CFD-Calculix-Mesh-Force" mesh_name="Calculix-SU2_CFD-Mesh"/>
      <write-data name="Calculix-SU2_CFD-Mesh-Displacement" mesh_name="Calculix-SU2_CFD-Mesh"/>
   </participant>
   <coupling-scheme:parallel-implicit>
      <participant first="SU2_CFD" second="Calculix"/>
      <max-timesteps value="20"/>
      <timestep-length value="1e-3" valid-digits="8"/>
      <max-iterations value="100"/>
      <exchange data="Calculix-SU2_CFD-Mesh-Displacement" mesh="SU2_CFD-Calculix-Mesh" from="Calculix" to="SU2_CFD"/>
      <relative-convergence-measure limit="0.0001" mesh="SU2_CFD-Calculix-Mesh" data="Calculix-SU2_CFD-Mesh-Displacement"/>
      <exchange data="SU2_CFD-Calculix-Mesh-Force" mesh="SU2_CFD-Calculix-Mesh" from="SU2_CFD" to="Calculix"/>
      <relative-convergence-measure limit="0.0001" mesh="SU2_CFD-Calculix-Mesh" data="SU2_CFD-Calculix-Mesh-Force"/>
      <post-processing:IQN-ILS>
         <filter type="QR1" limit="1e-06"/>
         <initial-relaxation value="0.1"/>
         <max-used-iterations value="50"/>
         <timesteps-reused value="8"/>
         <data name="Calculix-SU2_CFD-Mesh-Displacement" mesh="Calculix-SU2_CFD-Mesh"/>
         <data name="SU2_CFD-Calculix-Mesh-Force" mesh="SU2_CFD-Calculix-Mesh"/>
      </post-processing:IQN-ILS>
   </coupling-scheme:parallel-implicit>
</precice-configuration>"""

xml_reader = XMLReader(xml_string)
xml_tag = xml_reader.root

print(xml_tag)
