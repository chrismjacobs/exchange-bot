//
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// @version = 4
// @author  = The_Caretaker
// © The_Caretaker
//
// Much respect to Alex Orekhov (everget) for sharing the Stochastic Momentum Index script which I based this indicator on.
// Greatly inspired by the original paper from William Blau, the inventor of the Stochastic Momentum Index
// and the prior works of Giorgos Siligardos, Dimitris Tsokakis and Johny Dough in reverse engineering momentum oscillators.
//


// SMi INDICATOR
// TSI INDICATOR
// RSI INDICATOR
// EMA PLOTS
// CANDLE PLOT
// LABELS

study ( "The Mixer", "Mix", false)


/// SMI Indicator ///////////////////////////////////////////////////////////////////////////

// Inputs and global variable declarations

i_srcPrice  = input ( close,    "SMI Price Source",         input.source )
i_SMI_len   = input ( 13,       "SMI Length",               input.integer, minval = 1 )
i_smth1     = input ( 25,       "Smooth Length 1",          input.integer, minval = 1 )
i_smth2     = input ( 2,        "Smooth Length 2",          input.integer, minval = 1 )
i_sigLen    = input ( 12,       "Signal Length",            input.integer, minval = 1 )
i_alrtInfo  = input ( true,     "Show Alert Levels Info",   input.bool )
i_alrtHi    = 40 // input ( 40,       "Upper Alert Level",        input.float,   minval = -100, maxval = 100)
i_midLine   = 0 // input ( 0,        "Midline",                  input.integer, minval = -100, maxval = 100)
i_alrtLo    = -40 // input ( -40,      "Lower Alert Level",        input.float,   minval = -100, maxval = 100)
i_alrtLines = false // input ( false,    "Show Alert Level Lines",   input.bool )
i_infoBox   = true // input ( true,     "Show Info Box",            input.bool )
i_decimalP  = 2 //input ( 2,        "Prices Decimal Places",    input.integer, minval = 0, maxval = 10)
i_boxOffSet = 5 // input ( 5,        "Info Box Offset",          input.integer, minval = 1, maxval = 50)

ScaleHi     =  100
ScaleLo     = -100

var label  Infobox      = na

///////////////////////////////////////////////////////////////////////////////
// Declare Functions

f_truncdNum ( Val, DecPl ) =>
    Fact = pow ( 10, DecPl )
    int( Val * Fact) / Fact

     // decimal truncation

a(x) => 2 / (x + 1)

     // exponentially weighted multiplier

f_reverse_SMI ( P, U, W, X, Y, Z ) =>
    V = 0.5
    H = highest(W)
    L = lowest(W)
    D = ema (( P - V * ( H + L )), X )[1]
    E = ema ((( a(X)* ( P - V * ( H + L )))+( D -D*a(X))), Y )[1]
    F = ema ( H - L , X )[1]
    G = ema ((( a(X)*( H -L ) +  F*( 1 -a(X)))), Y )[1]
    J = 100 * (( a(Y)* ( ( a(X)* ( P - V * ( H + L ))) + ( D - D*a(X)))) + ( E * ( 1 -a(Y)) )) / ( V * (a(Y)*((a(X)*( H -L ) +  F*( 1 -a(X)))) + ( G*( 1 -a(Y)))))[1]
    K = ema ( ( 100 * (( a(Y)* ( ( a(X)* ( P - V * ( H + L ))) + ( D - D*a(X)))) + ( E * ( 1 -a(Y)) )) / ( V * (a(Y)*((a(X)*( H -L ) +  F*( 1 -a(X)))) + ( G*( 1 -a(Y)))))), Z )[1]
    rawReturn = ( V*U*(a(Y)*a(X)*H -a(Y)*a(X)*L -a(Y)*F*a(X) +a(Y)*F -G*a(Y) + G) + 100*(a(Y)*a(X)*V*H +a(Y)*a(X)*V*L -a(Y)*D +a(Y)*D*a(X) +E*a(Y) -E)) / ( 100*a(Y)*a(X))
    return = rawReturn > 0 ? rawReturn : 0

     // see orignal comments

