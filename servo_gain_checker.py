def pval(fb_coeff, shifts) :

    pi = 3.142

    # unit convert
    fb_coeff_f = fb_coeff*(800-343)/3.8*pi/4096.0 * 2**shifts
    # round-off
    fb_coeff_i = int(fb_coeff_f)
    # error percentage
    err = (fb_coeff_i-fb_coeff_f)/fb_coeff_f*100
    # max input
    max_fb_val = 2**15 / fb_coeff_i

    print(fb_coeff_i)
    print(err)
    print(max_fb_val)

    return (fb_coeff_i,err,max_fb_val)


pval(13, 2)
#pval(4, 0)