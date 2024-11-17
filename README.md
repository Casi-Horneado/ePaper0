# NOTICE

this project is absolutely not complete.

# Materials

1. Raspberry Pi Zero WH (1st gen.)

2. Waveshare e-ink display (7.5inches - V2 - "old")

3. Corresponding Waveshare e-ink driver board

# Instructions

## PART A: on host machine

1. flash SD card  with Raspberry pi OS Lite (32 bit)

2. remove & re-insert Raspberry Pi 0 W SD card

3. add `ssh` file to `/boot` directory 

`sudo touch /media/$USER/rootfs/boot/ssh`

4. eject SD card

## PART B: on Raspberry Pi Zero WH

1. connect: display <-> driver board <-> RP0WH
2. Insert SD card & boot

## PART C: on host machine

1. ssh into RP0WH

2. download from GH & setup Rpi

`sh setup.sh`