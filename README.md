# spmigration
### This is a commandline script for service pack migration in SUSE Manager v3.x. ###


### Motivation: ###
__SUSE Manager is the best Patch and Configuration Management Tool for Linux Systems, mainly for SLES but also supports RHEL, CentOS, Ubuntu, OpenSUSE, Containers and more will come. The reason for me to write something for Service Pack Migration is due to the fact that Service Pack Migration for SLES systems can only be done by mouse clicks in the web UI or using spacecmd command which is quite longly if you have a maintenance window and need to run SP Migration for hundreds of SLES systems.__

_This program should give you some ideas how a such task could be automated by using SUSE Manager API._

**I would appreciate any help, bug fixing, code optimization and testing feedbacks to me.**

Which scenarios are covered by the scripts:
* __Parameters:__ - enter your base channel label, target base channel label, the current sp version and target sp version. See spmigration.py -h
* __Checking system availability prior Migration start__ - Then the script will use SUSE Manager API to get a list of all systems matching the base channel and query api to check if the systems have been marked as "inactive". Inactive systems will be pulled out from the systems list.
* __Checking salt minion online status__ - Then the script will take the matching list of systems and issue salt hostname test.ping to check if the system is only.
* __Avoid job creation for offline systems__ - If salt test.ping is successful then a service pack migration **job** in SUSE Manager with the given target sp version will be created, for each single node.
* __Schedule Jobs in SUSE Manager__ - A job ID will be returned.

## Sample command: ##

```suma:~/myscripts # python spmigration.py -s bjsuma.bo2go.home -u bjin -p suse1234 -base dev-sles12-sp3-pool-x86_64 -newbase dev-sles12-sp4-pool-x86_64 -fromsp sp3 -tosp sp4```

If __`-x`__ is not specified the SP Migration is always a **dryRun**.
Check Job status of the system if dryrun was successful before run the above command with -x specified.

## Download and try it! ##
```git clone https://github.com/bjin01/spmigration```


### See here additional command arguments: ###

optional arguments:

  -h, --help            show this help message and exit
  
  -x, --execute_migration __THIS parameter is the real _fire_ button__ :shipit:
  
  
  -s SERVER, --server SERVER
  
 Enter your suse manager host address e.g. myserver.abd.domain
                        
                        
  -u USERNAME, --username USERNAME
  
 Enter your suse manager loginid e.g. admin
                        
                        
  -p [PASSWORD]         Enter your password
  
  
  -base CURRENT_BASE_CHANNEL, --current_base_channel CURRENT_BASE_CHANNEL
  
  Enter the current base channel label. e.g. sles12-sp3-pool-x86_64
                        
                        
  -newbase NEW_BASE_CHANNEL, --new_base_channel NEW_BASE_CHANNEL
  
  Enter the new base channel label. e.g. sles12-sp4-pool-x86_64
                        
                        
  -fromsp MIGRATE_FROM_SERVICEPACK, --migrate_from_servicepack MIGRATE_FROM_SERVICEPACK
  
 Enter the current service pack version e.g. sp3 , of course you can jump from sp3 to sp5 as well.
                        
                        
  -tosp MIGRATE_TO_SERVICEPACK, --migrate_to_servicepack MIGRATE_TO_SERVICEPACK
  
 Enter the target service pack version e.g. sp4 , of course you can jump from sp3 to sp5 as well.
