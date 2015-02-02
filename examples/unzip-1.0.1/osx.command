cd "$(dirname $0)"

# Download source distribution
curl -L http://www.winimage.com/zLibDll/unzip101h.zip | tar zx

# Generate Lua project
cd ../../
python yap.py --source examples/unzip-1.0.1/ --output examples/projects/unzip.mac --name unzip --platform MacOS