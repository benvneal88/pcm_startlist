import xml.etree.ElementTree as ET

def create_start_list_xml(start_list_data, race_name, race_year):
    """
    Generates an XML representation of the start list data.

    Parameters:
    - start_list_data: List of dictionaries containing cyclist and team information.
    - race_name: Name of the race.
    - race_year: Year of the race.

    Returns:
    - XML string of the start list.
    """
    root = ET.Element("start_list")
    root.set("race_name", race_name)
    root.set("race_year", str(race_year))

    for entry in start_list_data:
        cyclist_element = ET.SubElement(root, "cyclist")
        cyclist_element.set("name", entry["name"])
        cyclist_element.set("team", entry["team"])
        cyclist_element.set("number", str(entry["number"]))

    return ET.tostring(root, encoding='unicode')

def save_xml_to_file(xml_string, file_path):
    """
    Saves the XML string to a file.

    Parameters:
    - xml_string: The XML string to save.
    - file_path: The path where the XML file will be saved.
    """
    with open(file_path, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_string)