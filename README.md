# Getting Set Up
Start with this excellent guide by [@asln82N](https://github.com/asln82Ns) to get set up with a telegram bot and setup the script.

https://github.com/asln82Ns/Config-Monitoring 

# Using This Script
This script has some additional changes to restart on various conditions.

To allow the script to restart the node without a sudo password, edit the sudoers file.
This assumes that you're running the script as the dagger user.

Open the file for editing:
<pre>
sudo visudo
</pre>

Add this line:
<pre>
dagger ALL=(ALL) NOPASSWD: /usr/bin/systemctl
</pre>
