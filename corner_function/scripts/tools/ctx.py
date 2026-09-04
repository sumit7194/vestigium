import sys,re
f=sys.argv[1]; pat=re.compile(sys.argv[2]); c=int(sys.argv[3]) if len(sys.argv)>3 else 1; mx=int(sys.argv[4]) if len(sys.argv)>4 else 40
L=open(f).read().split('\n'); n=0; last=-10
for i,l in enumerate(L):
    if pat.search(l):
        n+=1
        if n>mx: print("...more"); break
        lo,hi=max(0,i-c),min(len(L),i+c+1)
        if lo>last+1: print("----")
        for j in range(max(lo,last+1),hi): print(f"{j}: {L[j][:600]}")
        last=hi-1
