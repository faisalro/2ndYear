"""
Code for compressing and decompressing using Huffman compression.
"""

from nodes import HuffmanNode, ReadNode


# ====================
# Helper functions for manipulating bytes

def helper_generate_tree(node_lst):
    """A helper functions to generate a tree"""
    huffman_lst = []

    for element in list(node_lst):      #changing list to huffman nodes
        if element.l_type == 0 and element.r_type == 0:     # both leaves
            left = HuffmanNode(element.l_data)
            right = HuffmanNode(element.r_data)
            
        elif (element.l_type == 0 and element.r_type == 1): # left leaf
            left = HuffmanNode(element.l_data)
            right = HuffmanNode()
            right.number = element.r_data
            
        elif (element.l_type == 1 and element.r_type == 0): # right leaf
            left = HuffmanNode()
            left.number = element.l_data
            right = HuffmanNode(element.r_data)
            
        else:                                               # no leaves
            left = HuffmanNode()
            left.number = element.l_data
            right = HuffmanNode()
            right.number = element.r_data
            
        node = HuffmanNode(None, left, right)
        huffman_lst.append(node)
    return huffman_lst

def invert_dict(dict_):
    """inverts the dictionary"""
    new_dict = {}
    for key in dict_:
        value = dict_[key]
        new_dict[value] = key
    return new_dict

def deduct_freq(tree):
    """Trim the freq counters off, leaving just the node value

    @param HuffmanNode: A Huffman Tree
    @rtype: a trimmed huffman Tree with only leaf nodes
    """
    node = tree[1]
    if type(node) == HuffmanNode:
        return node
    else: 
        return HuffmanNode(None, deduct_freq(node[0]), deduct_freq(node[1]))


def sort_freq(freq_dict):
    """ Return a list of tuples sorted by the most frequent occurences

    @param freq_dict: dictionary object of int keys and int values
    @rtype: list of tuples of int frequency and int byte [(int, int)]

    """
    byte_list = list(freq_dict.keys())
    tuples = []
    for byte in byte_list:
        tuples.append((freq_dict[byte], HuffmanNode(byte, None, None)))
    tuples.sort()
    return tuples
      
def get_bit(byte, bit_num):
    """ Return bit number bit_num from right in byte.

    @param int byte: a given byte
    @param int bit_num: a specific bit number within the byte
    @rtype: int

    >>> get_bit(0b00000101, 2)
    1
    >>> get_bit(0b00000101, 1)
    0
    """
    return (byte & (1 << bit_num)) >> bit_num


def byte_to_bits(byte):
    """ Return the representation of a byte as a string of bits.

    @param int byte: a given byte
    @rtype: str

    >>> byte_to_bits(14)
    '00001110'
    """
    return "".join([str(get_bit(byte, bit_num))
                    for bit_num in range(7, -1, -1)])


def bits_to_byte(bits):
    """ Return int represented by bits, padded on right.

    @param str bits: a string representation of some bits
    @rtype: int

    >>> bits_to_byte("00000101")
    5
    >>> bits_to_byte("101") == 0b10100000
    True
    """
    return sum([int(bits[pos]) << (7 - pos)
                for pos in range(len(bits))])


# ====================
# Functions for compression


def make_freq_dict(text):
    """ Return a dictionary that maps each byte in text to its frequency.

    @param bytes text: a bytes object
    @rtype: dict{int,int}

    >>> d = make_freq_dict(bytes([65, 66, 67, 66]))
    >>> d == {65: 1, 66: 2, 67: 1}
    True
    """
    freq_dict = {}
    for element in list(text):
        freq_dict[element] = freq_dict.setdefault(element, 0) +1
    return freq_dict


def huffman_tree(freq_tup):
    """Return the root HuffmanNode of a Huffman tree corresponding
    to frequency dictionary freq_dict.

    @param dict(int,int) freq_dict: a frequency dictionary
    @rtype: HuffmanNode

    >>> freq = {2: 6, 3: 4}
    >>> t = huffman_tree(freq)
    >>> result1 = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> result2 = HuffmanNode(None, HuffmanNode(2), HuffmanNode(3))
    >>> t == result1 or t == result2
    True
    """
    sorted_tup = sort_freq(freq_tup)
    def internal(sorted_tup):
        """Returns a Huffman Tree
        @param list of tuples: a list of sorted tuples
        @rtype: a Huffman Tree
        """
        if len(freq_tup) == 1:
            return sorted_tup[0][1]
        if sorted_tup == []:
            return None
        if len(sorted_tup) == 1:
            i = deduct_freq(sorted_tup[0])
            return HuffmanNode(None, i.left, i.right)
        sorted_tup.sort(key=lambda tup: tup[0])
        least_freq = tuple(sorted_tup[0:2])
        remainder = sorted_tup[2:]
        comb_freq = least_freq[0][0] + least_freq[1][0] 
        sorted_tup = remainder + [(comb_freq, least_freq)]
        return internal(sorted_tup)
    t = internal(sorted_tup)
    return t
    
