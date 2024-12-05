import xml.etree.ElementTree as ET
from feature_model import Feature

def parse_features(element, parent_mandatory=False):
    """
    Recursively parses features from an XML element and builds the feature hierarchy.

    Args:
        element (ET.Element): The current XML element.
        parent_mandatory (bool): The mandatory status of the parent feature.

    Returns:
        Feature: A Feature instance representing the parsed element.
    """
    feature_name = element.attrib.get("name")
    mandatory = element.attrib.get("mandatory", "false").lower() == "true"
    
    # For root feature, it is mandatory by default, unless specified otherwise
    if parent_mandatory or feature_name == "Application":  # Set root feature as mandatory
        mandatory = True

    group_type = element.attrib.get("group", "").lower()

    feature = Feature(name=feature_name, mandatory=mandatory, group_type=group_type)

    # Parse child features
    for child in element.findall('feature'):
        child_feature = parse_features(child, parent_mandatory=mandatory)
        feature.add_child(child_feature)

    return feature

# Create the feature model hierarchy
def create_feature_model(file_path):
    """
    Dynamically creates and returns the feature model hierarchy from an XML file.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        Feature: The root feature of the feature model.
    """
    # Load the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Parse the root feature using the imported parse_features function
    return parse_features(root)


def load_and_parse_xml(file_path):
    """
    Loads the XML file and builds the feature model hierarchy.

    Args:
        file_path (str): Path to the XML file.

    Returns:
        Feature: The root feature of the feature model.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Skip the <featureModel> element and process its first child (<feature>)
    feature_element = root.find('feature')
    if feature_element is None:
        raise ValueError("No root feature found in the XML file.")
    
    #  Build the feature model
    # root_feature = parse_features_with_relationships(root)
    root_feature = parse_features_with_relationships(feature_element)

    return root, root_feature

def parse_features_with_relationships(element):
    """
    Parses features and handles relationships like XOR and OR groups.

    Args:
        element (ET.Element): The current XML element.

    Returns:
        Feature: The root feature with relationships applied.
    """
    feature = parse_features(element)

    # Handle group types (XOR, OR)
    group_type = element.attrib.get("group", "").lower()
    if group_type == "xor":
        # Only one child can be selected
        feature.group_type = "XOR"
    elif group_type == "or":
        # One or more children can be selected
        feature.group_type = "OR"
    else:
        feature.group_type = "None"  # Default to "None" if no group specified

    return feature

def parse_constraints(root):
    """
    Parses cross-tree constraints from the XML.

    Args:
        root (ET.Element): The root XML element.

    Returns:
        list: A list of constraints in tuple format (e.g., ("A", "B", "requires")).
    """
    constraints = []

    for constraint in root.findall(".//constraints/constraint"):
        # Parse English constraints
        english_statement = constraint.find("englishStatement")
        if english_statement is not None and english_statement.text:
            # text = english_statement.text.lower().strip()
            text = english_statement.text.strip()
            print("Parsed statement (English):", text)

            # Handle "requires" or "required" cases
            if "requires" in text or "required" in text:
                parts = text.split("requires" if "requires" in text else "required")
                if len(parts) == 2:
                    print("Parts after split:", parts)
                    constraints.append(f"{parts[0].strip()} -> {parts[1].strip()}")
                    # constraints.append((parts[0].strip(), parts[1].strip(), "requires"))
            elif "excludes" in text:
                parts = text.split("excludes")
                print("Parts after split (excludes):", parts)
                constraints.append(f"{parts[0].strip()} -> !{parts[1].strip()}")
                # constraints.append((parts[0].strip(), parts[1].strip(), "excludes"))

        # Parse Boolean constraints
        boolean_expression = constraint.find("booleanExpression")
        if boolean_expression is not None and boolean_expression.text:
            text = boolean_expression.text.strip()
            print("Parsed statement (Boolean):", text)
            constraints.append(text)
            # constraints.append((text, None, "boolean"))

    return constraints

