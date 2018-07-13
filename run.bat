rem cd www
rem start cmd /c "python -m SimpleHTTPServer 80"
rem cd ..
start cmd /c "python reg.py COM15 | tee data/raw_data.csv | python ac_voltage_extractor.py > data/data.csv"
start cmd /c "python json_builder.py data/data.csv www/voltages.json"
