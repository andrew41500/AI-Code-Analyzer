"""
Sample Python code for testing the AI Code Reviewer.

This file contains intentionally imperfect code to demonstrate
the code review capabilities of the tool.
"""

# Missing docstring for module
import os
import sys

# Global variable without proper naming convention
myVar = 10

# Function with style issues
def calculate_sum(a,b):
    # Missing docstring
    result=a+b
    return result

# Class with issues
class DataProcessor:
    # Missing docstring
    def __init__(self):
        self.data = []
    
    def process(self, items):
        # Missing docstring
        # Potential bug: no input validation
        for item in items:
            self.data.append(item*2)
        return self.data
    
    def get_data(self):
        # Missing docstring
        return self.data

# Function with potential security issue
def read_file(filename):
    # Missing docstring
    # Security issue: no path validation
    with open(filename, 'r') as f:
        return f.read()

# Function with logic error
def divide_numbers(a, b):
    # Missing docstring
    # Bug: no division by zero check
    return a / b

# Unused import
import json

# Code with poor naming
def fn(x):
    # Missing docstring
    y = x * 2
    z = y + 10
    return z

# Main execution
if __name__ == "__main__":
    # Example usage
    result = calculate_sum(5, 10)
    print(f"Sum: {result}")
    
    processor = DataProcessor()
    data = processor.process([1, 2, 3, 4, 5])
    print(f"Processed data: {data}")
    
    # This would cause an error
    # result = divide_numbers(10, 0)


