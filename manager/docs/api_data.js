define({ api: [
  {
    "type": "get",
    "url": "/devicetypes",
    "title": "List of Device Types",
    "name": "GetDeviceTypes",
    "group": "DeviceType",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "field": "List",
            "optional": false,
            "description": "of Device Types"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "routes/api.py"
  }
] });