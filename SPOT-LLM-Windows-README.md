
# SPOT-LLM Windows Environment Setup

This guide provides step-by-step instructions to set up a working Python development environment on **Windows** for running and testing SPOT-related scripts in the `SPOT-LLM` project. It includes virtual environment setup, package installation, and connectivity verification.

---

## Prerequisites

Make sure you have **Python 3.13** installed. If you're unsure what version you have, open your terminal (search "Terminal" or "Command Prompt") and check via:

```bash
py.exe -3 --version
```
Or the Python command your terminal uses (e.g. "python3 --version").
---

## Virtual Environment Setup

1. **Install `virtualenv`**:
   ```bash
   py.exe -3 -m pip install virtualenv
   ```

2. **Upgrade `pip` (if needed)**:
   ```bash
   # Your Python executable full path
   C:\Users\...\Python\Python313\python.exe -m pip install --upgrade pip
   ```

3. **Create the virtual environment**:
   ```bash
   py.exe -3 -m virtualenv my_spot_env
   ```
Your environment will be named my_spot_env, but feel free to name it anything else!

4. **Activate the environment**:
   ```bash
   .\my_spot_env\Scripts\activate.bat
   ```

---

## Install Required SPOT SDK Packages

If the `bosdyn` packages are not yet installed or need upgrading:

### Upgrade all packages:
```bash
py.exe -3 -m pip install --upgrade bosdyn-client bosdyn-mission bosdyn-choreography-client bosdyn-orbit
```

### Or install a specific version:
```bash
py.exe -3 -m pip install bosdyn-client==4.1.1 bosdyn-mission==4.1.1 bosdyn-choreography-client==4.1.1 bosdyn-orbit==4.1.1
```

---

## Verify Package Installation

Run the following command to ensure all `bosdyn` packages are installed:

```bash
py.exe -3 -m pip list --format=columns | findstr bosdyn
```
This should list the following packages:
- bosdyn-api
- bosdyn-choreography-client
- bosdyn-choreography-protos
- bosdyn-client
- bosdyn-core
- bosdyn-mission
- bosdyn-orbit
---

## Connect to SPOT

Use this command to check if you can connect to SPOT with the installed SDK:

```bash
py.exe -3 -m bosdyn.client 192.168.80.3 id
```
This asks SPOT to send you its ID. If you receive a response you have successfully completed this step!
---

## Run a Sample SDK Script (`hello_spot.py`)

Before running, make sure to:
- Confirm `my_spot_env` contains the `spot-sdk` folder. You can do this by checking within your folder or "ls" within your terminal.
- Navigate to the folder containing `hello_spot.py`.

Then run the following:

```bash
set BOSDYN_CLIENT_USERNAME=user
set BOSDYN_CLIENT_PASSWORD=password
py.exe -3 hello_spot.py
```

---

## Run Other Sample Scripts

You may also run other example SDK scripts:

```bash
py.exe -3 arm_walk_to_object.py
```

---

## Troubleshooting

- If commands fail, verify that the virtual environment is activated.
- Double-check that packages were installed **inside** `my_spot_env`.
- If `spot-sdk` folder is missing, ensure you have cloned the SDK repository correctly.