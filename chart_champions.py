// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// Thanks go to
//ahancock for allow usage of his script
//AnyDozer and Bjorn Mistiaen on Stack Overflow for all their assistance


//@version=4
study(title="Trading Ideas - CCV - POI", shorttitle="TI - CCV - POI", overlay=true)

//Session Rules
bartimeSess = time('D')
newbarSess = bartimeSess != bartimeSess[1]
offset_val = input(title="Label Offset", type=input.integer, defval=6)
high_range = valuewhen(newbarSess,high,0)
low_range = valuewhen(newbarSess,low,0)

//Daily Open
dOpen = security(syminfo.tickerid, "D", open, lookahead = barmerge.lookahead_on)
plot(dOpen, " dOpen", change(dOpen) ? na : color.blue, offset = 0)
plotshape(dOpen, style=shape.labeldown, location=location.absolute, color=color.blue,  textcolor=color.white, show_last=1, text="dOpen",  offset = offset_val, transp=20, title="dOpen")

//Calcul For Opening Range
locHigh = security(syminfo.tickerid, "60", high_range)
locLow = security(syminfo.tickerid, "60", low_range)
range = locHigh - locLow


plot(locHigh, "IB High", change(locHigh) ? na : color.white, offset = 0)
plotshape(locHigh, style=shape.labeldown, location=location.absolute, color=color.white,  textcolor=color.black, show_last=1, text="IB High",  offset = offset_val, transp=20, title="IB High")


plot(locLow, "IB Low", change(locLow) ? na : color.white, offset = 0)
plotshape(locLow, style=shape.labeldown, location=location.absolute, color=color.white,  textcolor=color.black, show_last=1, text="IB Low",  offset = offset_val, transp=20, title="IB Low")


locMid = locLow + range/2
plot(locMid, "IB Mid", change(locMid) ? na : color.orange, offset = 0)
plotshape(locMid, style=shape.labeldown, location=location.absolute, color=color.orange,  textcolor=color.white, show_last=1, text="IB Mid",  offset = offset_val, transp=20, title="IB Mid")

//USer configurations
va_percent = input(0.7, title = "Value Area (Igor 0.7 / Daniel 0.68)", type = input.float,
     minval = 0.1, maxval = 1, step = 0.1)


show_ccv = input(true, title = "First check if CCV is in play", type = input.bool)

dtf = input("D", title = "Time Frame", type = input.resolution)
resolution = input(1, title = "Resolution (Change resolution to Symbol decimal)", type = input.float)


//CCV color
ccvtxt_color = show_ccv ? color.white : na
ccvdopen_color = show_ccv ? color.blue : na


is_new_bar(t) =>
    change(time(t)) != 0

round_to_nearest(v, x) =>
    round(v / x) * x


tick_size = max(syminfo.mintick, resolution)

var a = array.new_float(0)

a_min = 0.0, a_min := nz(a_min[1], round_to_nearest(low, tick_size))
a_max = 0.0, a_max := nz(a_max[1], round_to_nearest(high, tick_size))

d_switch = is_new_bar(dtf)

if d_switch
    a_min := low
    a_max := high
    array.clear(a)

// Scaled min max
v_min = int(round_to_nearest(low - a_min, tick_size) / tick_size)
v_max = int(round_to_nearest(high - a_min, tick_size) / tick_size)

// Scaled candle range
ticks = v_max - v_min

vol = volume / (ticks == 0 ? 1 : ticks)

for i = v_min to max(v_max - 1, v_min)

    // Insert new low value
    if i < 0
        array.insert(a, i - v_min, vol)
        continue

    // Adjust index
    offset = v_min < 0 ? abs(v_min) : 0
    index = int(i + offset)

    // Push new high value
    if index >= array.size(a)
        array.push(a, vol)
        continue

    // Update existing value
    v = array.get(a, index)
    array.set(a, index, v + vol)

// Array bounds
a_min := min(a_min, round_to_nearest(low, tick_size))
a_max := max(a_max, round_to_nearest(high, tick_size))
a_size = array.size(a)

// { POC

poc_index = -1
poc_prev = -1.0
sum_vol = 0.0

for i = 0 to a_size - 1

    poc_current = array.get(a, i)
    sum_vol := sum_vol + poc_current

    if poc_current > poc_prev
        poc_prev := poc_current
        poc_index := i

// }

// { VA

va_high_index = poc_index
va_low_index  = poc_index

va_vol_cap = sum_vol * va_percent
sum_va_vol = array.get(a, poc_index)

