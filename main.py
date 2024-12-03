from xml_parser import create_feature_model, load_and_parse_xml
from feature_model import print_feature_hierarchy
from xml_parser import load_and_parse_xml, parse_constraints
# from constraints import validate_constraints
# from logic_translator import translate_to_logic
# from mwp_calculator import calculate_mwp
# from visualizer import start_visualization

def main():
    # Step 1: Load and Parse the feature model from XML
    print("Loading feature model...")
    # xml_file_path = 'feature-model.xml'
    xml_file_path = 'file3_boolean_constraints.xml'
    print("Parsing the feature model...")
    xml_root, root_feature = load_and_parse_xml(xml_file_path)

    # Step 2: Parse and display cross-tree constraints
    print("\nParsing constraints...")
    constraints = parse_constraints(xml_root)
    print("Constraints:", constraints)

    # Step 3: Display the feature hierarchy
    print("\nFeature Model Hierarchy:")
    print_feature_hierarchy(root_feature)


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
    root_feature = create_feature_model(xml_file_path)

    # Display the feature model hierarchy
    print("Feature Model Hierarchy:")
    print_feature_hierarchy(root_feature)



if __name__ == "__main__":
    main()
