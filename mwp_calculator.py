from itertools import combinations

def calculate_mwp(logic):
    all_rules = (
        logic["root"]
        + logic["mandatory"]
        + logic["children_to_parent"]
        + logic["xor"]
        + logic["or"]
        + logic["constraints"]
    )
    features = extract_features_from_logic_rules(all_rules)
    all_combinations = [set(combo) for r in range(1, len(features) + 1) for combo in combinations(features, r)]

    mwps = []
    for subset in all_combinations:
        if is_valid_mwp(subset, all_rules):
            mwps.append(subset)

    return mwps


def extract_features_from_logic_rules(logic_rules):
    features = set()
    for rule in logic_rules:
        features.update(rule.replace("(", "").replace(")", "").split())
    return {f for f in features if f.isalnum()}


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
        eval_rule = rule.replace("->", "or not")  # translate implication

        # Ensure proper replacement for feature names in logic (handling hyphens in feature names)
        eval_rule = eval_rule.replace("-", "_")

        # Replace feature names in the rule with True/False based on the feature set
        try:
            for feature in feature_set:
                eval_rule = eval_rule.replace(feature, "True")
            for feature in extract_features_from_logic_rules([rule]) - feature_set:
                eval_rule = eval_rule.replace(feature, "False")

            # Evaluate the rule
            if not eval(eval_rule):
                return False
        except Exception as e:
            print(f"Error evaluating rule '{rule}': {e}")
            return False

    return True




def format_mwp_results(mwps):
    print("\nCalculated Minimum Working Products (MWPs):")
    for idx, mwp in enumerate(mwps, start=1):
        print(f"MWP {idx}: {sorted(mwp)}")
