# from itertools import combinations

# def calculate_mwp(logic, mandatory_features):
#     """
#     Calculate the Minimum Working Products (MWPs) from the propositional logic.

#     Args:
#         logic (dict): The propositional logic representing feature relationships and constraints.
#         mandatory_features (set): A set of mandatory features to include in every MWP.

#     Returns:
#         list: A list of MWPs, where each MWP is a set of feature names.
#     """
#     # Extract all possible features from the logic rules
#     all_features = extract_features_from_logic_rules(logic)
    
#     # Generate all valid combinations of features that include mandatory features
#     valid_combinations = []
    
#     # Create all combinations of optional features (we will combine them with mandatory features)
#     optional_features = all_features - mandatory_features
    
#     # Generate all possible subsets of the optional features
#     all_combinations = [set(combo) for r in range(0, len(optional_features) + 1) for combo in combinations(optional_features, r)]
    
#     for combo in all_combinations:
#         # Include mandatory features in each combination
#         feature_set = mandatory_features.union(combo)
        
#         print("Logic dictionary:")
#         print(logic)

#         # Check if this feature set is valid by evaluating all constraints
#         if is_valid_mwp(feature_set, logic["constraints"]):
#             valid_combinations.append(feature_set)

#     return valid_combinations


# def extract_features_from_logic_rules(logic):
#     """
#     Extract all features from the propositional logic rules.

#     Args:
#         logic (dict): The propositional logic containing feature relationships.

#     Returns:
#         set: A set of all feature names.
#     """
#     features = set()
    
#     # Extract feature names from all logic rules (root, mandatory, children, xor, or, and constraints)
#     for rule in logic["root"] + logic["mandatory"] + logic["children_to_parent"] + logic["xor"] + logic["or"] + logic["constraints"]:
#         features.update(rule.replace("(", "").replace(")", "").split())
    
#     return {f for f in features if f.isalnum()}


# def is_valid_mwp(feature_set, constraints):
#     """
#     Check if a given feature set satisfies all constraints.

#     Args:
#         feature_set (set): A set of features to validate.
#         constraints (list): A list of constraints in propositional logic format.

#     Returns:
#         bool: True if the feature set satisfies all constraints, False otherwise.
#     """
#     for constraint in constraints:
#         # Replace feature names with True or False based on whether they are in the feature set
#         eval_rule = constraint
        
#         # Substitute feature names in the rule with True or False
#         for feature in feature_set:
#             eval_rule = eval_rule.replace(feature, "True")
#         for feature in extract_features_from_logic_rules([constraint]) - feature_set:
#             eval_rule = eval_rule.replace(feature, "False")
        
#         try:
#             # Evaluate the constraint expression
#             if not eval(eval_rule):
#                 return False
#         except Exception as e:
#             print(f"Error evaluating rule '{constraint}': {e}")
#             return False
    
#     return True

from itertools import combinations

def calculate_mwp(logic_rules, mandatory_features):
    """
    Calculates the Minimum Working Products (MWPs) based on logic rules.
    
    Args:
        logic_rules (list): A list of logic rules derived from the feature model.
        mandatory_features (set): A set of mandatory features.
        
    Returns:
        list: A list of valid MWPs, where each MWP is a set of feature names.
    """
    # Extract unique features from the logic rules
    features = extract_features_from_logic_rules(logic_rules)

    # Generate all possible feature subsets, ensuring that mandatory features are always included
    all_combinations = []
    for r in range(len(mandatory_features), len(features) + 1):  # Start from mandatory size
        all_combinations.extend(combinations(features, r))

    # Add mandatory features to all combinations
    all_combinations = [set(comb).union(mandatory_features) for comb in all_combinations]

    # Filter valid MWPs by checking against the logic rules
    mwps = []
    for subset in all_combinations:
        if is_valid_mwp(subset, logic_rules, mandatory_features):
            mwps.append(subset)

    return mwps


def extract_features_from_logic_rules(logic_rules):
    """
    Extracts unique feature names from the logic rules.
    
    Args:
        logic_rules (list): A list of logic rules derived from the feature model.
        
    Returns:
        set: A set of unique feature names.
    """
    features = set()
    for rule in logic_rules:
        features.update(rule.split())  # Split by space to extract features
    return {feature for feature in features if feature.isalnum()}  # Filter out logical operators


def is_valid_mwp(feature_set, logic_rules, mandatory_features):
    """
    Checks if a given feature set satisfies the logic rules.
    
    Args:
        feature_set (set): A set of features representing a potential MWP.
        logic_rules (list): A list of logic rules derived from the feature model.
        
    Returns:
        bool: True if the feature set satisfies all logic rules, False otherwise.
    """
    # Ensure that all mandatory features are included in the feature set
    if not mandatory_features.issubset(feature_set):
        return False
    
    # Check each logic rule against the feature set
    for rule in logic_rules:
        eval_rule = rule
        # Replace feature names with True/False based on the feature set
        for feature in feature_set:
            eval_rule = eval_rule.replace(feature, "True")
        for feature in extract_features_from_logic_rules([rule]) - feature_set:
            eval_rule = eval_rule.replace(feature, "False")
        
         # Replace logical operators with Python equivalents
        eval_rule = eval_rule.replace("->", "<=").replace("|", " or ").replace("&", " and ")

        # Evaluate the rule
        try:
            if not eval(eval_rule):
                return False
        except Exception as e:
            print(f"Error evaluating rule '{rule}': {e}")
            return False

    return True
