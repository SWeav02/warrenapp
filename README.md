<!-- This displays entry text -->
<h1><p align="center">
Welcome to the Warren Lab's extension app for
</h1></p>
<!-- This displays the Simmate Logo -->
<p align="center" href=https://github.com/jacksund/simmate>
   <img src="https://github.com/jacksund/simmate/blob/main/src/simmate/website/static_files/images/simmate-logo-dark.svg?raw=true" width="300" style="max-width: 700px;">
</p>

## **_PLEASE NOTE_: We have incorporated the features of this repo directly into the Simmate package. We are aware that most people interested in this package are interested in the BadELF algorithm published in JACS (https://doi.org/10.1021/jacs.3c10876), and we believe this merging will ease the installation and usage of the algorithm. To install the most up-to-date version of BadELF, follow the instructions immediately below. If you still wish to use this original repo, follow the instructions under "Installation of the Warren Lab Extension"**

### Requirements for using BadELF in Simmate
1. To use the BadELF algorithm, you must have the [Henkelman group's Bader software](https://theory.cm.utexas.edu/henkelman/code/bader/) installed.
2. For full functionality, you must have the [Vienna Ab-Initio Simulation Package](https://www.vasp.at/) installed.

### How to Install using Current Simmate (Recommended)
The most up-to-date version of BadELF is available in Simmate. We suggest using this version, as there have been significant speed improvements and updates since the original publication.
1. Follow the instructions for [installing Simmate](https://jacksund.github.io/simmate/getting_started/installation/quick_start/). You may skip starting the local server if you are not interested in using other features of Simmate.
2. Follow the instructions for [installing the BadELF app in Simmate](https://jacksund.github.io/simmate/apps/badelf/). This page also contains the information for using the BadELF app, and will continue to be updated in the future as the app is developed.
3. If you would like to automatically use our recommended VASP single-point energy calculation settings prior to running BadELF, follow the instructions for [installing the Warren Lab app in Simmate](https://jacksund.github.io/simmate/apps/warren_lab/). This app contains presets and workflows to automate BadELF and other calculations. Please note that you must install VASP seperately for this app to work.

### How to Use BadELF
If everything is installed properly, the BadELF algorithm can be run in a folder with VASP results. Please note that your VASP settings must produce a CHGCAR and ELFCAR with the same grid size.
```shell
simmate badelf run
```
If you would prefer to have Simmate handle the VASP calculation (VASP still must be installed), there are Simmate workflows that will first run the required DFT and then BadELF. For usage of these types of workflows, we recommend following along with the [Simmate documentation](https://jacksund.github.io/simmate/getting_started/run_a_workflow/quick_start/). Once you're familiar, we recommend looking at the command `simmate workflows explore` which you can use to investigate what types of workflows and settings are available to you.

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
