# iSmartHome

Installation:

```
cd /tmp
git clone https://github.com/danyial/iSmartHome.git
cd iSmartHome
chmod +x install.sh
./install.sh
```


Deinstallation:

```
cd /tmp
git clone https://github.com/danyial/iSmartHome.git
cd iSmartHome
chmod +x uninstall.sh
./uninstall.sh
```


Befehle ausführen lassen:

Die Datei Action.json kann dementsprechend angepasst werden.
Statt der DEVICE_ID_X wird die tatsächliche ID der Geräts verwendet.

```
{
	"Actions": [
		{
			"LID": "DEVICE_ID_1",
			"Attribute": "Value",
			"Value": "True",
			"Commands": [
				"sudo service hyperion restart"
			]
		},
		{
			"LID": "DEVICE_ID_2",
			"Attribute": "Value",
			"Value": "False",
			"Commands": [
				"hyperion-remote --priority 50 --color black",
				"sleep 2",
				"sudo service hyperion stop"
			]
		},
		{
			"LID": "DEVICE_ID_3",
			"Attribute": "DmLvl",
			"Value": "100",
			"Commands": [
				"echo Dimmer = 100%"
			]
		}
	]
}
```