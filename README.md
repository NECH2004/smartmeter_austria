[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

[![GitHub Activity][commits-shield_y]][commits]
[![GitHub Activity][commits-shield_m]][commits]
[![GitHub Activity][commits-shield_w]][commits]


[![Validate][validate-shield]][validation]

<!--
[!Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
-->

# Smartmeter Austria
Integration of smart meter for electricity into Home Assistant.
Component to integrate with a Austrian smart meter using its wired M-BUS interface.
EVN, SALZBURGNETZ and TINETZ are supported.

**This component will set up the following platform.**

Platform | Description
-- | --
`sensor` | Show information from the Smartmeter Austria smart meter.

<!-- ![example][exampleimg] -->

## Installation

1. If you do not have a `custom_components` directory (folder) there, you need to create it.
2. In the `custom_components` directory (folder) create a new folder called `smartmeter_austria`.
3. Download _all_ the files from the `custom_components/smartmeter_austria/` directory (folder) in this repository.
4. Place the files you downloaded in the new directory (folder) you created.
5. Restart Home Assistant
6. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Smart Meter Austria"

## Configuration is done in the UI

1. Select the COM port of your M-BUS to USB converter: eg. /dev/ttyUSB0
2. You can configure the default poll interval (30s) using the configuration link of the integration. It can be set between 10 and 3600 seconds.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

You should use Visual Studio Code to develop in a container. In this container you
will have all the tools to ease your python development and a dedicated Home
Assistant core instance to run your integration. See `.devcontainer/README.md` for more information.
Run the appropriate requirement task to install the requirements for development or test.

# Notice

This integration is under construction.
Some functions are missing yet.

# Information
The smart meter uses DLMS/COSEM and the OBIS naming model in its protocol.
[DLMS](https://www.dlms.com/dlms-cosem/overview)
[OBIS codes](https://onemeter.com/docs/device/obis/)

Following OBIS codes are provided:
OBIS-Code | Attribute | German description | Unit
-- | -- | -- | --
0-0:1.0.0.255,1 | Clock Attribute 1 | |
0-0:1.0.0.255,2 | Clock attribute 2 | | 
0-0:96.1.0.255 | Zählernummer | device number | |
0-0:42.0.0.255 | COSEM logical device name | logische Zählernummer (COSEM) |
1-0:32.7.0.255 | Voltage L1 | Spannung L1 | V |
1-0:52.7.0.255 | Voltage L2 | Spannung L2 | V* |
1-0:72.7.0.255 | Voltage L3 | Spannung L3 | V* |
1-0:31.7.0.255 | Current L1| Strom L1 | A |
1-0:51.7.0.255 | Current L2 | Strom L2 | A* |
1-0:71.7.0.255 | Current L3 | Strom L3 | A* |
1-0:1.7.0.255 | Effective Power consumed +P | Wirkleistung Bezug +P | W |
1-0:2.7.0.255 | Effective Power retured -P | Wirkleistung Lieferung -P | W |
1-0:1.8.0.255 | Active Energy consumed +A | Wirkenergie Bezug +A | Wh |
1-0:2.8.0.255 | Active Energy retured -A | Wirkendergie Lieferung -A | Wh |
1-0:3.8.0.255 | Reactive energy consumed +R | Blindenergie Bezug +R | varh |
1-0:4.8.0.255 | Reactive energy returned -R | Blindenergie Lieferung -R | varh |

* Values are available only on three-phase meters

### Additional information
[SALZBURGNETZ Kundenschnittstelle](https://www.salzburgnetz.at/content/dam/salzburgnetz/dokumente/stromnetz/Technische-Beschreibung-Kundenschnittstelle.pdf)

[TINETZ Smart Meter](https://www.tinetz.at/uploads/tx_bh/tinetz_bedienungsanleitung_display_konfiguration.pdf?mod=1644495901)


### Room for improvements
The integration is done using the poll method. Perhaps it would be better to switch to push but I didn't want to float Home Assistant by its values (every 5 s).

# Thanks
Special thanks to Stefan (@tirolerstefan) who did an excellent work to read out the Kaifa MA300 smart meters used by TINETZ and EVN.
I've used some parts of his code (mainly decrypt) as starting point here.
[tirolerstefan/kaifa repository](https://github.com/tirolerstefan/kaifa)

***

<!-- HACS-Default-orange.svg?style=for-the-badge -->
[releases-shield]: https://img.shields.io/github/v/release/NECH2004/smartmeter_austria?style=for-the-badge
[releases]: https://github.com/NECH2004/smartmeter_austria/releases

[commits-shield_y]: https://img.shields.io/github/commit-activity/y/NECH2004/smartmeter_austria?style=for-the-badge
[commits-shield_m]: https://img.shields.io/github/commit-activity/m/NECH2004/smartmeter_austria?style=for-the-badge
[commits-shield_w]: https://img.shields.io/github/commit-activity/w/NECH2004/smartmeter_austria?style=for-the-badge
[commits]: https://github.com/NECH2004/smartmeter_austria/commits/dev

[validate-shield]: https://github.com/NECH2004/smartmeter_austria/actions/workflows/validate.yml/badge.svg?branch=dev
[validation]: https://github.com/NECH2004/smartmeter_austria/actions/workflows/validate.yml

[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]:https://img.shields.io/github/license/NECH2004/smartmeter_austria?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Christian%20Neumeier%20%40NECH2004?style=for-the-badge

[smartmeter_austria]: https://github.com/NECH2004/smartmeter_austria
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
