import xml.etree.ElementTree as ET

# Parse features
def parse_features(element, parent=None):
    feature_name = element.attrib.get("name")
    print(f"Feature: {feature_name}, Parent: {parent}")
    for child in element.findall('feature'):
        parse_features(child, feature_name)


def load_and_parse_xml(file_path):
    """
    Loads the XML file and starts parsing features from the root.

    Args:
        file_path (str): Path to the XML file.
    """
    # Load the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Start parsing from the root
    parse_features(root)