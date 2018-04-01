# Build a cryptocurrency catalog app
This is a web application that provides a list of cryptocurrency items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.


## Install Vagrant and Virtual Box
### 1. Installing a Linux VM with Vagrant
We have put together a Linux virtual machine (VM) configuration that already contains the PostgreSQL database software. To run it, you will need to install three things on your computer (if you don't already have them):

The VirtualBox VM environment
The Vagrant configuration program

#### Installing VirtualBox
VirtualBox is the program that runs your Linux virtual machine. Install it from this [site](https://www.virtualbox.org/wiki/Downloads). Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

#### Installing Vagrant
Vagrant is the program that will download a Linux operating system and run it inside the virtual machine. Install it from this [site](https://www.vagrantup.com/downloads.html).

Windows users: The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

### 2. Clone the fullstack-nanodegree-vm repository
[here](https://github.com/MinchanJun/fullstack-nanodegree-vm.git). Put this file into a new directory (folder) on your computer. Using your terminal, change directory (with the cd command) to catalog directory, then run


### 3. Run the virtual machine!
Using the terminal, change local directory to fullstack/vagrant/catalog (cd fullstack/vagrant/catalog), then type vagrant up to launch your virtual machine.



Once it is up and running, type vagrant ssh to log into it. This will log your terminal in to the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type exit at the shell prompt.  To turn the virtual machine off (without deleting anything), type vagrant halt. If you do this, you'll need to run vagrant up again before you can log into it. Be sure to change to the /vagrant directory by typing cd /vagrant in order to share files between your home machine and the VM.

```
vagrant up

vagrant ssh

cd /vagrant
```


### 4. Run your application within the VM by typing
```
python /vagrant/catalog/models.py
python /vagrant/catalog/project.py
```
into the Terminal.
### 6. Access and test your application
visit locally
```
http://localhost:(your host)
```

### 7. Requirements
#### Google sign in
1. Go to your app's page in the Google APIs Console — https://console.developers.google.com/apis
2. Choose Credentials from the menu on the left.
3. Create an OAuth Client ID.
4. This will require you to configure the consent screen, with the same choices as in the video.
5. When you're presented with a list of application types, choose Web application.
6. You can then set the authorized JavaScript origins, with the same settings as in the video.
7. You will then be able to get the client ID and client secret.
8. Click a download link and change the file name to "client_secrets.json" and save it on the directory where my project.py file locates

#### Facebook sign in
1. Go to your app's page in the Google APIs Console —
https://developers.facebook.com/
2. create fb_client_secrets.json on the same directory as project.py file
    ```
    {
      "web": {
        "app_id": "PASTE_YOUR_APP_ID_HERE",
        "app_secret": "PASTE_YOUR_CLIENT_SECRET_HERE"
      }
    }
    ```

3. Click + Add Product in the left column.
4. Find Facebook Login in the Recommended Products list and click Set Up.
5. Click Facebook Login that now appears in the left column.
6. Add http://localhost:5000/ to the Valid OAuth redirect URIs section.

### 8. What's not pushed on this repo
- client_secrets.json (Google sign in requirements)
- fb_client_secrets.json (Facebook sign in requirements)


### 9. Usage
1. Click login button to login to the website using third party app.

## Authors
Minchan Jun

## License
