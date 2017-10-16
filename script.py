import csv

f = open('lab3b_check.txt', 'w')

class super_block:
    def __init__(self, inodes_count, blocks_count, block_size, blocks_per_group, inodes_per_group):
        self.inodes_count = inodes_count
        self.blocks_count = blocks_count
        self.block_size = block_size
        self.blocks_per_group = blocks_per_group
        self.inodes_per_group = inodes_per_group
#self.first_data_block = first_data_block

class inode:
    def __init__(self, inode_number, block_count, block_pointers, links_count):
        self.number = int(inode_number)
        self.block_count = int(block_count)
        self.block_pointers = block_pointers
        self.link_count = links_count
        self.ref_list = []

class block:
    def __init__(self, block_number):
        self.block_number = block_number
        self.ref_list = []

class directory:
    def __init__(self, parent_inode, child_inode, entry_number):
        self.parent_inode = parent_inode
        self.child_inode = child_inode
        self.entry_number = entry_number

superblock = super_block(0,0,0,0,0)
free_inode_list = []
free_block_list = []
allocated_inodes = {}
allocated_blocks = {}
indirect_pointer_list = []
indirect_dict = {}
directory_dict = {}
direct_c_p = {}
inode_bitmap = []
block_bitmap = []

def MULTIPLY_REFERENCED(block):
    f.write('MULTIPLY REFERENCED BLOCK < %s > BY' % (block.block_number))
    block.ref_list.sort()
    for index in block.ref_list:
        if index[1] == 0:
            f.write(' INODE < %s > ENTRY < %s >' % (index[0], index[2]))
        else:
            f.write(' INODE < %s > INDIRECT_BLOCK < %s > ENTRY < %s >' % (index[0], index[1], index[2]))

    f.write('\n')

def UNALLOCATED_BLOCK_ERROR(block):
    f.write('UNALLOCATED BLOCK < %s > REFERENCED BY' % (block.block_number))
    block.ref_list.sort()
    for i in range(0, len(block.ref_list)):
        if block.ref_list[i][1] == 0:
            f.write(' INODE < %s > ENTRY < %s >' % (block.ref_list[i][0], block.ref_list[i][2]))
        else:
            f.write(' INODE < %s > INDIRECT BLOCK < %s > ENTRY < %s >' % (block.ref_list[i][0], block.ref_list[i][1], block.ref_list[i][2]))

    f.write('\n')

def INCORRECT_DIRECTORY_ENTRY(inode_number, directory_name, incorrect_inode, correct_inode ):
    f.write('INCORRECT ENTRY IN < %s > NAME < %s > LINK TO < %s > SHOULD BE < %s >\n' % (inode_number, directory_name, incorrect_inode, correct_inode));

def INVALID_BLOCK_POINTER(block_number, inode_number, entry_number, indirect_block_number):
    if (indirect_block_number == 0):
        f.write('INVALID BLOCK < %s > IN INODE < %s > ENTRY < %s >\n' % (block_number, inode_number, entry_number))
    else:
        f.write('INVALID BLOCK < %s > IN INODE < %s > INDIRECT BLOCK < %s > ENTRY < %s >\n' % (block_number, inode_number, indirect_block_number, entry_number))

def UNALLOCATED_INODE_ERROR(inode_num, directory_inode, entry_num):
    f.write('UNALLOCATED INODE < %s > REFERENCED BY' % inode_num)
    
    f.write(' DIRECTORY < %s > ENTRY < %s >\n' % (directory_inode, entry_num))

def INCORRECT_ENTRY_ERROR(inode_num, entry_name, false_inode_num, correct_inode_num):
    f.write('INCORRECT ENTRY IN < %s > NAME < %s > LINK TO < %s > SHOULD BE < %s >\n' % (inode_num, entry_name.strip('"'), false_inode_num, correct_inode_num))

def MISSING_INODE_ERROR(inode_num, block_num):
    f.write('MISSING INODE < %s > SHOULD BE IN FREE LIST < %s >\n' % (inode_num, block_num))

