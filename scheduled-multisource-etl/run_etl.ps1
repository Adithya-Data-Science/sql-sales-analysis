# Example Windows Task Scheduler command target.
# Configure Task Scheduler to call this script on the desired cadence.
python etl.py --assets data/assets.csv --usage data/usage.json --db data/integration.db --log data/etl.log
