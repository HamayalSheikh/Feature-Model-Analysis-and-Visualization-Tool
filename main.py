from xml_parser import load_and_parse_xml
from feature_model import create_feature_model
# from constraints import validate_constraints
# from logic_translator import translate_to_logic
# from mwp_calculator import calculate_mwp
# from visualizer import start_visualization

def main():
    # Step 1: Parse and Validate XML
    print("Parsing the feature model...")
    xml_file_path = 'feature-model.xml'
    load_and_parse_xml(xml_file_path)

    # # Step 2: Translate to Propositional Logic
    # logic = translate_to_logic(xml_data)
    
    # # Step 3: Calculate Minimum Working Product
    # mwp = calculate_mwp(logic)
    
    # # Step 4: Start Visualization
    # start_visualization(xml_data, mwp)

    """
    Main function to initialize and display the feature model hierarchy.
    """
    # Create the feature model
    root_feature = create_feature_model()

    # Display the feature model hierarchy
    print("Feature Model Hierarchy:")
    print_feature_hierarchy(root_feature)

def print_feature_hierarchy(feature, depth=0):
    """
    Prints the feature hierarchy in a readable format.

    Args:
        feature (Feature): The current feature.
        depth (int): The level of indentation for child features.
    """
    indent = "  " * depth
    print(f"{indent}- {feature.name} (Mandatory: {feature.mandatory})")
    for child in feature.children:
        print_feature_hierarchy(child, depth + 1)


if __name__ == "__main__":
    main()
