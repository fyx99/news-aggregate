
import diff_match_patch as dmp_module

def diff_ratio(a, b):
    dmp = dmp_module.diff_match_patch()
    diff = dmp.diff_main(a, b)
    matches = [w for c, w in diff if c == 0]
    la = len(a)
    lb = len(b)
    t = la + lb
    if t == 0:
        return 0.0
    m = sum([len(w) for w in matches])
    
    idx_a = 0
    idx_b = 0
    start_a = 0
    start_b = 0
    matches_indexes = []
    for i, w in diff:
        w_len = len(w)
        if i == 0:
            matches_indexes.append((start_a, start_b, w_len, w))
            idx_a += w_len
            idx_b += w_len
        elif i == -1:
            idx_a += w_len
        elif i == 1:
            idx_b += w_len
        start_a = idx_a
        start_b = idx_b
    

    d = sum([l for a,b,l,w in matches_indexes if a==b or (la - a + l) == (lb - b + l)])
    
    
    return  0.33333333334*(2.0*m / t) + 0.66666666666*((2.0*d / t)**(1/7))


if __name__ == "__main__":
    print(diff_ratio("", ""))