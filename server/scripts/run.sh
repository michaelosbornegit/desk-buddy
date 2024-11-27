# source me! using source ./script.sh
# or . ./script.sh
cd ../
python3 -m venv env
source ./env/bin/activate
flask --app app run --host=0.0.0.0 --debug
deactivate
