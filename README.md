# Dagger Node Log Monitoring

## Getting Set Up
Do all the steps in this [excellent guide](https://github.com/asln82Ns/Config-Monitoring) by [@asln82N](https://github.com/asln82Ns) to get set up with a telegram bot and get the original script running as a service.

https://github.com/asln82Ns/Config-Monitoring 

## Using This Script

### How is it different from the original (above)

This script has some additional changes to restart on various conditions. 
- If no `is_up=true` is emitted within a threshold
- If more than N `is_up=false` occur within a window (disabled)
- If more than N errors occur within a window (disabled)

The windows, thresholds, and numbers of errors & down messages are configurable.

You can comment/uncomment lines to control what the script sends to telegram. Sending every error and down message is ok during normal testnet operation, but during an outage it's really spammy.

During the outage on 02/02, I found that the script was restarting the node too frequently, so this version has the is_up=false and error restarts commented out. Uncomment them if you still want them.

The script may still have bugs, I'll fix them as I find them but no guarantees.

### Additional setup

To allow the script to restart the node without prompting you for a sudo password, edit the sudoers file.
This assumes that you're running the script as the dagger user.

Open the file for editing:
<pre>
sudo visudo
</pre>

Add this line:
<pre>
dagger ALL=(ALL) NOPASSWD: /usr/bin/systemctl
</pre>