for i = 1 to a_size - 1

    above = 0.0
    if va_high_index + 1 < a_size - 1
        above := above + nz(array.get(a, (va_high_index + 1)), 0.0)
    if va_high_index + 2 < a_size - 1
        above := above + nz(array.get(a, (va_high_index + 2)), 0.0)

    below = 0.0
    if va_low_index - 1 > 0
        below := below + nz(array.get(a, (va_low_index - 1)), 0.0)
    if va_low_index - 2 > 0
        below := below + nz(array.get(a, (va_low_index - 2)), 0.0)

    if above > below
        va_high_index := min(va_high_index + 2, a_size - 1)
        sum_va_vol  := sum_va_vol + above
    else
        va_low_index := max(va_low_index - 2, 0)
        sum_va_vol := sum_va_vol + below

    if sum_va_vol >= va_vol_cap or (va_low_index <= 0 and va_high_index >= a_size - 1)
        break

// }

float p_poc = 0.0
float p_va_h = 0.0
float p_va_l = 0.0

float d_poc = 0.0
float b_poc = 0.0

float d_va_h = 0.0
float d_va_l = 0.0

d_poc  := poc_index * tick_size + a_min
d_va_h := va_high_index * tick_size + a_min
d_va_l := va_low_index  * tick_size + a_min



if is_new_bar(dtf)
    p_poc  := d_poc[1]
    p_va_h := d_va_h[1]
    p_va_l := d_va_l[1]
    b_poc  := p_poc[1]
else
    p_poc  := p_poc[1]
    p_va_h := p_va_h[1]
    p_va_l := p_va_l[1]
    b_poc  := b_poc[1]


plot(d_poc, color = color.red, title = "dPOC")
plotshape(d_poc, style=shape.labeldown, location=location.absolute, color=color.red,  textcolor=color.white, show_last=1, text="dPOC",  offset = offset_val, transp=20, title="dPOC")

plot(b_poc, "dby_POC", change(b_poc) ? na : color.yellow, offset = 0)
plotshape(b_poc, style=shape.labeldown, location=location.absolute, color=color.yellow,  textcolor=color.white, show_last=1, text="dbyPOC",  offset = offset_val, transp=20, title="dbyPOC")


ccv_color =  show_ccv ?
     dOpen > p_va_h ? color.green :
     dOpen < p_va_l ? color.green :
     color.red :
     na


plot(p_poc, " pd_POC", change(p_poc) ? na : color.purple, offset = 0)
plotshape(p_poc, style=shape.labeldown, location=location.absolute, color=color.purple,  textcolor=color.white, show_last=1, text="pdPOC",  offset = offset_val, transp=20, title="pdPOC")




ccvplot_p_va_h = plot(p_va_h, " pdVAH", change(p_va_h) ? na : ccv_color, offset = 0)
plotshape(p_va_h, style=shape.labeldown, location=location.absolute, color=ccv_color, textcolor=ccvtxt_color, show_last=1, text="pdVAH",  offset = offset_val, transp=20, title="pdVAH")

ccvplot_p_va_l = plot(p_va_l, " pdVAL", change(p_va_l) ? na : ccv_color, offset = 0)
plotshape(p_va_l, style=shape.labeldown, location=location.absolute, color=ccv_color, textcolor=ccvtxt_color, show_last=1, text="pdVAL",  offset = offset_val, transp=20, title="pdVAL")

fill(ccvplot_p_va_h, ccvplot_p_va_l, ccv_color)


//VWAPs
show_VWAPs = input(false, title = "Show Daily and previous VWAP", type = input.bool)
show_VWAPs_color = show_VWAPs ? color.red : na
show_VWAPs_text = show_VWAPs ? color.white : na

VWAP = vwap
plot(VWAP, "VWAP", color=show_VWAPs_color, offset = 0)
plotshape(VWAP, style=shape.labeldown, location=location.absolute, color=show_VWAPs_color,  textcolor=show_VWAPs_text, show_last=1, text="VWAP",  offset = offset_val, transp=20, title="VWAP")

//Previous Day's Closing Vwap
newday(res) =>
    t = time(res)
    change(t) != 0 ? 1 : 0
new_day = newday("D")
pdVWAP = valuewhen(new_day, int(vwap[1]), 0)
plot(pdVWAP, "pdVWAP", change(pdVWAP) ? na : show_VWAPs_color, offset = 0)
plotshape(pdVWAP, style=shape.labeldown, location=location.absolute, color=show_VWAPs_color,  textcolor=show_VWAPs_text, show_last=1, text="pdVWAP",  offset = offset_val, transp=20, title="pdVWAP")

