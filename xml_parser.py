import xml.etree.ElementTree as ET
from feature_model import Feature

def parse_features(element, parent_path=""):
    """
    Recursively parses features from an XML element and builds the feature hierarchy.
    
    Args:
        element (ET.Element): The current XML element.
        parent_path (str): The hierarchical path to the current feature (used for uniqueness).
    
    Returns:
        Feature: A Feature instance representing the parsed element.
    """
    # feature_name = element.attrib.get("name", "Group")
    feature_name = element.attrib.get("name")
    mandatory = element.attrib.get("mandatory", "false").lower() == "true"
    group_type = element.attrib.get("group", "").lower()

    # Generate a unique path for this node
    # unique_path = f"{parent_path}/{feature_name}" if parent_path else feature_name

    # Create the current feature
    # feature = Feature(name=unique_path, mandatory=mandatory, group_type=group_type)
    feature = Feature(name=feature_name, mandatory=mandatory, group_type=group_type)



    for child in element.findall("feature"):
        child_feature = parse_features(child)
        feature.add_child(child_feature)

    for group in element.findall("group"):
        group_type = group.attrib.get("type", "").lower()
        group_feature = Feature(name=f"{feature_name}-Group-{group_type}", group_type=group_type)
        for group_child in group.findall("feature"):
            group_feature.add_child(parse_features(group_child))
        feature.add_child(group_feature)
    # # Process child features
    # for index, child in enumerate(element, start=1):
    #     if child.tag == "group":  # Handle groups explicitly
    #         group_features = []
    #         group_type = child.attrib.get("type", "and").lower()

    #         # Parse all features within this group
    #         for group_child in child.findall("feature"):
    #             group_features.append(parse_features(group_child, parent_path=feature_name))

    #         # Add the group to the feature
    #         group_feature = Feature(name=f"{feature_name}/Group ({group_type}-{index})", mandatory=False)
    #         for gf in group_features:
    #             group_feature.add_child(gf)
    #         feature.add_child(group_feature)
    #     elif child.tag == "feature":  # Standard feature processing
    #         child_feature = parse_features(child, parent_path=feature_name)
    #         feature.add_child(child_feature)

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

# def parse_constraints(root):
#     """
#     Parses cross-tree constraints from the XML.

#     Args:
#         root (ET.Element): The root XML element.

#     Returns:
#         list: A list of constraints in propositional logic format.
#     """
#     def extract_feature_name(text):
#         """
#         Extracts the feature name from a string by isolating the last significant word.

#         Args:
#             text (str): The input text containing a feature description.

#         Returns:
#             str: The cleaned feature name.
#         """
#         #  Split text into words and keep only capitalized words (assuming feature names are capitalized)
#         words = text.split()
#         feature_words = [word for word in words if word[0].isupper() and word.isalnum()]
#         return " ".join(feature_words) if feature_words else text.strip()

    
#     constraints = []

#     for constraint in root.findall(".//constraints/constraint"):
#         # Parse English constraints
#         english_statement = constraint.find("englishStatement")
#         if english_statement is not None and english_statement.text:
#             text = english_statement.text.strip()
#             print(f"Parsed statement (English): {text}")

#             # Check if the statement contains "requires" or "required"
#             if "requires" in text or "required" in text:
#                 parts = text.split("requires" if "requires" in text else "required")
#                 if len(parts) == 2:
#                     # feature_a = parts[0].strip().split()[-1]  # Extract last meaningful word
#                     # feature_b = parts[1].strip().split()[-1]  # Extract last meaningful word
#                     feature_a = extract_feature_name(parts[0].strip())
#                     feature_b = extract_feature_name(parts[1].strip())
#                     default_translation = f"{feature_a} → {feature_b}"
#                     print(f"Default translation: {default_translation}")
#                     user_input = input(f"Translate '{text}' into propositional logic (Press Enter to accept '{default_translation}', or provide your logic): ").strip()
#                     # user_input = input(f"Translate '{text}' into propositional logic (e.g., A → B): ")
#                     if not user_input:
#                         # Default translation if the user doesn't provide one
#                         constraints.append(default_translation)
#                     else:
#                         constraints.append(user_input)

#             # Handle "excludes" constraints
#             elif "excludes" in text:
#                 parts = text.split("excludes")
#                 if len(parts) == 2:
#                     # feature_a = parts[0].strip().split()[-1]  # Extract last meaningful word
#                     # feature_b = parts[1].strip().split()[-1]  # Extract last meaningful word
#                     feature_a = extract_feature_name(parts[0].strip())
#                     feature_b = extract_feature_name(parts[1].strip())
#                     default_translation = f"{feature_a} → !{feature_b}"
#                     print(f"Default translation: {default_translation}")
#                     user_input = input(f"Translate '{text}' into propositional logic (Press Enter to accept '{default_translation}', or provide your logic): ").strip()
#                     # user_input = input(f"Translate '{text}' into propositional logic (e.g., A → !B): ")
#                     if not user_input:
#                         # Default translation if the user doesn't provide one
#                         constraints.append(default_translation)
#                     else:
#                         constraints.append(user_input)

