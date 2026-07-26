# AOI/SMT Data Validator

A Python-based portfolio project for validating bill-of-material and component-placement data used in AOI, SPI, and SMT programming workflows.

The application compares BOM data against placement data, identifies inconsistencies, normalizes manufacturing information, and generates both human-readable and JSON validation reports.

All products, part numbers, files, and manufacturing data in this repository are fictional and independently created for demonstration purposes.

## Project Purpose

Manufacturing programs often depend on multiple data sources, including:

* Bills of materials
* Component-placement files
* Footprint definitions
* Board-side assignments
* Rotation values
* Reference designators
* Part identifiers

Errors between these sources can cause missing components, duplicate placements, incorrect footprints, bottom-side programming problems, and inconsistent inspection results.

This project demonstrates how those data sources can be parsed, normalized, compared, and reported before being imported into AOI, SPI, or SMT programming software.

## Current Capabilities

### BOM Processing

* Parses BOM data from CSV files
* Groups reference designators by part ID
* Normalizes part IDs and reference designators
* Calculates quantity from grouped references
* Detects duplicate reference designators
* Detects conflicting part descriptions
* Detects conflicting footprint definitions
* Reports missing descriptions and footprints

### Placement Processing

* Parses component-placement data from CSV files
* Validates X and Y coordinates
* Validates top- and bottom-side assignments
* Normalizes component rotations to a range of 0 to 359 degrees
* Detects duplicate placements
* Detects missing coordinates
* Detects nonnumeric coordinate and rotation values
* Reports missing footprint information

### BOM-to-Placement Validation

* Detects BOM references missing from placement data
* Detects placements missing from the BOM
* Detects part-ID mismatches
* Detects footprint mismatches
* Consolidates parser errors and warnings
* Tracks correctly matched reference designators
* Produces an overall pass/fail result

### Reporting

* Displays a formatted validation report in the terminal
* Generates a text report
* Generates a structured JSON report
* Summarizes:

  * Unique BOM parts
  * Total BOM references
  * Total placements
  * Matched references
  * Top-side placements
  * Bottom-side placements
  * Errors
  * Warnings

### Automated Testing

The project includes automated tests for:

* BOM parsing
* Placement parsing
* Duplicate detection
* Missing-column detection
* Invalid coordinate handling
* Rotation normalization
* Part-ID comparison
* Footprint comparison
* Missing references
* Unexpected placements
* Text report generation
* JSON report generation

## Repository Structure

```text
aoi-smt-data-validator/
├── README.md
├── requirements.txt
├── sample_data/
│   ├── demo_bom.csv
│   └── demo_placements.csv
├── screenshots/
├── src/
│   └── aoi_validator/
│       ├── __init__.py
│       ├── bom_parser.py
│       ├── cli.py
│       ├── placement_parser.py
│       ├── report.py
│       └── validator.py
└── tests/
    ├── test_bom_parser.py
    ├── test_placement_parser.py
    ├── test_report.py
    └── test_validator.py
```

## Requirements

* Python 3.11 or newer
* `pytest` for automated testing

## Installation

Clone the repository:

```powershell
git clone https://github.com/JustinGottliebEngineering/aoi-smt-data-validator.git
cd aoi-smt-data-validator
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install -r requirements.txt
```

Set the source directory on the Python path for the current PowerShell session:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

## Running the Tests

Run the complete automated test suite:

```powershell
python -m pytest -v
```

All tests should pass before running or modifying the application.

## Usage

Run the validator against the included fictional sample files:

```powershell
python -m aoi_validator.cli `
    sample_data\demo_bom.csv `
    sample_data\demo_placements.csv
```

Generate both a text report and a JSON report:

```powershell
python -m aoi_validator.cli `
    sample_data\demo_bom.csv `
    sample_data\demo_placements.csv `
    --text-report output\validation_report.txt `
    --json-report output\validation_report.json
```