def get_codes(tree):
    """ Return a dict mapping symbols from tree rooted at HuffmanNode to codes.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: dict(int,str)

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> d = get_codes(tree)
    >>> d == {3: "0", 2: "1"}
    True
    """
    d = {}
    lft = '0'
    rite = '1'
    def internal(tree, byte):
        """Returns a tree after traversing it"""
        if not tree:
            return tree
        if tree.symbol or tree.symbol == 0:
            d[tree.symbol] = byte
        return (internal(tree.left, byte+lft), internal(tree.right, byte+rite))
    internal(tree, '')
    return d

def number_nodes(tree):
    """ Number internal nodes in tree according to postorder traversal;
    start numbering at 0.

    @param HuffmanNode tree:  a Huffman tree rooted at node 'tree'
    @rtype: NoneType

    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(None, HuffmanNode(9), HuffmanNode(10))
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> tree.left.number
    0
    >>> tree.right.number
    1
    >>> tree.number
    2
    """
    l = []
    n = 0
    def internal(tree, n, op):
        """Returns a tree after traversing it"""
        if not tree.left and not tree.right:
            return n
        else:
            l.append(n)
            tree.number = n
            return internal(tree.left, internal(tree.right, n+op, op), op)
    if (tree.left or tree.left == 0) and (tree.right or tree.right == 0):
        internal(tree, n, 1)
        internal(tree, l[-1], -1)

def avg_length(tree, freq_dict):
    """ Return the number of bits per symbol required to compress text
    made of the symbols and frequencies in freq_dict, using the Huffman tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: float

    >>> freq = {3: 2, 2: 7, 9: 1}
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(9)
    >>> tree = HuffmanNode(None, left, right)
    >>> avg_length(tree, freq)
    1.9
    """
    if not tree:
        return 0
    codes = get_codes(tree)
    sums = s = 0
    for (key, value) in codes.items():
        sums += len(value)*freq_dict[key]
        s += freq_dict[key]
    return round(sums/s, 2)


def generate_compressed(text, codes):
    """ Return compressed form of text, using mapping in codes for each symbol.

    @param bytes text: a bytes object
    @param dict(int,str) codes: mappings from symbols to codes
    @rtype: bytes

    >>> d = {0: "0", 1: "10", 2: "11"}
    >>> text = bytes([1, 2, 1, 0])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111000']
    >>> text = bytes([1, 2, 1, 0, 2])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111001', '10000000']
    """

    stop = 0
    comp_list = []
    ret_list = []
    comp_text = ''
    for i in list(text):
        comp_text += codes[i]
    comp_len = len(comp_text)
    end_point = comp_len - comp_len%8
    for initial in range(0, end_point, 8):
        stop = initial + 8
        comp_list.append(comp_text[initial:stop])
    if comp_text[stop:] != '':
        comp_list.append(comp_text[stop:])
    if len(comp_list[-1]) % 8 != 0:
        for i in range(0, 8-len(comp_list[-1])):
            comp_list[-1] += '0'
    for bits in comp_list:
        ret_list.append(bits_to_byte(bits))
    return bytes(ret_list)


def tree_to_bytes(tree):
    """ Return a bytes representation of the tree rooted at tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes

    The representation should be based on the postorder traversal of tree
    internal nodes, starting from 0.
    Precondition: tree has its nodes numbered.

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2]
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(5)
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2, 1, 0, 0, 5]
    """
    leaf_lst = []
    recurse = []
        
    def internal(tree):
        """Makes a list bytes representation while traversing"""

        def leaf(tree):
            '''Appends a leaf repr in the list'''
            leaf_lst.append(0)
            leaf_lst.append(tree.symbol)

        if tree.is_leaf():
            leaf(tree)
            
        elif tree.left.is_leaf() and tree.right.is_leaf(): 
            leaf(tree.left)
            leaf(tree.right)

        elif tree.left.is_leaf() and not tree.right.is_leaf():
            
            internal(tree.right) # at least 4 bits
            leaf(tree.left) # 2 bits
            leaf_lst.append(1) 
            leaf_lst.append(tree.right.number) 
            
        elif not tree.left.is_leaf() and tree.right.is_leaf():
            internal(tree.left) 
            leaf_lst.append(1) 
            leaf_lst.append(tree.left.number) 
            leaf(tree.right)

        elif not tree.left.is_leaf() and not tree.right.is_leaf(): 
            recurse.extend([[1, tree.left.number, 1, tree.right.number]])
            internal(tree.left)
            internal(tree.right)
            leaf_lst.extend(recurse[-1]) 
            recurse.pop()

    if tree:
        internal(tree)

    return bytes(leaf_lst)


