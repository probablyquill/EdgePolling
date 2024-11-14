# Edge Monitoring

This is a tool for monitoring a NetInsight Edge installation via their provided API. This system includes email alerts,
as well as maintaining an SQL database for other systems such as Grafana to monitor. 

## Installation

Use the package manager to install all python dependencies.

```bash
pip3 install -r requirements.txt -y
```

This system also requires a MySQL installation, with an existing database. User permissions can be configured as needed.

The config_example.json file has an example configuration file which must be updated to suit your installation.

## Usage

Configure the config_examples.json file to have all necessary information and API keys, then rename it to config.json.

To test the that the Polling can sucessfully reach the Edge installation and write to the SQL database, run the following command.

```bash
python3 CheckConfig.py
```

If the config is found to be valid, then you can launch the program using the following command.

```bash
python3 run.py
```

Please note that the config check only validates that information has been entered, if incorrect settings are given it will cause other problems in the program.

## License
All code is provided as-is and is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.
