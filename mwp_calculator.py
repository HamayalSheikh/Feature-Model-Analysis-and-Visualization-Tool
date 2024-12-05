from itertools import combinations

def calculate_mwp(logic_rules):
    """
    Calculates the Minimum Working Products (MWPs) based on logic rules.
    
    Args:
        logic_rules (list): A list of logic rules derived from the feature model.
        
    Returns:
        list: A list of valid MWPs, where each MWP is a set of feature names.
    """
    # Extract unique features from the logic rules
    features = extract_features_from_logic_rules(logic_rules)

    # Generate all possible feature subsets
    all_combinations = []
    for r in range(1, len(features) + 1):
        all_combinations.extend(combinations(features, r))

    # Filter valid MWPs by checking against the logic rules
    mwps = []
    for subset in all_combinations:
        if is_valid_mwp(set(subset), logic_rules):
            mwps.append(set(subset))

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
        features.update(rule.split())
    return {feature for feature in features if feature.isalnum()}  # Filter out logical operators


def is_valid_mwp(feature_set, logic_rules):
    """
    Checks if a given feature set satisfies the logic rules.
    
    Args:
        feature_set (set): A set of features representing a potential MWP.
        logic_rules (list): A list of logic rules derived from the feature model.
        
    Returns:
        bool: True if the feature set satisfies all logic rules, False otherwise.
    """
    for rule in logic_rules:
        # Replace feature names in the rule with True/False based on the feature set
        eval_rule = rule
        for feature in feature_set:
            eval_rule = eval_rule.replace(feature, "True")
        for feature in extract_features_from_logic_rules([rule]) - feature_set:
            eval_rule = eval_rule.replace(feature, "False")
        
        # Evaluate the rule
        try:
            if not eval(eval_rule):
                return False
        except Exception as e:
            print(f"Error evaluating rule '{rule}': {e}")
            return False

    return True