def INCORRECT_LINK_COUNT(inode_num, incorrect_link, correct_link):
    f.write('LINKCOUNT < %s > IS < %s > SHOULD BE < %s >\n' % (inode_num, incorrect_link, correct_link))

def register_block(block_number, inode_number, indirect_block_number, entry_number):
    if block_number == 0 or block_number >= superblock.blocks_count:
        INVALID_BLOCK_POINTER(block_number, inode_number, entry_number, indirect_block_number)
    elif block_number in allocated_blocks:
        allocated_blocks[block_number].ref_list.append([inode_number, indirect_block_number, entry_number])
    else:
        new_block = block(block_number)
        allocated_blocks[block_number] = new_block
        allocated_blocks[block_number].ref_list.append([inode_number, indirect_block_number, entry_number])

def check_block_pointers():
    global superblock
    for j in allocated_inodes:
        number_blocks = allocated_inodes[j].block_count
        for i in range(0, number_blocks):
            if i < 12:
                block_number = allocated_inodes[j].block_pointers[i]
                if block_number == 0 or block_number >= superblock.blocks_count:
                    INVALID_BLOCK_POINTER(block_number, j, i, 0)
                else:
                    register_block(block_number, j, 0, i)
    
            elif i == 12:
                if allocated_inodes[j].block_pointers[12] == indirect_pointer_list[i][0]:
                    block_number = allocated_inodes[j].block_pointers[12]
                    indirect_block_number = int(indirect_pointer_list[i][2])
                    entry = indirect_pointer_list[i][1]
                    if block_number == 0 or block_number >= superblock.block_count:
                        INVALID_BLOCK_POINTER(block_number, j, entry, indirect_block_number)
                    else:
                        register_block(block_number, j, indirect_block_entry, i)

            elif i == 13 and block_number > 267:
                if allocated_inodes[j].block_pointers[13] == indirect_pointer_list[i][0]:
                    block_number = allocated_inodes[j].block_pointers[13]
                    indirect_block_number = int(indirect_pointer_list[i][2])
                    entry = indirect_pointer_list[i][1]
                    if block_number == 0 or block_number >= superblock.block_count:
                        INVALID_BLOCK_POINTER(block_number, j, entry, indirect_block_number)
                    else:
                        register_block(block_number, j, indirect_block_entry, i)

            elif i == 14 and block_number > 267 + 256*256:
                if allocated_inodes[j].block_pointers[14] == indirect_pointer_list[i][0]:
                    block_number = allocated_inodes[j].block_pointers[i]
                    indirect_block_number = int(indirect_pointer_list[i][2])
                    entry = indirect_pointer_list[i][1]
                    if block_number == 0 or block_number >= superblock.block_count:
                        INVALID_BLOCK_POINTER(block_number, j, entry, indirect_block_number)
                    else:
                        register_block(block_number, j, indirect_block_entry, i)

def check_indirect_pointers():
    for i in indirect_dict:
        line = i.rstrip().split(',')
        block_num = int(line[0])
        indirect_ptr = int(line[0])
        entry_num = int(line[1])
        block_num2 = indirect_dict[i]

        while block_num not in allocated_blocks:
            for j in indirect_dict:
                line2 = j.rstrip().split(',')
                if block_num == indirect_dict[j]:
                    block_num = int(line2[0])
                    if indirect_ptr == int(line[0]):
                        indirect_ptr = block_num

        inode = allocated_blocks[block_num].ref_list[0][1]

        if block_num2 == 0 or block_num2 >= superblock.blocks_count:
            INVALID_BLOCK_POINTER(entry_num, block_num, inode, indirect_block_entry)
        else:
            register_block(block_num2, inode, indirect_block_entry, entry_num)

def check_directory():
    for line in directory_dict:
        direct_line = line.rstrip().split(',')
        pi = int(direct_line[0])
        entry_num = int(direct_line[1])
        ci = directory_dict[line][0]
        entry_name = directory_dict[line][1]

        if entry_num == 0 and pi != ci:
            INCORRECT_ENTRY_ERROR(pi, entry_name, ci, pi)
        if entry_num == 1 and ci != direct_c_p[pi]:
            INCORRECT_ENTRY_ERROR(pi, entry_name, ci, direct_c_p[pi])

        if ci in allocated_inodes:
            allocated_inodes[ci].ref_list.append([pi, entry_num])

