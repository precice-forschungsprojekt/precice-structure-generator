cd setup_scripts/
git submodule update --init
python -m venv venv
.\venv\Scripts\activate
pip install -r ../requirements.txt