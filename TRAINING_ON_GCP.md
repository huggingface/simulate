# Running Simulate on GCP

## Setting up the VM

We recommend using Google’s [Deep Learning VM](https://cloud.google.com/deep-learning-vm) to quickly suitable a compatible VM instance.

In addition, we recommend attaching a GPU in order to render camera observations and train more quickly. We also recommend setting the vCPU count to be as high as possible.

## Installing Dependencies for Headless Rendering

In order to perform offscreen rendering, the are a number of additional dependencies to install.

Please run the following:

```
sudo apt update
sudo apt upgrade
sudo apt install -y xorg-dev libglu1-mesa libglu1-mesa-dev libgl1-mesa-dev freeglut3-dev mesa-common-dev xvfb libxinerama1 libxcursor1 mesa-utils
sudo apt-get install xserver-xorg
Now we need to identify which busid your GPU is using:
```

Now we need to identify which busid your GPU is using and add it to your xorg config file:

```
# run this command to find your GPU bus id (for example PCI:0:30:0)
nvidia-xconfig --query-gpu-info
# replace the busid flag with your value
# Note: with headless GPUs (e.g. Tesla T4), which don't have display outputs, remove the --use-display-device=none option
sudo nvidia-xconfig --busid=PCI:0:30:0 --use-display-device=none --virtual=1280x1024
```

We can now start an X server:

```
sudo Xorg :0
```

Run the following to confirm that offscreen rendering is working.

```
DISPLAY=:0 glxinfo | grep version
DISPLAY=:0 glxgears
nvidia-smi # xorg should show up in the running programs
```

**Important!** The DISPLAY=:0 envirionment variable must be set befire you launch Simulate.

```
export DISPLAY=:0
```

## Install Simulate

Your VM is now set up for headless training. Follow the installation instructions from the [README](https://github.com/huggingface/simulate#readme)