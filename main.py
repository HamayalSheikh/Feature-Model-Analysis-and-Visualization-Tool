from logic_translator import format_and_print_logic, translate_to_logic
from mwp_calculator import calculate_mwp
from xml_parser import create_feature_model, load_and_parse_xml
from feature_model import print_feature_hierarchy
from xml_parser import load_and_parse_xml, parse_constraints
import os

def get_mandatory_features(root_feature):
    """
    Recursively gets all mandatory features from the feature model.

    Args:
        root_feature (Feature): The root feature of the feature model.

    Returns:
        set: A set of mandatory feature names.
    """
    mandatory_features = set()

    def recurse_features(feature):
        if feature.mandatory:
            mandatory_features.add(feature.name)
        
        # Recurse into children
        for child in feature.children:
            recurse_features(child)
    
    recurse_features(root_feature)
    return mandatory_features

def main():
 # Step 1: Load and Parse the feature model from XML
    print("Feature Model Analysis Tool")
    print("----------------------------")
    
    while True:
        # Prompt the user for an XML file path
        xml_file_path = input("Enter the path to the XML file (or 'exit' to quit): ").strip()
        if xml_file_path.lower() == 'exit':
            print("Exiting the program.")
            return
        
        # Check if the file exists
        if not os.path.isfile(xml_file_path):
            print(f"Error: File '{xml_file_path}' does not exist. Please try again.")
            continue
        
        # Try to load the file
        try:
            print("\nLoading feature model...")
            xml_root, root_feature = load_and_parse_xml(xml_file_path)
            break
        except Exception as e:
            print(f"Error loading XML file: {e}. Please check the file and try again.")
    

    # # Step 1: Load and Parse the feature model from XML
    # print("Loading feature model...")
    # xml_file_path = 'feature-model.xml'
    # # xml_file_path = 'featuremodel-1-wo-const.xml'
    # print("Parsing the feature model...")
    # xml_root, root_feature = load_and_parse_xml(xml_file_path)

    # # Step 2: Parse and display cross-tree constraints
    print("\nParsing constraints...")
    constraints = parse_constraints(xml_root)
    print("Constraints:", constraints)

# Step 2: Ask if the user wants to add new constraints
    new_constraints = []
    while True:
        add_new = input("Do you want to add a new constraint? (yes/no): ").strip().lower()
        if add_new == "no":
            break
        elif add_new == "yes":
            new_constraint = input("Enter the new constraint (English or propositional logic): ").strip()
            translated_constraint = parse_constraints(xml_root, new_constraint=new_constraint)
            new_constraints.extend(translated_constraint)

    # Step 3: Parse existing constraints from XML
    existing_constraints = parse_constraints(xml_root)
    
    # Combine constraints
    all_constraints = existing_constraints + new_constraints

    print("\nAll Constraints (in propositional logic):", all_constraints)
    
    # Step 4: Translate feature model into propositional logic
    logic = translate_to_logic(root_feature)
    if all_constraints:
        print("\nAdding constraints to propositional logic...")
        logic["constraints"].extend(all_constraints)


    # Step 3: Translate feature model into propositional logic
    print("\nTranslating to propositional logic...")
    logic = translate_to_logic(root_feature)

    print("Propositional Logic:")
    # Check if constraints are properly formatted before adding them
    if constraints:
        print("Adding constraints to logic...")
        logic["constraints"].extend(constraints)
    # # Add constraints to logic
    # logic["constraints"].extend(constraints)
    format_and_print_logic(logic)
    # for formula in logic:
    # print(logic)
    
      # Step 4: Get mandatory features
    mandatory_features = get_mandatory_features(root_feature)
    print("Mandatory Features:", mandatory_features)

     # Step 5: Calculate Minimum Working Product
    print("\nCalculating Minimum Working Products (MWPs)...")
    
    mwps = calculate_mwp(logic, mandatory_features)

    # Step 6: Display the MWP results
    format_mwp_results(mwps,  logic["root"] )

    # Step 8: Display MWPs
    # print("\nMinimum Working Products (MWPs):")
    # for mwp in mwps:
    #     print(mwp)
    
    # Create the feature model
    root_feature = create_feature_model(xml_file_path)

    # Display the feature model hierarchy
    print("Feature Model Hierarchy:")
    print_feature_hierarchy(root_feature)

def format_mwp_results(mwps, root):

    unique_mwps = []
    for mwp in mwps:
        if mwp not in unique_mwps:
            unique_mwps.append(mwp)

    print("\nCalculated Minimum Working Products (MWPs):")
    # for idx, mwp in enumerate(mwps, start=1):
    #     print(f"MWP {idx}: {', '.join(sorted(mwp))}")
        # print(f"MWP {idx}: {sorted(mwp)}")
    count=0
    # get the first word in the first mwp in mwps
    # rootValue = list(sorted(mwps[0]))[0]

    for index, mwp in enumerate(unique_mwps, start=int(len(unique_mwps)*.8)):
    # for index, mwp in enumerate(unique_mwps, start=1):
        # if mwp contains the root, print it
        if root[0] in mwp:
            print(f"MWP {count+1}: {', '.join(sorted(mwp))}")
            # print(f"MWP {index}: {', '.join(sorted(mwp))}")
            count+=1
        if count == 15:
            break


if __name__ == "__main__":
    main()
