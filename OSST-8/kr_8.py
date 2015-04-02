
import libvirt
import argparse
import xml.etree.cElementTree as ET


parser = argparse.ArgumentParser()
parser.add_argument('instance_name', type=str, help='Name of the instance')
parser.add_argument('action', type=str, help='create; start; stop; restart;')
args = parser.parse_args()
conn=libvirt.open("qemu:///system")
vm_name = args.instance_name
xml_file = 'xml/vm_template.xml'


def editXML(filename):
    tree = ET.ElementTree(file=filename)
    root = tree.getroot()

    for name in root.iter("name"):
        name.text = vm_name

    tree = ET.ElementTree(root)
    with open(filename, "w") as f:
        tree.write(f)


def create():
    # edit new vm_name from template at start new domian
    editXML(xml_file)
    reader = open(xml_file, 'r')
    vm_xml = reader.read()
    reader.close()

    conn.createXML(vm_xml, 0)

try:
    vm = conn.lookupByName(vm_name)
except libvirt.libvirtError:
    if args.action == "create":
        print 'Creating new Domian %s' % vm_name
    else:
        exit(1)



#power_on
def start():
    if vm.info()[0] == 1:
        print "VM isn't in stopped state"
    else:
        vm.create()
        print 'VM %s started' % vm.name()

#power_off
def stop():
    if vm.info()[0] == 5:
        print "VM is already stopped"
    else:
        vm.shutdown()
        print 'VM %s stopped' % vm.name()

def restart():
    if vm.info()[0] == 1:
        vm.reboot(0)
        print 'VM %s rebooted' % vm.name()
    else:
        print "Vm isn't in running state"


def delete():
    vm.destroy()
    print 'VM %s deleted' % vm.name()

def status():
    infos = vm.info()
    print 'Name =  %s' % vm.name()
    print 'State = %d' % infos[0]
    print 'Max Memory = %d' % infos[1]
    print 'Number of virt CPUs = %d' % infos[3]
    print 'CPU Time (in ns) = %d' % infos[2]
    print ' '

action_hash = {"create": create, "start": start, "stop": stop, "restart": restart, "delete": delete, "status": status}
action = action_hash.get(args.action)

action()