def num_nodes_to_bytes(tree):
    """ Return number of nodes required to represent tree (the root of a
    numbered Huffman tree).

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes
    """

    return bytes([tree.number + 1])


def size_to_bytes(size):
    """ Return the size as a bytes object.

    @param int size: a 32-bit integer that we want to convert to bytes
    @rtype: bytes

    >>> list(size_to_bytes(300))
    [44, 1, 0, 0]
    """
    # little-endian representation of 32-bit (4-byte)
    # int size
    return size.to_bytes(4, "little")


def compress(in_file, out_file):
    """ Compress contents of in_file and store results in out_file.

    @param str in_file: input file whose contents we want to compress
    @param str out_file: output file, where we store our compressed result
    @rtype: NoneType
    """
    with open(in_file, "rb") as f1:
        text = f1.read()
    freq = make_freq_dict(text)
    tree = huffman_tree(freq)
    codes = get_codes(tree)
    number_nodes(tree)
    print("Bits per symbol:", avg_length(tree, freq))
    result = (num_nodes_to_bytes(tree) + tree_to_bytes(tree) +\
              size_to_bytes(len(text)))
    result += generate_compressed(text, codes)
    with open(out_file, "wb") as f2:
        f2.write(result)


# ====================
# Functions for decompression


def generate_tree_general(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].

    The function assumes nothing about the order of the nodes in the list.

    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in the node list
    @rtype: HuffmanNode

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12),\
    ReadNode(1, 1, 1, 0)]
    >>> k = HuffmanNode(None, HuffmanNode(None, HuffmanNode(10, None, None), \
    HuffmanNode(12, None, None)), HuffmanNode(None, \
    HuffmanNode(5, None, None), HuffmanNode(7, None, None)))
    >>> generate_tree_general(lst, 2) == k
    True
    
    """
    huffman_lst = helper_generate_tree(node_lst)
    def duplicate_node(node):
        """takes huffman nodes, and makes it into a single node
        @param HuffmanNode node: a HuffmanNode node
        rtype: a HuffmanNode with its left and right duplicates of itself
        """
        return HuffmanNode(None, node.left, node.right)
    tree = duplicate_node(huffman_lst[root_index])
    def create_tree(tree):

        """Creates the HuffmanTree in general order
        @param HuffmanNode tree: a HuffmanNode tree
        rtype: an implemented Huffman tree
        """
        if tree.symbol or tree.symbol == 0: 
            return tree
        
        if tree.left.symbol is None: #left subtree is not a leaf
            tree.left = duplicate_node(huffman_lst[tree.left.number])

        if tree.right.symbol is None: #right subtree is not a leaf
            tree.right = duplicate_node(huffman_lst[tree.right.number])
        
        create_tree(tree.right)               
        create_tree(tree.left)
        
        return tree
    return create_tree(tree)


def generate_tree_postorder(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].

    The function assumes that the list represents a tree in postorder.

    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in the node list
    @rtype: HuffmanNode

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 0, 1, 0)]
    >>> k = HuffmanNode(None, HuffmanNode(None, HuffmanNode(5, None, None), \
    HuffmanNode(7, None, None)), HuffmanNode(None, HuffmanNode(10, None, None),\
    HuffmanNode(12, None, None)))
    >>> generate_tree_postorder(lst, 2) == k
    True
    """
    huffman_lst = helper_generate_tree(node_lst)
    tree = huffman_lst.pop(root_index)
    def traversal(tree):
        """Traverses through the list"""
        if not tree:
            return tree
        if huffman_lst != []:
            if not tree.left.symbol:
                tree.left = huffman_lst.pop(0)
                if huffman_lst != []:
                    if not tree.left.left.symbol or\
                       not tree.left.right.symbol:
                            traversal(tree.left)              
            if not tree.right.symbol:
                tree.right = huffman_lst.pop(0)
                if huffman_lst != []:
                    if not tree.right.left.symbol or \
                       not tree.right.right.symbol:
                        traversal(tree.right)
        return tree
    return traversal(tree)

