#! /bin/bash
sudo apt update
sudo apt upgrade
python -m venv ePaper-venv
sudo sed -i.bak 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/firmware/config.>
# remove -i.bak to not backup config (in the same folder)
sudo reboot
