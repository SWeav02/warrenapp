<!-- This displays entry text -->
<h1><p align="center">
Welcome to the Warren Lab's extension app for
</h1></p>
<!-- This displays the Simmate Logo -->
<p align="center" href=https://github.com/jacksund/simmate>
   <img src="https://github.com/jacksund/simmate/blob/main/src/simmate/website/static_files/images/simmate-logo-dark.svg?raw=true" width="300" style="max-width: 700px;">
</p>

## **_PLEASE NOTE_: We are aware that most people interested in this package are here for the BadELF algorithm published in JACS (https://doi.org/10.1021/jacs.3c10876). As of January 2026 we have moved the core functionality of BadELF to the [BaderKit](https://github.com/SWeav02/baderkit) package and made significant updates to improve speed and memory usage. To install the most up-to-date version of BadELF, follow the instructions in the [BaderKit documenation](https://sweav02.github.io/baderkit/). We have also developed workflows similar to those in this repo which are now located in the [Simmate](https://github.com/jacksund/simmate) package. If you still wish to use this original repo, follow the instructions under "Installation of the Warren Lab Extension"**

## Installation of the Warren Lab Extension

### Requirements
1. This extension is built off of [Simmate](https://github.com/jacksund/simmate). In order to use it you must have the base Simmate package installed. The current version is built on top of Simmate 0.13.2 and does not work with the most up-to-date version of Simmate. Tutorials for simmate can be found [here](https://jacksund.github.io/simmate/getting_started/overview/).
2. To use the BadELF algorithm, you must have the [Henkelman group's Bader software](https://theory.cm.utexas.edu/henkelman/code/bader/) installed.
3. For full functionality, you must have the [Vienna Ab-Initio Simulation Package](https://www.vasp.at/) installed.

### How to Install
1. If you don't already have Simmate installed, follow the instructions to [install Simmate](https://jacksund.github.io/simmate/getting_started/installation/quick_start/)
``` shell
conda create -n my_env -c conda-forge python=3.11 simmate=0.13.2
conda activate my_env
simmate database reset
```
2. Install the warrenapp using pip
``` shell
pip install warrenapp
```
3. Register the warrenapp with simmate by adding `- warrenapp.apps.SimmateWarrenConfig` to ~/Home/simmate/my_env-apps.yaml
4. Update your database to include custom tables from the warrenapp
``` shell
simmate database update
```
