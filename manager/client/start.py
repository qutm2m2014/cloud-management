#!/usr/bin/env python

"""
Manages activation of devices and setting of API KEY and FEED ID.
"""
import configparser
import requests
import os.path
import click
import hmac
from hashlib import sha1
import sys
import subprocess

API_END_POINT = "http://192.168.1.125/api/v1/"


def request_api_key(device_type, serial_number, activation_secret):
    """
    Request API credentials
    """
    activation_code = hmac.new(activation_secret.encode(
        encoding='UTF-8'), serial_number.encode(encoding='UTF-8'), sha1).hexdigest()
    activation_url = API_END_POINT + "devicetypes/" + device_type + "/devices/" + serial_number + "/activate"
    req = requests.post(activation_url, data={"activation_code": activation_code})
    return req.json()


def activate_device(config, configfile):
    # See if we already have the API key
    try:
        api_key = config.get('auth', 'api_key')
        print("Provisioning Details")
        print("API Key: %s" % (api_key))
        return config
    except:
        print("API Key not found")

    # No API key. Is the activation secret defined.
    try:
        activation_secret = config.get('provisioning', 'activation_secret')
    except:
        print("The activation secret was not defined in the config file. Giving up.")
        sys.exit(1)

    # Is the serial number defined in config. If not, fallback to hostname.
    try:
        serial_number = config.get('provisioning', 'serial_number')
    except:
        serial_number = subprocess.check_output("hostname", shell=True)
        if not serial_number:
            print("The serial was not defined in the config file. Giving up.")
            sys.exit(1)

    try:
        device_type = config.get('provisioning', 'device_type')
    except:
        print("The device type was not defined in the config file. Giving up.")
        sys.exit(1)

    try:
        response = request_api_key(device_type, serial_number, activation_secret)
        try:
            response["error"]
        except:
            pass
        else:
            print("Product activation failed: %s" % (response['error']))
            sys.exit(1)

        print('Device activation successful.')
        print('Device Type: %s' % (device_type))
        print('Serial Number: %s' % (serial_number))
        print('API Key: %s' % (api_key))

        if not config.has_section('auth'):
            config.add_section('auth')

        config.set('auth', 'api_key', api_key)
        with open(configfile, 'w') as configfile:
            config.write(configfile)
        return config
    except Exception as e:
        print("Product activation failed: %s" % (e))
        sys.exit(1)


def test_config_file(ctx, param, value):
    if os.path.isfile(value):
        return value
    else:
        raise click.BadParameter("%s is not a valid configuration file" % (value))


def open_config(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    return config


@click.command()
@click.option("--configfile", default="conf.ini", help="The path to the configuration file", callback=test_config_file)
def main(configfile):
    config = open_config(configfile)
    config = activate_device(config, configfile)


if __name__ == "__main__":
    main()
