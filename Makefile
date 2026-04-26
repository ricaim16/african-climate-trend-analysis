PYTHON ?= venv/bin/python
SCRIPT := src/climate_analysis.py
INPUT ?= data/raw/example_climate_data.csv

.PHONY: run run-example

run:
	$(PYTHON) $(SCRIPT) --input $(INPUT)

run-example:
	$(PYTHON) $(SCRIPT) --input data/raw/example_climate_data.csv

test:
	$(PYTHON) -m pytest src/test_climate_analysis.py

serve:
	@echo "Serving reports at http://localhost:8000/outputs/summary_report.html"
	$(PYTHON) -m http.server 8000
