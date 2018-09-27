from random import shuffle


def split_seq(seq, NUMBER_OF_PROCESSES):
    '''
    Slices a list into NUMBER_OF_PROCESSES pieces
    of roughly the same size
    '''
    shuffle(seq)  # don't want newer/older years going to a single process
    num_files = len(seq)
    if num_files < NUMBER_OF_PROCESSES:
        NUMBER_OF_PROCESSES = num_files
    size = NUMBER_OF_PROCESSES
    newseq = []
    splitsize = 1.0 / size * num_files
    if NUMBER_OF_PROCESSES == 1:
        newseq.append(seq[0:])
        return newseq
    for i in range(size):
        newseq.append(seq[int(round(i * splitsize)):int(round((i + 1) * splitsize))])
    return newseq
