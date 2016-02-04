M2M demo GUI client
===================

This is a demo web client for the M2M capability - an experimental API providing programmatic access to manageability data, available in IOS-XR from version 6.0 onwards. This app allows the following:

  * Connect to an IOS-XR device over SSH.
  * Explore the manageability schema used by M2M and Telemetry.
  * Explore the relationship between CLI and schema.
  * Write and execute simple Python scripts using the M2M API.
  * Generate policy files for Telemetry.
  * And more...

For example a user wanting to write a script using the M2M API to automate interface configuration across all of their devices needs to find which paths correspond to the configuration they're using, as well as what values they can set, and this web GUI can, to a certain extent, guide you through this process. You may also want to see some example scripts, or test some ideas out, and this lets you do that as well.

For more information about the new M2M capability, read the documentation [here](m2m.md).

Getting going
-------------
### Dependencies
The app has dependencies on the following:

  * Docker (optional)
  * Python 2.7
  * Twisted web
  * Twisted conch
  * OpenSSH client
  * Sass

Use of Docker is optional, but if you are using it then the remaining dependencies will be set up for you. If you're not using Docker, you'll need to install these yourself - if you're running Ubuntu, for example, this can be done by:

    sudo apt-get install python-twisted-conch python-twisted-web openssh-client ruby-sass

### On-box privileges
The `schema-describe` tool requires that the user you connect as has `cisco-support` privileges, not just the default `root-system`. You can check your user privileges by running `admin show running-config` and, if you don't see the line `group cisco-support` then run the following:

    admin config
    user <username> group cisco-support
    commit

### SSH
In order to connect to your IOS-XR device from the GUI client, you'll first need to set up SSH (for this you'll need a `k9` image):

  1. Configure an SSH server (on the router):

    `conf
    int Mgmt 0/0/CPU0/0
    no shut
    ipv4 addr dhcp
    ssh server
    commit`

  2. Generate an SSH fingerprint (on the router):

    `crypto key generate dsa`

  3. Generate a 1024-bit RSA key (on the server):

    `cd ~/.ssh
    ssh-keygen -b 1024 -t rsa -f <key-name>`

  4. Create a base64-decoded binary public key for the router (on the server):

    `cut -d" " -f2 <key-name>.pub | base64 -d > <key-name>.pub.b64`

  5. Copy the public key onto the router (on the server), e.g.

    `scp -o PreferredAuthentications=password -o PubkeyAuthentication=no ~/.ssh/<key-name>.pub.b64 <user>@<router-ip>:/disk0:`

  6. Import the public key (on the router), e.g.

    `crypto key import auth rsa disk0:/<key-name>.pub.b64`

Note that steps 3 and 4 may be skipped if using the built-in SSH key, which can be found in `src/assets/cisco_pubkey.b64`.

### Booting the Server
To boot up the GUI server, simply run `./run` from the root of the repository (if you're using Docker you'll need to pass the `-d` or `--docker` flag). You can then point your browser at the relevant IP address on port 8080, enter the credentials for your router in the `Connection` tab and you're away.

Note, if you're using Docker then the IP address won't necessarily be obvious. It'll be `localhost` if you're running natively on 64-bit linux, or the output of `docker-machine ip` or `boot2docker ip` etc otherwise.


Disclaimer
----------
The code in this repository was put together for demonstration purposes and so comes with a few caveats:

  * The server does not support HTTPS, meaning router credentials are exchanged in plaintext. Only run this app within your own network, or better still on your local machine.
  * Run the app in multiple tabs simultaneously is not supported.
  * Some operations are slow, in particular the 'Current Config' tab can take several minutes to calculate the correct mapping in the case of a large set of config.

Any comments/questions/bugs? Raise an [issue](https://github.com/cisco/xr-telemetry-m2m-web/issues).

