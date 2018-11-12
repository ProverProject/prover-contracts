#! /usr/bin/env python3

import sys, binascii, bisect


def choice(m, n, bignum):
    assert m<=n+1
    n+=1

    r=[]
    for i in range(m):
        bignum,residue=divmod(bignum, n-i)
        for j in range(i):
            if residue>=r[j]:
                residue+=1
        # it's just an insert into sorted list keeping the list sorted
        bisect.insort(r, residue)

    return r

if __name__=="__main__":
    if len(sys.argv)<4:
        sys.exit("Usage: {0} M N HASH\nIt deterministically produces M distinct numbers from [0;N] using HASH as seed\n".format(sys.argv[0]))

    m=int(sys.argv[1])
    n=int(sys.argv[2])
    h=int("0x"+sys.argv[3], 16)

    print(choice(m, n, h))