def check_inodes():
    for i in allocated_inodes:
        links = int(len(allocated_inodes[i].ref_list) / 2 )
        correct_links = int(allocated_inodes[i].link_count)
        if i > 10 and links == 0:
            group = int((i - 1) / superblock.inodes_per_group)
            MISSING_INODE_ERROR(i, inode_bitmap[group])
        elif links != correct_links:
            INCORRECT_LINK_COUNT(i, correct_links, links)

    for i in range(11, superblock.inodes_count):
        if i not in free_inode_list and i not in allocated_inodes:
            group = int((i - 1) / superblock.inodes_per_group)
            MISSING_INODE_ERROR(i, inode_bitmap[group])

def check_unallocated_blocks():
    for block in allocated_blocks:
        if block in free_block_list:
            UNALLOCATED_BLOCK_ERROR(allocated_blocks[block])

def check_duplicately():
    for block in allocated_blocks:
        if len(allocated_blocks[block].ref_list) > 1:
            MULTIPLY_REFERENCED(allocated_blocks[block])

def main():
    
    # load inode.csv
    with open('inode.csv', 'r') as csvfile:
        for line in csvfile:
            inode_line = line.rstrip().split(',')
            inode_number = int(inode_line[0])
            block_count = inode_line[10]
            link_count = int(inode_line[5])
            block_pointers = []
            for i in range(11,26):
                block_pointers.append(int(inode_line[i],16))


            allocated_inodes[inode_number] = inode(inode_number, block_count, block_pointers, link_count)

    # load super.csv
    with open('super.csv', 'r') as csvfile:
        for line in csvfile:
            super_line = line.rstrip().split(',')
            inodes_count = int(super_line[1])
            blocks_count = int(super_line[2])
            block_size = int(super_line[3])
            blocks_per_group = int(super_line[5])
            inodes_per_group = int(super_line[6])
            
            global superblock
            superblock = super_block(inodes_count, blocks_count, block_size, blocks_per_group, inodes_per_group)

    # load bitmap.csv
    with open('bitmap.csv', 'r') as csvfile:
        for line in csvfile:
            bitmap_line = line.rstrip().split(',')
            if int(bitmap_line[0], 16) % 2 == 1:
                free_block_list.append(int(bitmap_line[1]))
            else:
                free_inode_list.append(int(bitmap_line[1]))

    # load indirect.csv
    with open('indirect.csv', 'r') as csvfile:
        for line in csvfile:
            indirect_line = line.rstrip().split(',')
            indirect_pointer_list.append([indirect_line[0],indirect_line[1],indirect_line[2]])
            indirect_dict['%s,%s' % (int(line[0], 16), int(line[1], 16))] = int(line[2],16)

    # load directory.csv
    with open('directory.csv', 'r') as csvfile:
        for line in csvfile:
            directory_line = line.rstrip().split(',')
            parent_inode = int(directory_line[0])
            entry_num = int(directory_line[1])
            child_inode = int(directory_line[4])
            entry_name = directory_line[5]
            directory_dict['%s,%s' % (parent_inode, entry_num)] = [child_inode, entry_name]

            if parent_inode == 2 or (entry_num > 1 and parent_inode != child_inode):
                direct_c_p[child_inode] = parent_inode
            
            if child_inode in allocated_inodes:
                allocated_inodes[child_inode].ref_list.append([parent_inode, entry_num])
            else:
                UNALLOCATED_INODE_ERROR(parent_inode, entry_num, child_inode)

    # load group.csv
    with open('group.csv', 'r') as csvfile:
        for line in csvfile:
            group_line = line.rstrip().split(',')
            inode_bitmap.append(int(group_line[4], 16))
            block_bitmap.append(int(group_line[5], 16))


    check_block_pointers()

#check_indirect_pointers()

    check_directory()

    check_inodes()

    check_duplicately()

    check_unallocated_blocks()

if __name__ == '__main__':
    main()







