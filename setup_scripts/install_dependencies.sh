cd setup_scripts/
git submodule update --init
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt