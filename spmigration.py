#!/usr/bin/python
import xmlrpclib,  argparse,  getpass,  textwrap
from mymodules import saltping
from datetime import datetime
from mymodules import checkactivesystems
from mymodules import newoptchannels
#from mymodules import sumalogin

class Password(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if values is None:
            values = getpass.getpass()

        setattr(namespace, self.dest, values)

parser = argparse.ArgumentParser()
#parser.add_argument("-v", "--verbosity", action="count", default=0)
parser = argparse.ArgumentParser(prog='PROG', formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\
This scripts runs service pack migration for given base channel. 

Sample command:

              python spmigration.py -s bjsuma.bo2go.home -u bjin -p suse1234 -base dev-sles12-sp3-pool-x86_64 -newbase dev-sles12-sp4-pool-x86_64 -fromsp sp3 -tosp sp4 \n \

If -x is not specified the SP Migration is always a dryRun.
Check Job status of the system if dryrun was successful before run the above command with -x specified. ''')) 
parser.add_argument("-x", "--execute_migration", action="store_true")
parser.add_argument("-s", "--server", help="Enter your suse manager host address e.g. myserver.abd.domain",  default='localhost',  required=True)
parser.add_argument("-u", "--username", help="Enter your suse manager loginid e.g. admin ", default='admin',  required=True)
parser.add_argument('-p', action=Password, nargs='?', dest='password', help='Enter your password',  required=True)
parser.add_argument("-base", "--current_base_channel", help="Enter the current base channel label. e.g. sles12-sp3-pool-x86_64 ",  required=True)
parser.add_argument("-newbase", "--new_base_channel", help="Enter the new base channel label. e.g. sles12-sp4-pool-x86_64 ",  required=True)
parser.add_argument("-fromsp", "--migrate_from_servicepack", help="Enter the current service pack version e.g. sp3\n of course you can jump from sp3 to sp5 as well.",  required=True)
parser.add_argument("-tosp", "--migrate_to_servicepack", help="Enter the target service pack version e.g. sp4\n of course you can jump from sp3 to sp5 as well.",  required=True)
args = parser.parse_args()

MANAGER_URL = "http://"+ args.server+"/rpc/api"
MANAGER_LOGIN = args.username
MANAGER_PASSWORD = args.password
client = xmlrpclib.Server(MANAGER_URL, verbose=0)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)
today = datetime.today()
earliest_occurrence = xmlrpclib.DateTime(today)

#print('lets see execute_migration value: %s'%(args.execute_migration))
if args.execute_migration:
    dryRun = 0
else:
    dryRun = 1

L = []
previous_sp = args.migrate_from_servicepack
new_sp = args.migrate_to_servicepack
base_channel = args.current_base_channel
new_base_channel = args.new_base_channel

checksystems = checkactivesystems.checkInactives(client,  key,  args.username,  args.password)
activesystems = checksystems.getactive_systems()
print(activesystems)

for server in activesystems:
    s = server.get('id')
    basech_name = client.system.listSubscribableBaseChannels(key, s)
    availpkgs = client.system.listLatestUpgradablePackages(key,  s)

    for a in basech_name:
       if a['current_base'] == 1:
            print('%s: %s '%(server['name'], a['label']))
            L.append(a['name'])
            getoptchannels = newoptchannels.getnew_optionalChannels(client, key, s)
            optionalChannels = getoptchannels.find_replace(previous_sp, new_sp)
            if a['label'] == base_channel and len(availpkgs) <=3 :
                print('\nChecking system through salt %s test.ping: \n' %(server['name']))                
                p1 = saltping.mysalt(server['name'])
                p1.ping() 
                #print('The server is not ready for salt: %s'%(server['name']))
                #print('p1.code is: %d' %(p1.code))
                if p1.code == 0:
                    try:
                        #print('lets see key, s, new_base_channel childchannels, dryRun',  key, s, new_base_channel, optionalChannels, dryRun)
                        spjob = client.system.scheduleSPMigration(key, s,  new_base_channel,  optionalChannels,  dryRun,  earliest_occurrence)
                        print('A new job has been scheduled with id: %d' %(spjob))
                    except:
                        print('something went wrong with system while scheduling job with client.system.scheduleSPMigration %s'%(server['name']))
            elif a['label'] == base_channel:
                print('\033[1;31;40m%s The system need to be updated prior SPMigration. It still has upgradable pkgs: %d \033[1;32;40m'%(server['name'], len(availpkgs)))
client.auth.logout(key)