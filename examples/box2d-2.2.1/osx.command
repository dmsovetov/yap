cd "$(dirname $0)"

# Remove previous download
rm -rf src

# Download source distribution
curl -L https://box2d.googlecode.com/files/Box2D_v2.2.1.zip | tar zx

# Rename downloaded folder to src
mv Box2D_v2.2.1 src

# Generate Lua project
cd ../../
python yap.py --source examples/box2d-2.2.1/ --output examples/projects/Box2D.mac --name Box2D --platform MacOS