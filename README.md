---

# F5 UCS/QKView Configuration Comparison Script

This Python script compares the configured virtual servers between two F5 UCS backup files or QKView files. It identifies discrepancies in the virtual server configurations, including any differences in attributes, missing virtual servers, or missing attributes.

---

## Features
- Automatically unpacks UCS or QKView files using the `tarfile` module.
- Extracts and parses the `bigip.conf` file from the archive.
- Detects discrepancies between virtual servers in the two configuration files.
- Writes any discrepancies to a time-stamped results file.
- Handles temporary file cleanup after execution.

---

## Requirements

### Python Version
- Python 3.6 or above.

### Libraries
- No external libraries are required. All functionality is based on built-in Python modules (`tarfile`, `os`, `sys`, `re`, `datetime`, among others).

---

## Setup

Download the script and place it in your working directory.

### Files Needed
- Two UCS or QKView files to be compared.
- This script will extract the contents and identify the `bigip.conf` files for comparison.

---

## Usage

### Basic Command
Run the script with the paths to the UCS or QKView files as arguments:

```bash
python compare_f5_configs.py <file1> <file2>
```

### Example
```bash
python compare_f5_configs.py bigip1.qkview bigip2.qkview
```

Upon execution:
1. The script unpacks both UCS/QKView files into temporary directories.
2. Locates the `bigip.conf` file inside each archive.
3. Parses the virtual server configurations from the two `bigip.conf` files.
4. Compares the configurations and lists all discrepancies.

---

## Output

### Discrepancies Found
If discrepancies are identified, the script creates a time-stamped results file a detailed list of the differences. Example:

```
Virtual server 'vs_one' is missing in the first configuration.
Attribute 'ip' in virtual server 'vs_two' differs: '192.168.1.1' vs '192.168.1.2'.
Attribute 'port' in virtual server 'vs_three' is missing in the second configuration.
```

### No Discrepancies
If no differences are found between the configurations, the script reports the following:

```
No discrepancies found. The configurations are identical.
```

---

## Temporary File Cleanup

The script automatically cleans up temporary directories and extracted files after execution.

---

## Notes

### UCS and QKView Files
- UCS files are encrypted archives of F5 configurations. Ensure you have permissions to access and extract them.
- QKView files are diagnostic archives intended for troubleshooting.
- This script assumes the UCS or QKView files contain a `bigip.conf` file in their extracted contents.

---

## Troubleshooting

### Common Issues
1. **File not found**: Ensure the provided UCS/QKView file paths are correct.
2. **Missing `bigip.conf`**: The script searches for the `bigip.conf` file in the extracted contents. If it's missing, verify the completeness of the UCS/QKView file.
3. **Permission Errors**: If accessing the UCS or QKView file fails, check your file system permissions.

### Debugging
- To debug issues during execution, you can add print statements or use logging within the code.

---

## License

This script is provided as-is and is not affiliated with F5 Networks. You are free to modify and use it for your own purposes.

---

## Author

This script was written with the intention of simplifying the comparison of F5 UCS and QKView configurations. If you have suggestions or need additional features, feel free to reach out!

---