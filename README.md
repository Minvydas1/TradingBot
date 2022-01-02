Kažkodėl neveikia macd, tik stochrsi iš TAAPI. Galbūt dėl to, kad pas mane nemokamas planas parinktas, tikliai nežinau.
Prieš pusę metų veikė, nelabai sugalvoju kas dar gali būti blogai su kodu.
Taip pat tada, kai rašiau šį kodą nesuvokiau, kad neparašiau:
if if_candle_closed == "True":
ir t.t.
Dabar bijojau labai prisiliesti prie kodo, kad nesugadinti kažko, nes kitaip dar ilgiau užtrukčiau tau jo neišsiuntęs :Ddd
Sorry už nepatogumus

Basic kodo strategija:
Nupirkti kai macd crossinasi ir kai stochrsi nėra overbought (value < 60)
ir parduoti, kai yra bent vieno procento profitas ir stochrsi overbought (value > 60)

Stochrsi naudojau vietoj paprasto rsi, nes stochrsi yra gerokai jautresnis.

Rašyk, jei kas neaišku.

Jei išspręsi mano kodo problemas, būtų gerai, kad pasidalintum 
Būčiau labai labai dėkingas :))

Tikiuosi padėjau, jei kas neaišku, rašyk
