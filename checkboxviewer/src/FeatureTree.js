import React, { useState, useEffect, useCallback } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheckSquare, faSquare, faFolder, faFolderOpen, faChevronDown, faChevronRight } from "@fortawesome/free-solid-svg-icons";

const FeatureTree = () => {
    const [checked, setChecked] = useState([]);
    const [expanded, setExpanded] = useState([]);
    const [treeData, setTreeData] = useState([]);
    const [constraints, setConstraints] = useState([]);

    const xmlData = "feature_model.xml"
    // Format tree data from backend response
    const formatTreeData = useCallback((features) => {
        // Deep clone to avoid mutation issues
        const processNode = (node) => {
            let type = ""

            //check the name, if it has '(xor' then it is a xor group, if it has '(or' then it is an or group
            if (node.label.includes("(xor")) {
                type = "xor"

            } else if (node.label.includes("(or")) {
                type = "or"
            }

            const formattedNode = {
                label: node.label,
                value: node.value,
                mandatory: node.mandatory || false,
                groupType: type || null
            };


            // Process children recursively
            if (node.children && node.children.length > 0) {
                formattedNode.children = node.children.map(processNode);
            }

            return formattedNode;
        };

        return features.map(processNode);
    }, []);

    // Fetch data from backend
    useEffect(() => {
        if (!xmlData) return;

        fetch("http://127.0.0.1:5000/parse-xml", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ xml: xmlData }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Error fetching XML data: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Received data:", data);

                // Ensure treeData exists and is valid
                if (!data.treeData || typeof data.treeData !== "object" || !data.treeData.children) {
                    console.error("Invalid or missing 'treeData' in response:", data);
                    setTreeData([]);
                    return;
                }

                // Set tree data
                setTreeData([data.treeData]); // Wrap treeData in an array for root processing

                // Format constraints
                const formattedConstraints = Array.isArray(data.constraints)
                    ? data.constraints
                    : [];
                setConstraints(formattedConstraints);
            })
            .catch((error) => console.error("Error fetching XML data:", error));
    }, [xmlData]);


    // Check if a node can be selected based on constraints
    const canSelectNode = (value, currentChecked) => {
        // Check XOR group constraints
        const findNodeByValue = (nodes, targetValue) => {
            for (const node of nodes) {
                if (node.value === targetValue) return node;
                if (node.children) {
                    const found = findNodeByValue(node.children, targetValue);
                    if (found) return found;
                }
            }
            return null;
        };

        const targetNode = findNodeByValue(treeData, value);

        // Check XOR group constraint
        if (targetNode && targetNode.parent && targetNode.parent.groupType === 'xor') {
            const xorSiblings = targetNode.parent.children;
            const alreadySelectedSibling = xorSiblings.find(
                sibling => currentChecked.includes(sibling.value)
            );
            return !alreadySelectedSibling;
        }

        return true;
    };

    const handleCheck = (value, isChecked) => {
        let updatedChecked = [...checked];

        const updateNodeSelection = (node, isSelecting) => {
            // Handle mandatory node deselection
            if (!isSelecting && node.mandatory) {
                updatedChecked = []; // Deselect root node and all nodes
                return;
            }

            // Add or remove the node
            if (isSelecting) {
                if (!updatedChecked.includes(node.value)) {
                    updatedChecked.push(node.value);
                }
            } else {
                updatedChecked = updatedChecked.filter((v) => v !== node.value);
            }

            // Handle XOR constraint
            if (isSelecting && node.parent?.groupType === "xor") {
                node.parent.children.forEach((sibling) => {
                    if (sibling.value !== node.value) {
                        updatedChecked = updatedChecked.filter((v) => v !== sibling.value);
                    }
                });
            }

            // Recursively update children
            if (node.children) {
                node.children.forEach((child) => updateNodeSelection(child, isSelecting));
            }

            // If deselecting, check if parent needs to be deselected
            if (!isSelecting) {
                const parent = findParentFeature(node.value, treeData[0]);
                if (parent) {
                    const allChildrenDeselected = parent.children.every(
                        (child) => !updatedChecked.includes(child.value)
                    );
                    if (allChildrenDeselected) {
                        updatedChecked = updatedChecked.filter((v) => v !== parent.value);
                    }
                }
            }

            // If selecting, ensure mandatory parents are selected
            if (isSelecting) {
                let currentParent = findParentFeature(node.value, treeData[0]);
                while (currentParent) {
                    if (currentParent.mandatory && !updatedChecked.includes(currentParent.value)) {
                        updatedChecked.push(currentParent.value);
                    }
                    currentParent = findParentFeature(currentParent.value, treeData[0]);
                }
            }
        };

        // Handle root deselection
        if (value === treeData[0]?.value && !isChecked) {
            updatedChecked = []; // Clear all selections
        } else {
            const targetNode = findFeatureByValue(value, treeData[0]);
            if (targetNode) {
                updateNodeSelection(targetNode, isChecked);
            }
        }

        // Ensure uniqueness
        setChecked([...new Set(updatedChecked)]);
    };



    // Existing helper functions
    const findFeatureByValue = (value, node) => {
        if (node.value === value) return node;
        for (const child of node.children || []) {
            const found = findFeatureByValue(value, child);
            if (found) return found;
        }
        return null;
    };

    const findParentFeature = (value, node) => {
        if (node.children) {
            for (const child of node.children) {
                if (child.value === value) return node;
                const parent = findParentFeature(value, child);
                if (parent) return parent;
            }
        }
        return null;
    };

    // Expand/collapse functionality
    const handleExpand = (value) => {
        setExpanded(prev =>
            prev.includes(value)
                ? prev.filter(v => v !== value)
                : [...prev, value]
        );
    };

    // Render icon functions
    const renderFolderIcon = (mandatory) => {
        return mandatory
            ? <FontAwesomeIcon icon={faFolderOpen} style={{ color: "red" }} />
            : <FontAwesomeIcon icon={faFolder} />;
    };

    const renderExpandCollapseIcon = (value, node) => {
        // Only render expand/collapse icon if node has children
        if (!node.children || node.children.length === 0) return null;

        return expanded.includes(value)
            ? <FontAwesomeIcon icon={faChevronDown} />
            : <FontAwesomeIcon icon={faChevronRight} />;
    };

    const renderIcon = (value) => {
        return checked.includes(value)
            ? <FontAwesomeIcon icon={faCheckSquare} />
            : <FontAwesomeIcon icon={faSquare} />;
    };

    // Render tree nodes
    const renderNode = (node) => {
        return (
            <div key={node.value}>
                <div style={{ display: "flex", alignItems: "center", margin: "5px 0" }}>
                    {/* Folder Expand Icon */}
                    {node.children && node.children.length > 0 && (
                        <div
                            onClick={() => handleExpand(node.value)}
                            style={{ cursor: "pointer", marginRight: "5px" }}
                        >
                            {renderExpandCollapseIcon(node.value, node)}
                        </div>
                    )}

                    {/* Checkbox and Folder Icon */}
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            cursor: "pointer"
                        }}
                        onClick={() => handleCheck(node.value, !checked.includes(node.value))}
                    >
                        <div style={{ marginRight: "10px" }}>
                            {renderIcon(node.value)}
                        </div>
                        <div>{renderFolderIcon(node.mandatory)}</div>
                        <div style={{
                            marginLeft: "10px",
                            fontWeight: node.mandatory ? "bold" : "normal"
                        }}>
                            {node.label}
                        </div>
                    </div>
                </div>

                {/* Render Child Nodes */}
                {node.children && node.children.length > 0 && expanded.includes(node.value) && (
                    <div style={{ paddingLeft: "20px" }}>
                        {node.children.map((child) => renderNode(child))}
                    </div>
                )}
            </div>
        );
    };

    // Render nothing if no tree data
    if (treeData.length === 0) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Feature Model</h1>
            {treeData.map((rootNode) => renderNode(rootNode))}
        </div>
    );
};

export default FeatureTree;