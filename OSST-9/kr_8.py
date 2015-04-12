
import argparse

class libvirt_wrapper(object):

    def __init__(self, vm_name='test'):
        import libvirt
        self.conn=libvirt.open("qemu:///system")
        self.xml_file = 'xml/vm_template.xml'
        self.vm_name = vm_name
    
    def editXML(self, filename):
        import xml.etree.cElementTree as ET

        tree = ET.ElementTree(file=filename)
        root = tree.getroot()
    
        for name in root.iter("name"):
            name.text = self.vm_name
    
        tree = ET.ElementTree(root)
        with open(filename, "w") as f:
            tree.write(f)
    
    
    def create(self):
        self.editXML(self.xml_file)
        with open(self.xml_file, 'r') as f:
            vm_xml = f.read()
    
        self.conn.createXML(vm_xml, 0)
        return 'Vm %s was created' % self.vm_name
    
    def connect_to_libvirt(self):
        vm = self.conn.lookupByName(self.vm_name)
        return vm
    
    #power_on
    def start(self):
        vm = self.connect_to_libvirt()
        if vm.info()[0] == 1:
            print "VM isn't in stopped state" 
            return "VM isn't in stopped state"
    
    #power_off
    def stop(self):
        vm = self.connect_to_libvirt()
        if vm.info()[0] == 5:
            return "VM is already stopped"
        else:
            vm.shutdown()
            return 'VM %s stopped' % vm.name()
    
    def restart(self):
        vm = self.connect_to_libvirt()
        if vm.info()[0] == 1:
            vm.reboot(0)
            return 'VM %s rebooted' % vm.name()
        else:
            return "Vm %s isn't in running state" % vm.name()
    
    
    def delete(self):
        vm = self.connect_to_libvirt()
        vm.destroy()
        print 'VM %s deleted' % vm.name()
        return 'VM %s deleted' % vm.name()
    
    def list_vm(self):
        '''
        Vm list
        '''
        list_vm = []
        for id in self.conn.listDomainsID():
            vm_id = self.conn.lookupByID(id)
            vm_name = vm_id.name()
            list_vm.append(vm_name)
        print list_vm
        return list_vm
    
    
    def status(self):
        vm = self.connect_to_libvirt()
        infos = vm.info()
        print 'Name =  %s' % vm.name()
        print 'State = %d' % infos[0]
        print 'Max Memory = %d' % infos[1]
        print 'Number of virt CPUs = %d' % infos[3]
        print 'CPU Time (in ns) = %d' % infos[2]
        print ' '


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--instance_name', default='test' , type=str, help='Name of the instance')
    parser.add_argument('--action', default='list', type=str, help='create; start; stop; restart;')
    args = parser.parse_args()
    vm_name = args.instance_name
    wrapper = libvirt_wrapper(vm_name)

    action_hash = {
    "create": wrapper.create,
    "start": wrapper.start,
    "stop": wrapper.stop,
    "restart": wrapper.restart,
    "delete": wrapper.delete,
    "list": wrapper.list_vm,
    "status": wrapper.status}

    action = action_hash.get(args.action)
    action()