def generate_uncompressed(tree, text, size):
    """ Use Huffman tree to decompress size bytes from text.

    @param HuffmanNode tree: a HuffmanNode tree rooted at 'tree'
    @param bytes text: text to decompress
    @param int size: how many bytes to decompress from text.
    @rtype: bytes
    """
    one_bit = new_bit = ''
    codes = invert_dict(get_codes(tree)) # maps codes to values : {101: 'a'}
    lst_byte = []
    text = list(text)
    for byte in text:
        one_bit += byte_to_bits(byte)
    for i in range(len(one_bit)): #0, 1, 2, 3
        new_bit += one_bit[i] # adding code from big boy to comparision string
        if new_bit in list(codes.keys()):
            lst_byte.append(codes[new_bit])
            new_bit = ''
            if len(lst_byte) == size:
                return bytes(lst_byte)
    return bytes(lst_byte)

def bytes_to_nodes(buf):
    """ Return a list of ReadNodes corresponding to the bytes in buf.

    @param bytes buf: a bytes object
    @rtype: list[ReadNode]

    >>> bytes_to_nodes(bytes([0, 1, 0, 2]))
    [ReadNode(0, 1, 0, 2)]
    """
    lst = []
    for i in range(0, len(buf), 4):
        l_type = buf[i]
        l_data = buf[i+1]
        r_type = buf[i+2]
        r_data = buf[i+3]
        lst.append(ReadNode(l_type, l_data, r_type, r_data))
    return lst


def bytes_to_size(buf):
    """ Return the size corresponding to the
    given 4-byte little-endian representation.

    @param bytes buf: a bytes object
    @rtype: int

    >>> bytes_to_size(bytes([44, 1, 0, 0]))
    300
    """
    return int.from_bytes(buf, "little")


def uncompress(in_file, out_file):
    """ Uncompress contents of in_file and store results in out_file.

    @param str in_file: input file to uncompress
    @param str out_file: output file that will hold the uncompressed results
    @rtype: NoneType
    """
    with open(in_file, "rb") as f:
        num_nodes = f.read(1)[0]
        buf = f.read(num_nodes * 4)
        node_lst = bytes_to_nodes(buf)
        tree = generate_tree_general(node_lst, num_nodes - 1)
        size = bytes_to_size(f.read(4))
        with open(out_file, "wb") as g:
            text = f.read()
            g.write(generate_uncompressed(tree, text, size))


# ====================
# Other functions

def improve_tree(tree, freq_dict):
    """ Improve the tree as much as possible, without changing its shape,
    by swapping nodes. The improvements are with respect to freq_dict.

    @param HuffmanNode tree: Huffman tree rooted at 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: NoneType

    >>> left = HuffmanNode(None, HuffmanNode(99), HuffmanNode(100))
    >>> right = HuffmanNode(None, HuffmanNode(101), \
    HuffmanNode(None, HuffmanNode(97), HuffmanNode(98)))
    >>> tree = HuffmanNode(None, left, right)
    >>> freq = {97: 26, 98: 23, 99: 20, 100: 16, 101: 15}
    >>> improve_tree(tree, freq)
    >>> avg_length(tree, freq)
    2.31
    """
    
    l = []
    il = []

    byte = list(tree_to_bytes(tree))
    for (key, value) in freq_dict.items():
        l.append((value, key))
    l.sort(reverse=True)
    for i in l:
        if i[1] in byte:
            il.append(byte.index(i[1]))
    il.sort()
    for index in range(len(il)):
        byte[il[index]] = l[index][1]
    n = bytes_to_nodes(byte)
    new_tree = generate_tree_postorder(n, len(n)-1)
    t = (avg_length(tree, freq_dict), avg_length(new_tree, freq_dict))
    # have to replace the old tree to new tree
    tree.left = new_tree.left
    tree.right = new_tree.right


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config="huffman_pyta.txt")
    # TODO: Uncomment these when you have implemented all the functions
    import doctest
    doctest.testmod()

    import time

    mode = input("Press c to compress or u to uncompress: ")
    if mode == "c":
        fname = input("File to compress: ")
        start = time.time()
        compress(fname, fname + ".huf")
        print("compressed {} in {} seconds."
              .format(fname, time.time() - start))
    elif mode == "u":
        fname = input("File to uncompress: ")
        start = time.time()
        uncompress(fname, fname + ".orig")
        print("uncompressed {} in {} seconds."
              .format(fname, time.time() - start))
