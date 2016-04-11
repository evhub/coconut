rm -r ./_docs
sphinx-build -b html . ./_docs
cd ./_docs
cp ./README.html ./index.html
zip -r ./_docs.zip ./*
cd ..
PAUSE
