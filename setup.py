from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'inoccu-py',
    packages = find_packages(),
    version = '0.0.1',
    description = """
        Receive near realtime alarms 
        when someone enters 
        in your second residence.
        """,
    long_description = long_description,
    long_description_content_type = "text/markdown",        
    author = 'Gustavo Martin Vela',
    license = 'MIT',
)