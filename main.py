from logic_translator import translate_to_logic, format_and_print_logic
from mwp_calculator import calculate_mwp, format_mwp_results
from xml_parser import load_and_parse_xml, parse_constraints
from feature_model import print_feature_hierarchy
from cross_tree_handler import handle_cross_tree_constraints
from cross_tree_handler import extract_feature_name

def main():
    print("Loading feature model...")
    xml_file_path = "feature-model.xml"
    xml_root, root_feature = load_and_parse_xml(xml_file_path)

    print("\nParsing constraints...")
    constraints = parse_constraints(xml_root)
    feature_names = extract_feature_name(root_feature)  # Extract feature names
    print("Constraints:", constraints)

    print("\nTranslating to propositional logic...")
    logic = translate_to_logic(root_feature)

    # Handle constraints separately, avoiding duplicate evaluation
    translated_constraints = handle_cross_tree_constraints(constraints, feature_names)
    logic["constraints"].extend(translated_constraints)

    print("Propositional Logic:")
    format_and_print_logic(logic)

    print("\nFeature Model Hierarchy:")
    print_feature_hierarchy(root_feature)

    print("\nCalculating Minimum Working Products...")
    mwps = calculate_mwp(logic)
    format_mwp_results(mwps)


if __name__ == "__main__":
    main()
