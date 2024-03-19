# Edge Monitoring

This is a tool for monitoring a NetInsight Edge installtion via their provided API. This system includes email alerts,
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

```bash
python3 run.py
```

## License
All code is provided as-is and is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.