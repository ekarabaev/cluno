# Logistics Package

## Table of contents
  1. [Introduction](#introduction)
  2. [Installation](#installation)
  3. [Usage](#usage)
  
## Introduction
The package provides the following processing functionality for the logistics data:
  * Extract raw data from the HTTP endpoint with basic authorization
  * Transform _duration_ and _distance_ attributes from text-based description into numeric fields represented in minutes and meters, correspondingly
  * Save the enriched dataset as a local CSV file
  
## Installation
Install the package by running the following command
```shell
pip install -i https://test.pypi.org/simple/ cluno-logistics-task
```

## Usage
The following is a python snippet demonstrating basic usage of the package
```python
from logistics import converter
c = converter.Converter()
c.do_processing()
```