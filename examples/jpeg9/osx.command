cd "$(dirname $0)"

# Download source distribution
curl -L http://www.ijg.org/files/jpegsrc.v9a.tar.gz | tar zx

# Rename
mv jpeg-9a src

cp src/jconfig.mac src/jconfig.h

# Generate project
#cd ../../
#python yap.py --source examples/jpeg9/ --output examples/projects/jpeg.mac --name jpeg --platform MacOS