The command returns:

* Exit code `0` when validation passes
* Exit code `1` when validation errors are found
* Exit code `2` when an input file cannot be read or parsed

## Example Output

```text
====================================================================
AOI / SMT DATA VALIDATION REPORT
====================================================================

Overall Status:          PASS

SUMMARY
--------------------------------------------------------------------
Unique BOM Parts:       5
Total BOM References:   8
Total Placements:       8
Matched References:     8
Top-Side Placements:    6
Bottom-Side Placements: 2
Errors:                 0
Warnings:               1

ERRORS
--------------------------------------------------------------------
None

WARNINGS
--------------------------------------------------------------------
1. Placement parser: Row 6: rotation 360 for C2 was normalized to 0 degrees.
```

A normalized rotation warning does not cause the overall validation to fail.

## Input File Formats

### BOM CSV

Required columns:

```csv
part_id,reference,description,footprint
```

Example:

```csv
part_id,reference,description,footprint
RES-10K-0603,R1,10K Ohm Resistor,0603
RES-10K-0603,R2,10K Ohm Resistor,0603
CAP-100NF-0603,C1,100 nF Ceramic Capacitor,0603
```

### Placement CSV

Required columns:

```csv
reference,part_id,footprint,side,x_mm,y_mm,rotation_deg
```

Example:

```csv
reference,part_id,footprint,side,x_mm,y_mm,rotation_deg
R1,RES-10K-0603,0603,TOP,12.500,18.250,0
R2,RES-10K-0603,0603,TOP,14.750,18.250,90
C1,CAP-100NF-0603,0603,BOTTOM,20.100,22.400,180
```

Valid side values are:

```text
TOP
BOTTOM
```

## Example Validation Conditions

The validator can identify conditions such as:

```text
Reference R2 is listed in the BOM but is missing from placement data.
```

```text
Reference C4 appears in placement data but is not listed in the BOM.
```

```text
Reference U1 has part ID IC-DEMO-002 in placement data but IC-DEMO-001 in the BOM.
```

```text
Reference R1 has footprint 0805 in placement data but 0603 in the BOM.
```

## Engineering Concepts Demonstrated

This project demonstrates:

* Python package organization
* CSV parsing
* Data normalization
* Dataclasses
* Type hints
* Exception handling
* Cross-file validation
* Human-readable reporting
* JSON serialization
* Command-line interface development
* Automated testing with `pytest`
* Manufacturing-data workflow analysis
* AOI and SMT programming concepts

## Planned Improvements

Future development may include:

* Reference-designator format validation
* Panel and PCB step validation
* Panel-fiducial validation
* Duplicate part-definition reporting
* Configurable rotation rules
* Bottom-side rotation conversion rules
* Coordinate-unit conversion
* CSV column mapping
* ODB++ data abstraction
* Gerber-related metadata checks
* Interactive Flask interface
* Drag-and-drop file selection
* Downloadable validation reports
* Graphical top- and bottom-side placement maps
* GitHub Actions continuous integration
* Packaged Windows executable

## Confidentiality and Data Policy

This repository does not contain:

* Employer-owned source code
* Customer information
* Production BOMs
* Production placement files
* Gerber data
* ODB++ archives
* Firmware
* Internal network information
* Proprietary equipment configurations
* Confidential manufacturing procedures

All sample information was created specifically for this public demonstration.

## Professional Context

This project reflects practical experience with:

* AOI and SPI program development
* SMT placement programming
* BOM and placement-data troubleshooting
* Component-footprint management
* Top- and bottom-side component validation
* Panel and PCB manufacturing workflows
* Python-based production automation
* Manufacturing test engineering

## Project Status

Version `0.1.0` includes:

* BOM parsing
* Placement parsing
* Cross-validation
* Text reporting
* JSON reporting
* Command-line execution
* Automated tests

The project is under active development as part of a professional manufacturing-test engineering portfolio.