f_reverse_SMI_cross ( P, W, X, Y, Z ) =>
    V = 0.5
    H = highest(W)
    L = lowest(W)
    D = ema (( P - V * ( H + L )), X )[1]
    E = ema (((a(X)* ( P - V * ( H + L )))+( D -D*a(X))), Y )[1]
    F = ema ( H - L , X )[1]
    G = ema (((a(X)*( H -L ) +  F*( 1 -a(X)))), Y )[1]
    J = 100 * (( a(Y)* ( ( a(X)* ( P - V * ( H + L ))) + ( D - D*a(X)))) + ( E * ( 1 -a(Y)) )) / ( V * (a(Y)*((a(X)*( H -L ) +  F*( 1 -a(X)))) + ( G*( 1 -a(Y)))))[1]
    K = ema ( ( 100 * (( a(Y)* ( ( a(X)* ( P - V * ( H + L ))) + ( D - D*a(X)))) + ( E * ( 1 -a(Y)) )) / ( V * (a(Y)*((a(X)*( H -L ) +  F*( 1 -a(X)))) + ( G*( 1 -a(Y)))))), Z )[1]
    rawReturn = ( a(Y)*(100*( a(Z)*(-a(X)*V*H -a(X)*V*L +D -D*a(X) -a(X) -E) +a(X)*V*H +a(X)*V*L -D +D*a(X) +E) +V*K*(a(X)*(-H*a(Z) +H +L*a(Z) -L +F*a(Z) -F) -F*a(Z) +F +G*a(Z) -G)) +100*(a(Z)*E-E) -V*K*G*a(Z) +V*K*G)/(100*a(Y)*a(X)*(-a(Z)+1))
    return = rawReturn > 0 ? rawReturn : 0

     /// see orignal comments

f_delta ( P, X ) => X - P > 0

f_negVal ( X, D ) => X > 0 ? tostring ( f_truncdNum ( X, D )) : "Impossible"

text_eq ( p, x, d ) => p > x ? "Continues Rising Above (eq) : " + tostring(int(x*pow(10,d))/pow(10,d)) : "Continues Falling Below (Eq) :" + tostring(int(x*pow(10,d))/pow(10,d))

f_crossText ( P, X, T, D ) => f_delta ( P, X ) ? "Cross Above " + T + " : " + f_negVal ( X, D ) + "\n" : "Cross Below " + T + " : " + f_negVal ( X, D ) + "\n"

//////////////////////////////////////////////////////////////////////////////
// Calculations

SMINumerator        = ema ( ema ( i_srcPrice - 0.5 * ( highest (i_SMI_len) + lowest (i_SMI_len)), i_smth1 ), i_smth2 )
SMIDenominator      = 0.5 * ema ( ema ( highest (i_SMI_len) - lowest (i_SMI_len), i_smth1 ), i_smth2 )
SMI                 = 100 * SMINumerator / SMIDenominator
SMI_eq              = f_reverse_SMI ( i_srcPrice, SMI[1], i_SMI_len, i_smth1, i_smth2, i_sigLen )
alrtHilineCross     = f_reverse_SMI ( i_srcPrice, i_alrtHi, i_SMI_len, i_smth1, i_smth2, i_sigLen )
zerolineCross       = f_reverse_SMI ( i_srcPrice, 0, i_SMI_len, i_smth1, i_smth2, i_sigLen )
alrtLolineCross     = f_reverse_SMI ( i_srcPrice, i_alrtLo, i_SMI_len, i_smth1, i_smth2, i_sigLen )
signalCross         = f_reverse_SMI_cross ( i_srcPrice, i_SMI_len, i_smth1, i_smth2, i_sigLen )


///////////////////////////////////////////////////////////////////////////////
// Compute Info Label

