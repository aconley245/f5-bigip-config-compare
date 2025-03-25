import os
import re
import sys
import tarfile
import datetime
from collections import defaultdict


def unpack_archive(file_path, extract_to):
    """
    Unpack a UCS or QKView file into a specified directory.

    Args:
        file_path (str): Path to the UCS or QKView file.
        extract_to (str): Path to the directory where the files should be extracted.

    Returns:
        str: Path to the extracted configuration file (`bigip.conf` or similar), or None.
    """
    if not tarfile.is_tarfile(file_path):
        sys.exit(f"Error: {file_path} is not a valid UCS or QKView file.")

    try:
        with tarfile.open(file_path, "r") as tar:
            print(f"Unpacking {file_path} to {extract_to}...")
            tar.extractall(path=extract_to)
    except Exception as e:
        sys.exit(f"Error extracting archive {file_path}: {e}")

    # Search for `bigip.conf` or other relevant files in the extracted contents
    conf_path = None
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file == "bigip.conf":
                conf_path = os.path.join(root, file)
                break
        if conf_path:
            break

    if not conf_path:
        sys.exit(f"Error: No 'bigip.conf' file found in the archive {file_path}.")

    print(f"Found configuration file: {conf_path}")
    return conf_path


def parse_bigip_conf(file_path):
    """
    Parse the bigip.conf file to extract virtual servers and their configurations.
    """
    try:
        with open(file_path, "r") as f:
            data = f.read()
    except FileNotFoundError:
        sys.exit(f"Error: File {file_path} not found.")

    virtual_servers = defaultdict(dict)
    vs_pattern = re.compile(r"ltm virtual (\S+) {([^}]+)}", re.DOTALL)
    attribute_pattern = re.compile(r"(\S+) (.+)")

    # Extract virtual server blocks
    for match in vs_pattern.finditer(data):
        vs_name = match.group(1)
        attributes_block = match.group(2)

        attributes = {}
        for attr_match in attribute_pattern.finditer(attributes_block):
            key, value = attr_match.groups()
            attributes[key.strip()] = value.strip()

        virtual_servers[vs_name] = attributes

    return virtual_servers


def compare_virtual_servers(vs1, vs2):
    """
    Compare the virtual server configurations between two dictionaries.
    """
    discrepancies = []

    all_vs_names = set(vs1.keys()).union(set(vs2.keys()))
    for vs_name in all_vs_names:
        if vs_name not in vs1:
            discrepancies.append(f"Virtual server '{vs_name}' is missing in the first configuration.\n")
        elif vs_name not in vs2:
            discrepancies.append(f"Virtual server '{vs_name}' is missing in the second configuration.\n")
        else:
            # Compare attributes for the same virtual server
            attributes_1 = vs1[vs_name]
            attributes_2 = vs2[vs_name]

            all_attributes = set(attributes_1.keys()).union(set(attributes_2.keys()))
            for attr in all_attributes:
                if attr not in attributes_1:
                    discrepancies.append(f"Attribute '{attr}' in virtual server '{vs_name}' is missing in the first configuration.\n")
                elif attr not in attributes_2:
                    discrepancies.append(f"Attribute '{attr}' in virtual server '{vs_name}' is missing in the second configuration.\n")
                elif attributes_1[attr] != attributes_2[attr]:
                    discrepancies.append(
                        f"Attribute '{attr}' in virtual server '{vs_name}' differs: "
                        f"'{attributes_1[attr]}' vs '{attributes_2[attr]}'.\n"
                    )

    return discrepancies


def main(file1, file2):
    """
    Main function to compare two configuration files or UCS/QKView archives.
    """
    # Create temporary directories for extraction
    temp_dir1 = "./temp_extract_1"
    temp_dir2 = "./temp_extract_2"
    os.makedirs(temp_dir1, exist_ok=True)
    os.makedirs(temp_dir2, exist_ok=True)

    # Unpack archives and locate the `bigip.conf` files
    conf1 = unpack_archive(file1, temp_dir1)
    conf2 = unpack_archive(file2, temp_dir2)

    print(f"Parsing configuration file: {conf1}")
    vs_config_1 = parse_bigip_conf(conf1)

    print(f"Parsing configuration file: {conf2}")
    vs_config_2 = parse_bigip_conf(conf2)

    print("Comparing configurations...")
    discrepancies = compare_virtual_servers(vs_config_1, vs_config_2)

    if discrepancies:
        print("Discrapancy found")
        # Get current date and time for results file name
        now = datetime.datetime.now()
        outputfile = "results-" + now.strftime("%Y-%m-%d-%H:%M.txt")
        try:
            with open(outputfile, "x") as f:
                    for discrepancy in discrepancies:
                        f.write(discrepancy)
        except FileExistsError:
            print("File Already exists.")

    else:
        print("\nNo discrepancies found. The configurations are identical.")

    # Clean up temporary directories
    print("Cleaning up temporary files...")
    for temp_dir in [temp_dir1, temp_dir2]:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_f5_configs.py <file1> <file2>")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    main(file1, file2)