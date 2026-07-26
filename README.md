# AOI/SMT Data Validator

A Python-based demonstration utility for validating bill-of-material and component-placement data used in AOI, SPI, and SMT programming workflows.

This project uses fictional products and independently generated sample data. It does not contain employer-owned source code, production files, customer data, or proprietary manufacturing information.

## Project Goals

The application will demonstrate how manufacturing data can be normalized and validated before it is imported into inspection or component-placement software.

Planned validation functions include:

* Grouping reference designators by part ID
* Detecting duplicate or conflicting part definitions
* Identifying missing footprints
* Validating top- and bottom-side component assignments
* Checking component rotations
* Detecting missing or malformed reference designators
* Verifying panel and PCB step information
* Identifying missing panel fiducials
* Producing a readable validation report
* Exporting normalized JSON data

## Intended Inputs

The demonstration will use fictional files such as:

* `demo_bom.csv`
* `demo_placements.csv`
* `demo_panel.json`

No production BOMs, Gerber files, ODB++ archives, customer assemblies, or proprietary machine programs are included.

## Technology

* Python
* CSV and JSON processing
* Data normalization and validation
* Automated testing
* Optional Flask user interface

## Project Status

Initial project structure and fictional sample-data design are in progress.