labelXLoc           = time_close + ( i_boxOffSet * ( time_close - time_close[1] ) )
crossSignalText     = f_crossText ( i_srcPrice, signalCross, "Signal Line", i_decimalP )
SMIeq               = text_eq     ( i_srcPrice, SMI_eq, i_decimalP )
crossZeroText       = f_crossText ( i_srcPrice, zerolineCross, "Zero Line", i_decimalP )
infoBoxText         = "SMI\n\n" + SMIeq + "\n\n" + crossSignalText + "\n" + crossZeroText

///////////////////////////////////////////////////////////////////////////////
// InfoBox Plot

if i_infoBox
    Infobox := label.new ( labelXLoc, close, infoBoxText, xloc.bar_time, yloc.price, #000000ff, label.style_label_left, color.white )

label.delete ( Infobox[1] )


///////////////////////////////////////////////////////////////////////////////

// color and marker for candle logic

var smi_color = color.white
smi_change = false

if SMI_eq < i_srcPrice
    if smi_color != color.green
        smi_change := true
    smi_color := color.green
else
    if smi_color != color.red
        smi_change := true
    smi_color := color.red




// SMI Plots & Fills


p_SMI_eqPlot    = plot ( SMI_eq,  "SMI EQ Price", smi_color, 2, plot.style_linebr, transp = 0)


// SMI end -------------------------------------------------



////// True RSI indicator

///////////////////////////////////////////////////////////////////////////////
// Inputs

i_src           = close // TSI Price Source
i_long_len      = input ( 25,       "TSI Long EMA Length",      input.integer )
i_short_len     = input ( 13,       "TSI Short EMA Length",     input.integer )
i_signal_len    = input ( 7,        "TSI Signal EMA Length",    input.integer )
i_alertLines    = input ( 0.5,        "TSI Alert Lines (dec%)",    input.float )
i_zero_line     = input ( 27000,     "TSI Zero Line",    input.integer )
i_price_range   = input ( 6000,    "TSI Price Range From Zero",    input.integer )
i_dec_places    = 2
i_lbl_offset    = 6
i_lbl_showAlert = true
i_lbl_txt_color = #FFFFFF
i_lbl_col_below = #EF5350  // box changes color
i_lbl_col_above = #26A69A


///////////////////////////////////////////////////////////////////////////////
// Function Declarations

alpha ( len ) =>
    2 / ( len + 1 )

     // Exponential weighted multiplier Function

f_tsi ( P, X, Y ) =>
	ema1 = ema ( P-P[1], X )
	ema2 = ema ( ema1, Y )
	ema3 = ema ( abs(P-P[1]), X )
	ema4 = ema ( ema3, Y )
	return = 100 * ( ema2 / ema4 )

     // True Strength Index Function

f_reverse_tsi ( P, W, X, Y ) =>
    Q = P[1]
    A = alpha ( X )
    B = alpha ( Y )
    G = ema ( P - Q , X )[1]
    H = ema ( G, Y )[1]
    I = ema ( abs( P - Q ), X )[1]
    J = ema ( I, Y )[1]
    positiveReturn = ( -A*B*I*W -A*B*Q*W -B*B*I*W +B*B*J*W +100*A*B*G +100*A*B*Q +100*B*B*G -100*B*B*H +2*B*I*W -2*B*J*W -200*B*G +200*B*H +J*W -100*H )/( -A*B*W +100*A*B )
    negativeReturn = ( -A*B*I*W +A*B*Q*W -B*B*I*W +B*B*J*W +100*A*B*G +100*A*B*Q +100*B*B*G -100*B*B*H +2*B*I*W -2*B*J*W -200*B*G +200*B*H +J*W -100*H )/(  A*B*W +100*A*B )
    rawReturn = positiveReturn > P[1] ? positiveReturn : negativeReturn
    return = rawReturn > 0 ? rawReturn : 0

     // see orignal comments

f_reverse_tsi_signal_cross ( P, X, Y, Z ) =>
    Q = P [1]
    TSI = f_tsi ( P, X, Y )
    TSI_Signal = ema ( TSI, Z )
    A = alpha ( X )
    B = alpha ( Y )
    C = alpha ( Z )
    B2 = B*B
    G = ema ( P-Q, X )[1]
    H = ema ( G, Y )[1]
    I = ema ( abs ( P - Q ), X)[1]
    J = ema ( I, Y )[1]
    K = ema ( TSI, Z )[1]
    Wx = P - P[1] > 0 ? ( C * ( 100 *(( B *( A *( P - Q ) +( 1 - A ) *G ) +( 1 - B ) *( B * G +( 1 - B ) *H )) / (( B *( A*(( P - Q )) +( 1 - A ) *I ) +( 1 - B ) *( B *I +( 1 - B ) * J ))))) +( 1 - C ) * K ):
         ( C* ( 100 *(( B*( A*( P - Q ) +( 1 - A )*G ) +( 1 - B ) *( B * G + ( 1 - B ) * H )) / (( B * ( A * (-( P - Q )) + ( 1 - A ) * I ) + ( 1 - B ) * ( B * I + ( 1 - B ) * J ))))) +( 1 - C ) * K )
    W = Wx[1]
    positiveReturn = (-A*B*C*I*K-A*B*C*K*Q-B2*C*I*K+B2*C*J*K+100*A*B*C*G+100*A*B*C*Q+A*B*I*K-A*B*I*W+A*B*K*Q-A*B*Q*W+100*B2*C*G-100*B2*C*H+B2*I*K-B2*I*W-B2*J*K+B2*J*W+2*B*C*I*K-2*B*C*J*K-200*B*C*G+200*B*C*H-2*B*I*K+2*B*I*W+2*B*J*K-2*B*J*W+C*J*K-100*C*H-J*K+J*W)/(-A*B*C*K+100*A*B*C+A*B*K-A*B*W)
    negativeReturn = (-A*B*C*I*K+A*B*C*K*Q-B2*C*I*K+B2*C*J*K+100*A*B*C*G+100*A*B*C*Q+A*B*I*K-A*B*I*W-A*B*K*Q+A*B*Q*W+100*B2*C*G-100*B2*C*H+B2*I*K-B2*I*W-B2*J*K+B2*J*W+2*B*C*I*K-2*B*C*J*K-200*B*C*G+200*B*C*H-2*B*I*K+2*B*I*W+2*B*J*K-2*B*J*W+C*J*K-100*C*H-J*K+J*W)/( A*B*C*K+100*A*B*C-A*B*K+A*B*W)
    rawReturn = positiveReturn > P[1] ? positiveReturn : negativeReturn
    return = rawReturn > 0 ? rawReturn : 0

     // see orignal comments


f_zeroTest ( X, D ) => X > 0 ? tostring ( f_truncdNum ( X, D )) : "Impossible"

f_text_eq ( p, x, d ) =>
    text = p > x ? "TSI\n\n Continues Rising Above (eq) : " + tostring( f_truncdNum ( x, d )) : "TSI\n\n Continues Falling Below (Eq) :" + tostring( f_truncdNum ( x, d ))

     // TSI (eq) text string function

f_crosstext ( p, t, x, d) =>
    ema_text = p > x ? "Cross Below " + t + " Line : " + f_zeroTest ( x, d ) : "Cross Above " + t + " Line : " + f_zeroTest ( x, d )

     // TSI line cross text string function

f_label_text ( P, A, D, V, W ) =>
    f_text_eq ( P, V, D ) + "\n\n" + f_crosstext ( P, "Signal", W, D ) + "\n\n"

     // TSI infobox text string combination function

///////////////////////////////////////////////////////////////////////////////
// Calculations

TSI                 = f_tsi ( i_src, i_long_len, i_short_len )                      // Get TSI value

TSI_signalLine      = ema ( TSI, i_signal_len )                                     // Get TSI signal line value

TSI_eq             = f_reverse_tsi ( i_src, TSI[1], i_long_len, i_short_len )       // Get TSI eq price1

TSI_signal_cross   = f_reverse_tsi_signal_cross ( i_src, i_long_len, i_short_len, i_signal_len) // Get TSI signal line cross price1

label_X_Loc         = time_close + (( time_close - time_close[1] ) * i_lbl_offset )             // Set Label offset

label_text          = f_label_text ( i_src, i_lbl_showAlert, i_dec_places, TSI_eq, TSI_signal_cross) // Get Label text

///////////////////////////////////////////////////////////////////////////////
// Plots and fills


/// rescale function

f_rescale (plotData, plotMinMax) =>
    // plotMinMaX = 50
    // 50 = 25000
    // -50 = 15000
    // 0 = 20000
    i_zero_line + plotData * ((i_price_range/2)/plotMinMax)

f_alert_rescale (plus_minus) =>
    // 20000 + 2500 <=  10000/2   5000/2
    i_zero_line + (i_price_range/2)  *(i_alertLines * plus_minus)



hline ( f_alert_rescale (1) , "High Alert Line", color.fuchsia, linestyle=hline.style_dotted)
hline ( i_zero_line, "Zero line", color.silver )
hline ( f_alert_rescale (-1) , "Low Alert Line", color.aqua, linestyle=hline.style_dotted )
plot ( f_rescale(TSI, 50), color = color.aqua )
plot ( f_rescale(TSI_signalLine, 50), color = color.yellow )

label = label.new ( label_X_Loc, f_rescale(TSI, 50) , label_text , xloc.bar_time, yloc.price, TSI < TSI[1] ? i_lbl_col_below : i_lbl_col_above, label.style_label_left, i_lbl_txt_color, size=size.small )

label.delete ( label[1] )   // Delete Previous Label

///////////////////////////////////////////////////////////////////////////////

//RSI data


rsiSource = input(title="RSI Source", type=input.source, defval=close)
rsiLength = input(title="RSI Length", type=input.integer, defval=14)
rsiBottom = input(title="RSI Scale Bottom", type=input.float, defval=28000)
rsiTop = input(title="RSI Scale Top", type=input.float, defval=32000)
rsiValue = rsi(rsiSource, rsiLength)

dTrend = false
uTrend = false

if rsiValue <= 50
    dTrend := true
else
    uTrend := true

fraction_dec = (rsiTop - rsiBottom)/10

rsi_factor = (rsiTop - rsiBottom) / 100
// rsi scale adjust  0 = 25000  100 = 3000

plot(rsiValue*rsi_factor + rsiBottom, color=color.aqua)
hline(price= rsiBottom + fraction_dec*7, linestyle=hline.style_dotted)
hline(price= rsiBottom + fraction_dec*5, color=color.white)
hline(price = rsiBottom + fraction_dec*3, linestyle=hline.style_dotted)


//////////////////////////////////////////////////////
//Heikin Ashi candles

tickerid = syminfo.tickerid

period = timeframe.period


ha_t = heikinashi(tickerid)
ha_open = security(ha_t, period, open)
ha_high = security(ha_t, period, high)
ha_low = security(ha_t, period, low)
ha_close = security(ha_t, period, close)

prev_open = security(ha_t, period, open[1])
prev_high = security(ha_t, period, high[1])
prev_low = security(ha_t, period, low[1])
prev_close = security(ha_t, period, close[1])

qi_open = security(ha_t, period, open[2])
qi_high = security(ha_t, period, high[2])
qi_low = security(ha_t, period, low[2])
qi_close = security(ha_t, period, close[2])



wickcolor = color.gray
bodycolor = color.black


var yellowPrint = 0
var purplePrint = 0


if smi_change == true
    yellowPrint := 0
    purplePrint := 0
    smi_change := false


delete_lines = true


// get buy candles
if ha_open == ha_low
    bodycolor := color.gray

    if prev_open == prev_low and yellowPrint == 1
        // don't delete previous line if yellow candle just printed
        yellowPrint := yellowPrint + 1
        delete_lines := false

    if prev_open == prev_low and yellowPrint == 0
        if uTrend == true and ha_close > SMI_eq
            bodycolor := color.yellow
            wickcolor := color.yellow
            yellowPrint := yellowPrint + 1
        if uTrend == false and ha_close > SMI_eq
            bodycolor := color.green

// get sell candles
if ha_open == ha_high
    bodycolor := color.gray

    if prev_open == prev_high and purplePrint == 1
        // don't delete previous line if purple candle just printed
        purplePrint := purplePrint + 1
        delete_lines := false

    if prev_open == prev_high and purplePrint == 0
        if dTrend == true and ha_close < SMI_eq
            bodycolor := color.purple
            wickcolor := color.purple
            purplePrint := purplePrint + 1
        if dTrend == false and ha_close < SMI_eq
            bodycolor := color.red

level1 = color.red
level2 = color.green

if purplePrint == 1
    level1 := color.green
    level2 := color.red

actionLine = line.new(x1=time, y1=close, x2=time + 30000000, y2=close, xloc=xloc.bar_time, extend=extend.none, color=bodycolor, style=line.style_dotted, width=2)
levelLine1 = line.new(x1=time, y1=close*0.97, x2=time + 30000000, y2=close*0.97, xloc=xloc.bar_time, extend=extend.none, color=level1, style=line.style_dotted, width=1)
levelLine2 = line.new(x1=time, y1=close*1.03, x2=time + 30000000, y2=close*1.03, xloc=xloc.bar_time, extend=extend.none, color=level2, style=line.style_dotted, width=1)
actionLabel = label.new(x=bar_index, y=na, text=tostring(close), yloc=yloc.belowbar, color=color.green, textcolor=color.white, style=label.style_label_up, size=size.normal)

if delete_lines
    line.delete(actionLine[1])
    line.delete(levelLine1[1])
    line.delete(levelLine2[1])
    label.delete(actionLabel[1])




// get dojis

bodysize = ha_open - ha_close

if bodysize <= 0
    bodysize :=  bodysize*-1


if bodysize < (ha_high - ha_low)*.1
    bodycolor := color.white
    wickcolor := color.white


plotcandle(ha_open, ha_high, ha_low, ha_close, color=bodycolor, wickcolor=wickcolor)


// label practice
// label.new(x, y, text, xloc, yloc, color, style, textcolor, size, textalign, tooltip) → series[label]

// lastClose = security(syminfo.tickerid, '60', close, barmerge.gaps_off, barmerge.lookahead_off)

labelText = tostring(close)
myLabel = label.new(x=bar_index, y=na, text=labelText, yloc=yloc.belowbar, color=color.green, textcolor=color.white,
 style=label.style_label_up, size=size.normal)

label.delete(myLabel[1])

// line practice
// line.new(x1, y1, x2, y2, xloc, extend, color, style, width) → series[line]

// myLine = line.new(x1=time, y1=close, x2=time + 1000, y2=close + 1000, xloc=xloc.bar_time, extend=extend.none, color=color.red, style=line.style_arrow_left, width=1)
// line.delete(myLine[1])

/// EMA plots

plot(ema(close, 21), style=plot.style_stepline, color=color.teal)


ema34 = ema(close, 34)
ema34_step = security(syminfo.tickerid, 'W', ema34, barmerge.gaps_off, barmerge.lookahead_off)

//plot(ema34_step, style=plot.style_line, color=color.yellow)

ema55 = ema(close, 55)
ema55_step = security(syminfo.tickerid, 'W', ema55, barmerge.gaps_off, barmerge.lookahead_off)

plot(ema34_step, style=plot.style_line, color=color.red)

ema21 = ema(close, 21)
ema21_smooth = security(syminfo.tickerid, 'D', ema21, barmerge.gaps_on, barmerge.lookahead_off)

plot(ema21_smooth, style=plot.style_line, color=color.blue)



var line _lpLine = line.new(0, 0, 0, 0, extend=extend.right, style=line.style_dashed, color=color.aqua)

_lastTradedPrice = close
line.set_xy1(_lpLine, bar_index-1, _lastTradedPrice)
line.set_xy2(_lpLine, bar_index, _lastTradedPrice)



/// Heikin Ashi end --------------------------------------------------------