#         # Parse Boolean constraints (already in propositional logic format)
#         boolean_expression = constraint.find("booleanExpression")
#         if boolean_expression is not None and boolean_expression.text:
#             text = boolean_expression.text.strip()
#             print(f"Parsed statement (Boolean): {text}")
#             constraints.append(text)

#     return constraints


def translate_constraint_to_logic(english_statement, default_translation):
    """
    Handles user input for translating an English statement to propositional logic.

    Args:
        english_statement (str): The original English statement.
        default_translation (str): The default propositional logic translation.

    Returns:
        str: The user-provided or default propositional logic translation.
    """
    print(f"Translate '{english_statement}' into propositional logic:")
    user_input = input(f"Press Enter to accept the default '{default_translation}', or provide your own translation: ").strip()

    if not user_input:
        return default_translation  # Use the default translation if input is empty
    else:
        return user_input


def parse_constraints(root, new_constraint=None):
    """
    Parses cross-tree constraints from the XML and handles new constraints entered by the user.
    
    Args:
        root (ET.Element): The root XML element.
        new_constraint (str): Optional new constraint entered by the user.
    
    Returns:
        list: A list of constraints in propositional logic format.
    """
    def extract_feature_name(text):
        """
        Extracts the feature name from a string by isolating the last significant word.

        Args:
            text (str): The input text containing a feature description.

        Returns:
            str: The cleaned feature name.
        """
        words = text.split()
        feature_words = [word for word in words if word[0].isupper() and word.isalnum()]
        return " ".join(feature_words) if feature_words else text.strip()

    constraints = []

    # Handle a new constraint entered by the user
    if new_constraint:
        if "requires" in new_constraint or "required" in new_constraint:
            parts = new_constraint.split("requires" if "requires" in new_constraint else "required")
            if len(parts) == 2:
                feature_a = extract_feature_name(parts[0].strip())
                feature_b = extract_feature_name(parts[1].strip())
                default_translation = f"{feature_a} → {feature_b}"
                translated_logic = translate_constraint_to_logic(new_constraint, default_translation)
                constraints.append(translated_logic)

        elif "excludes" in new_constraint:
            parts = new_constraint.split("excludes")
            if len(parts) == 2:
                feature_a = extract_feature_name(parts[0].strip())
                feature_b = extract_feature_name(parts[1].strip())
                default_translation = f"{feature_a} → !{feature_b}"
                translated_logic = translate_constraint_to_logic(new_constraint, default_translation)
                constraints.append(translated_logic)
        else:
            # If the constraint is already in propositional logic
            print("Assuming the constraint is already in propositional logic.")
            constraints.append(new_constraint)

        return constraints  # Return the new constraint directly

    # Parse existing constraints from the XML
    for constraint in root.findall(".//constraints/constraint"):
        english_statement = constraint.find("englishStatement")
        if english_statement is not None and english_statement.text:
            text = english_statement.text.strip()
            print(f"Parsed statement (English): {text}")

            if "requires" in text or "required" in text:
                parts = text.split("requires" if "requires" in text else "required")
                if len(parts) == 2:
                    feature_a = extract_feature_name(parts[0].strip())
                    feature_b = extract_feature_name(parts[1].strip())
                    default_translation = f"{feature_a} → {feature_b}"
                    user_input = input(f"Use default translation '{default_translation}'? (Press Enter to accept, or provide your own logic): ").strip()
                    if not user_input:
                        constraints.append(default_translation)
                    else:
                        constraints.append(user_input)

            elif "excludes" in text:
                parts = text.split("excludes")
                if len(parts) == 2:
                    feature_a = extract_feature_name(parts[0].strip())
                    feature_b = extract_feature_name(parts[1].strip())
                    default_translation = f"{feature_a} → !{feature_b}"
                    user_input = input(f"Use default translation '{default_translation}'? (Press Enter to accept, or provide your own logic): ").strip()
                    if not user_input:
                        constraints.append(default_translation)
                    else:
                        constraints.append(user_input)

        # Parse Boolean constraints (already formatted)
        boolean_expression = constraint.find("booleanExpression")
        if boolean_expression is not None and boolean_expression.text:
            text = boolean_expression.text.strip()
            constraints.append(text)

    return constraints
