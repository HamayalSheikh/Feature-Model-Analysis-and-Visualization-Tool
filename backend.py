from flask import Flask, jsonify, request
from flask_cors import CORS
from xml.etree.ElementTree import ParseError
from xml_parser import load_and_parse_xml, parse_constraints

app = Flask(__name__)
CORS(app)

@app.route('/parse-xml', methods=['POST'])
def parse_xml():
    try:
        # Get the XML data from the request
        xml_data = request.json.get("xml")
        temp_file = "feature_model_temp.xml"

        # Write XML to a temporary file for parsing
        with open(temp_file, "w") as file:
            file.write(xml_data)

        # Parse the XML and constraints
        root, root_feature = load_and_parse_xml(temp_file)
        constraints = parse_constraints(root)

        def feature_to_dict(feature):
            """
            Convert the Feature object to a dictionary for serialization.
            """
            return {
                "label": feature.name,
                "value": feature.name,
                "groupType": feature.group_type,
                "mandatory": feature.mandatory,
                "children": [feature_to_dict(child) for child in feature.children]
            }

        # Convert the root feature to a dictionary
        feature_model = feature_to_dict(root_feature)

        return jsonify({
            "treeData": feature_model,
            "constraints": constraints
        })

    except ParseError as e:
        return jsonify({"error": "Invalid XML file", "details": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
