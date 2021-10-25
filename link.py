va_high_index3 = poc_index3
va_low_index3  = poc_index3

va_vol_cap3 = sum_vol3 * va_percent
sum_va_vol3 = array.get(a3, poc_index3)

for i = 1 to a_size3 - 1

    above3 = 0.0
    if va_high_index3 + 1 < a_size3 - 1
        above3 := above3 + nz(array.get(a3, (va_high_index3 + 1)), 0.0)
    if va_high_index3 + 2 < a_size3 - 1
        above3 := above3 + nz(array.get(a3, (va_high_index3 + 2)), 0.0)

    below3 = 0.0
    if va_low_index3 - 1 > 0
        below3 := below3 + nz(array.get(a3, (va_low_index3 - 1)), 0.0)
    if va_low_index3 - 2 > 0
        below3 := below3 + nz(array.get(a3, (va_low_index3 - 2)), 0.0)

    if above3 > below3
        va_high_index3 := min(va_high_index3 + 2, a_size3 - 1)
        sum_va_vol3  := sum_va_vol3 + above3
    else
        va_low_index3 := max(va_low_index3 - 2, 0)
        sum_va_vol3 := sum_va_vol3 + below3

    if sum_va_vol3 >= va_vol_cap3 or (va_low_index3 <= 0 and va_high_index3 >= a_size3 - 1)
        break

// }

float p_poc3 = 0.0
float p_va_h3 = 0.0
float p_va_l3 = 0.0

float d_poc3 = 0.0
float b_poc3 = 0.0

float d_va_h3 = 0.0
float d_va_l3 = 0.0

d_poc3  := poc_index3 * tick_size + a_min3
d_va_h3 := va_high_index3 * tick_size + a_min3
d_va_l3 := va_low_index3  * tick_size + a_min3


if is_new_bar3('D')
    p_poc3  := d_poc3[1]
    p_va_h3 := d_va_h3[1]
    p_va_l3 := d_va_l3[1]
    b_poc3  := p_poc3[1]
else
    p_poc3 := p_poc3[1]
    p_va_h3 := p_va_h3[1]
    p_va_l3 := p_va_l3[1]
    b_poc3  := b_poc3[1]



start3 = timenow-80000000


var monh = 0.0
var monl = 0.0

pm = input(true, 'pMonth', input.bool)

if change(p_va_h3) and time > start3 and time < end
    actionMVAH = line.new(x1=time-100000000, y1=p_va_h3, x2=time, y2=p_va_h3, xloc=xloc.bar_time, extend=extend.right, color=pd ? color.rgb(102, 205, 170) : na, width=2)
    actioMVAL = line.new(x1=time-100000000, y1=p_va_l3, x2=time, y2=p_va_l3, xloc=xloc.bar_time, extend=extend.right, color=pd ? color.rgb(102, 205, 170) : na, width=2)
    actionMPOC = line.new(x1=time-100000000, y1=p_poc3, x2=timenow+300000000, y2=p_poc3, xloc=xloc.bar_time, extend=extend.none, color=pd ? color.new(color.white, 70) : na, width=2)
    actionMPOCa = line.new(x1=time-100000000, y1=p_poc3, x2=time, y2=p_poc3, xloc=xloc.bar_time, extend=extend.right, style=line.style_dotted, color=pd ? color.rgb(102, 205, 170) : na, width=2)
    monh := p_va_h3
    monl := p_va_l3

mh = plot(monh, color = na, offset = 0)
ml = plot(monl, color = na, offset = 0)

fill(mh, ml, color=pm ? color.new(color.rgb(102, 205, 170), 80) : na)
