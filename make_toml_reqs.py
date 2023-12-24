import toml

# Read requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

# Load existing pyproject.toml
with open('pyproject.toml', 'r') as f:
    pyproject = toml.load(f)

# Add dependencies to pyproject.toml
pyproject['project']['dependencies'] = [{'name': req.split('==')[0], 'version': req.split('==')[1]} for req in requirements if '==' in req]

# Write back to pyproject.toml
with open('pyproject.toml', 'w') as f:
    toml.dump(pyproject, f)