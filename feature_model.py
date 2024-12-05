class Feature:
    """
    Represents a feature in the feature model.
    """
    def __init__(self, name, mandatory=False, children=None, group_type=None):
        self.name = name
        self.mandatory = mandatory
        self.group_type = group_type
        self.children = children or []

    def add_child(self, feature):
        self.children.append(feature)

    def __repr__(self):
        return f"Feature(name={self.name}, mandatory={self.mandatory}, children={len(self.children)})"


def print_feature_hierarchy(feature, depth=0):
    indent = "  " * depth
    print(f"{indent}- {feature.name} (Mandatory: {feature.mandatory}, Group Type: {feature.group_type})")
    for child in feature.children:
        print_feature_hierarchy(child, depth + 1)
