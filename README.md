# metex-voltage-recorder
Record your mains voltage and see the chart from last 24 hours in a web browser

## How to run
- Connect the Metex M-3640D (or similar) to your computer via a DB9 <-> USB adapter and note the virtual COM port installed along with the adapter's drivers.
- Switch Metex into AC mode and connect it to mains. Make sure it measures mains voltage.
- Edit the COM port in `run2.bat` so it is the same as the port you noted previously.
- Run `run2.bat`.
- Run `nginx.exe`.

You can now access the voltage chart by typing `localhost` in your web browser. All the data is recorded in `data/data.csv`.

## Using the metex simulator
If you don't have a real Metex multimeter, you can use a simulator for testing/debugging purposes. To use it:
- Download, install and run `com0com`.
- Add a pair of connected virtual COM ports (say COM12 and COM13).
- Run `metex_simulator.py COM12`.
- Edit the COM port in `run2.bat` (in this example, it would be COM13).
- Run `run2.bat`.
- Run `nignx.exe`.

## Listing available COM ports
You can use `list_ports.bat` to list available COM ports.
