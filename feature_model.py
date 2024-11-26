class Feature:
    """
    Represents a feature in the feature model.
    """
    def __init__(self, name, mandatory=False, children=None):
        self.name = name
        self.mandatory = mandatory
        self.children = children or []

    def add_child(self, feature):
        """
        Adds a child feature to the current feature.
        """
        self.children.append(feature)

    def __repr__(self):
        """
        Returns a string representation of the feature.
        """
        return f"Feature(name={self.name}, mandatory={self.mandatory}, children={len(self.children)})"


# Create the feature model hierarchy
def create_feature_model():
    """
    Creates and returns the feature model hierarchy.

    Returns:
        Feature: The root feature of the feature model.
    """
    # Root feature
    application = Feature("Application", mandatory=True)

    # Catalog and its child features
    catalog = Feature("Catalog", mandatory=True)
    filtered = Feature("Filtered", mandatory=True)
    filtered.add_child(Feature("ByDiscount"))
    filtered.add_child(Feature("ByWeather"))
    filtered.add_child(Feature("ByLocation"))
    catalog.add_child(filtered)

    # Add Catalog to Application
    application.add_child(catalog)

    # Return the root feature
    return application
