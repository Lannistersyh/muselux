"""Twelve original editorial SVG scenes; standalone, deterministic and offline."""
from pathlib import Path
from html import escape
import json,math,re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/img/journal'

DEFS='''<defs>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#8c622d"/><stop offset=".26" stop-color="#f3d99c"/><stop offset=".48" stop-color="#bc8c43"/><stop offset=".73" stop-color="#fff0c4"/><stop offset="1" stop-color="#ac7837"/></linearGradient>
<linearGradient id="silver" x1="0" y1="0" x2="1" y2=".7"><stop stop-color="#63767d"/><stop offset=".25" stop-color="#f4f7f6"/><stop offset=".46" stop-color="#a4b3b6"/><stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#859da5"/></linearGradient>
<linearGradient id="rose" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#a46c58"/><stop offset=".27" stop-color="#f0bea3"/><stop offset=".5" stop-color="#bf826c"/><stop offset=".75" stop-color="#f8ddc8"/><stop offset="1" stop-color="#9f6355"/></linearGradient>
<radialGradient id="pearl" cx=".31" cy=".25"><stop stop-color="#fffdf7"/><stop offset=".25" stop-color="#f9f3e6"/><stop offset=".63" stop-color="#dfd7c9"/><stop offset="1" stop-color="#9c9e98"/></radialGradient>
<radialGradient id="black-pearl" cx=".3" cy=".25"><stop stop-color="#c6d0bf"/><stop offset=".35" stop-color="#607a75"/><stop offset=".65" stop-color="#3d5258"/><stop offset="1" stop-color="#172f38"/></radialGradient>
<linearGradient id="leather" x2="1" y2="1"><stop stop-color="#d3a785"/><stop offset="1" stop-color="#a37755"/></linearGradient>
<pattern id="grain" width="30" height="24" patternUnits="userSpaceOnUse"><path d="M2 5q8-9 15-1m-3 7q10-7 15 1M0 20q7-9 15-3m10 6 4-3" fill="none" stroke="#553c2e" stroke-width="1.2" opacity=".28"/></pattern>
<pattern id="pinstripe" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M2 0v16" stroke="#b4bca8" stroke-width="2"/></pattern>
<pattern id="scarf-check" width="120" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(16)"><rect width="120" height="120" fill="#acb7d6"/><path d="M0 20h120M0 80h120M20 0v120M80 0v120" stroke="#f0e0c8" stroke-width="16"/><path d="M0 45h120M45 0v120" stroke="#392d66" stroke-width="8"/><path d="M0 102h120M102 0v120" stroke="#e9663e" stroke-width="5"/></pattern>
</defs>'''

def text(x,y,value,size=20,fill='#243538',font='Arial, sans-serif',spacing=None,anchor=None,italic=False):
    attrs=f' x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}"'
    if spacing is not None:attrs+=f' letter-spacing="{spacing}"'
    if anchor:attrs+=f' text-anchor="{anchor}"'
    if italic:attrs+=' font-style="italic"'
    return '<text'+attrs+'>'+escape(value)+'</text>'

def serif(x,y,value,size=64,fill='#243538',**kw):
    return text(x,y,value,size,fill,'Georgia, serif',**kw)

def imprint(number,label,ink='#243538'):
    return text(44,51,'MUSELUX / THE JOURNAL',13,ink,spacing=2.8)+text(1156,51,f'{number:02} / {label}',13,ink,spacing=1.8,anchor='end')

def pearl(x,y,r,dark=False):
    return f'<ellipse cx="{x+4}" cy="{y+r*.8}" rx="{r*.9}" ry="{r*.23}" fill="#0a1b26" opacity=".15"/><circle cx="{x}" cy="{y}" r="{r}" fill="url(#{"black-pearl" if dark else "pearl"})"/><ellipse cx="{x-r*.27}" cy="{y-r*.32}" rx="{r*.22}" ry="{r*.12}" fill="#fff" opacity=".5"/>'

def first_bag():
    art='<rect y="590" width="1200" height="210" fill="#e0cdb3"/><path d="M710 80 1200 330V0H710Z" fill="#e6b29e"/>'
    art+=serif(65,195,'First love.',91)+text(70,237,'MAKE ROOM FOR REAL LIFE.',16,spacing=3)
    art+='''<g transform="translate(0 35)"><ellipse cx="368" cy="670" rx="237" ry="27" fill="#78634f" opacity=".16"/>
<path d="M205 376 535 362 579 654Q370 697 163 650Z" fill="#263f51"/>
<path d="M255 385V302q0-89 56-89t57 89v74m32 0v-74q0-89 56-89t57 89v70" fill="none" stroke="#152e40" stroke-width="18"/>
<path d="m210 400 316-10 32 245q-180 36-374 0Z" fill="none" stroke="#a0adb4" stroke-width="1.5" stroke-dasharray="3 7"/>
<path d="M185 488q184 32 369-9" fill="none" stroke="#192f3e" stroke-width="7"/>
<rect x="339" y="473" width="54" height="32" rx="6" fill="url(#gold)"/></g>
<g transform="rotate(9 865 388)"><rect x="680" y="240" width="345" height="360" fill="#b9a58c" opacity=".15"/><rect x="666" y="226" width="345" height="360" fill="#faf6ed"/><path d="M703 320h271M703 409h271M703 498h271" stroke="#d5ccbc"/>'''
    for y,word in [(291,'YOUR DAY'),(380,'YOUR BUDGET'),(469,'YOUR WAY')]:
        art+=f'<rect x="702" y="{y-19}" width="19" height="19" fill="none" stroke="#b66c55"/>'+text(742,y,word,19,'#6f675b',spacing=2)
    art+='</g><circle cx="984" cy="642" r="34" fill="none" stroke="#9b7444" stroke-width="9"/><path d="m1008 666 63 61m-21-21 18-18m-2 35 19-18" fill="none" stroke="#9b7444" stroke-width="8"/>'
    return '#f2eadb',art,'CHOOSING WELL'

def two_bags():
    art='<rect x="600" width="600" height="800" fill="#d8dfd0"/><path d="M600 96v620" stroke="#71816e" stroke-dasharray="2 9"/>'
    art+=serif(64,180,'Two structures.',69)+serif(650,180,'Two rhythms.',69)
    art+='''<path d="M114 425h360l32 230H86Z" fill="#e0c8a6" stroke="#846f50" stroke-width="2"/>
<path d="M177 436V338q0-72 47-72t47 72v90m45 0v-90q0-72 47-72t47 72v90" fill="none" stroke="#8f7452" stroke-width="13"/>
<path d="m123 442 345 0-23 87H142Z" fill="#ebd9bf" stroke="#987d5d"/>
<path d="M103 543h386M181 441v143m213-143v143" stroke="#b99a73" stroke-width="16"/>
<rect x="272" y="534" width="46" height="30" fill="url(#gold)"/>
<path d="M698 401h351l42 260H660Z" fill="#4e6356" stroke="#2d4138" stroke-width="2"/>
<path d="M797 414V330q0-66 51-66t51 66v84" fill="none" stroke="#2e4438" stroke-width="14"/>
<path d="M705 415h333l-43 102H743Z" fill="#687c69" stroke="#2c4436"/>
<path d="M704 528h342" stroke="#a7af85" stroke-width="15"/>
<rect x="854" y="515" width="42" height="29" fill="url(#gold)"/>
<path d="M1038 422q90-46 99 40t-66 157" fill="none" stroke="#344d3d" stroke-width="11"/>
<path d="M72 686h450m-450-11v22m450-22v22M642 686h485m-485-11v22m485-22v22" stroke="#9b9a7e"/>'''
    art+=text(300,742,'BIRKIN / TWO HANDLES',17,anchor='middle',spacing=2.4)+text(890,742,'KELLY / ONE HANDLE + STRAP',17,anchor='middle',spacing=1.8)
    return '#f4efe4',art,'FORM & FUNCTION'

def symbols():
    art=serif(60,166,'A jewelry alphabet.',75,'#763f3f')+text(65,207,'FIVE MOTIFS. FIVE WAYS TO SAY SOMETHING.',15,'#735f54',spacing=2.2)
    art+='<path d="M50 466h1100M400 247v486M799 247v486" stroke="#d0bca7" stroke-width="1"/>'
    # Screw heads, rather than the old pair of generic bands.
    art+='<circle cx="221" cy="345" r="75" fill="#ad8350"/><circle cx="221" cy="341" r="72" fill="url(#gold)"/><circle cx="221" cy="341" r="43" fill="#f2ebdf"/>'
    for angle in (0,90,180,270):
        x=221+58*math.cos(math.radians(angle));y=341+58*math.sin(math.radians(angle))
        art+=f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="#815d37" stroke-width="2"/><path d="M{x-6} {y}h12" stroke="#815d37" stroke-width="2" transform="rotate(35 {x} {y})"/>'
    art+=text(220,447,'01 / THE SCREW',14,'#735f54',spacing=2,anchor='middle')
    art+='''<ellipse cx="588" cy="341" rx="71" ry="31" fill="#303b33"/>
<path d="M631 331q18-15 20-31l26 13-13 38-34 11Z" fill="#303b33"/>
<circle cx="677" cy="311" r="27" fill="#303b33"/><ellipse cx="697" cy="321" rx="19" ry="11" fill="#303b33"/>
<path d="m658 295-2-25 21 19m6-1 18-19-2 29" fill="#303b33"/>
<path d="m551 357-13 56h17l20-57m34-3 10 58h17l-2-61m8-7q19 28 52 40l9-12-42-34" fill="#303b33"/>
<path d="M523 342q-57-5-55-47t-22-33" fill="none" stroke="#303b33" stroke-width="13" stroke-linecap="round"/>
<circle cx="690" cy="307" r="3" fill="#d9c797"/>'''
    for x,y in [(550,333),(582,331),(613,338),(566,353),(599,356),(645,328)]:art+=f'<circle cx="{x}" cy="{y}" r="5" fill="#a09c66"/>'
    art+=text(600,447,'02 / THE PANTHER',14,'#735f54',spacing=2,anchor='middle')
    art+='<path d="M995 343c-81-93-130 6-63 35-65 58 30 108 63 38 48 72 124-1 59-38 76-49-9-122-59-35Z" transform="translate(0 -40)" fill="#7e9780" stroke="url(#gold)" stroke-width="8"/>'+text(998,447,'03 / THE CLOVER',14,'#735f54',spacing=2,anchor='middle')
    art+='''<path d="M137 645q111 83 133 5t-59-79q-68-2-45-49t86-10" fill="none" stroke="url(#gold)" stroke-width="26" stroke-linecap="round"/>
<path d="m248 500 40 4-17 20-23-5Z" fill="#c4a36c"/><circle cx="270" cy="507" r="3" fill="#283c35"/>
<path d="M160 548l13 12m-3 30 17 8m40 2 12 8m14 33 15 7m-46 25 2 13m-46-25-3 13" stroke="#8d713f" stroke-width="2"/>'''
    art+=text(220,733,'04 / THE SERPENT',14,'#735f54',spacing=2,anchor='middle')
    art+='<g transform="rotate(32 602 586)"><circle cx="602" cy="548" r="45" fill="none" stroke="url(#gold)" stroke-width="14"/><path d="M602 594v116h32v-19h-32m0-8h23v-17h-23" fill="none" stroke="url(#gold)" stroke-width="13"/></g>'+text(600,733,'05 / THE KEY',14,'#735f54',spacing=2,anchor='middle')
    art+=serif(844,565,'Little signs,',42,'#763f3f',italic=True)+serif(844,623,'lasting',57,'#763f3f')+serif(844,685,'meanings.',57,'#763f3f')
    return '#f2ebdf',art,'A LANGUAGE OF SYMBOLS'

def pearls():
    art='<circle cx="915" cy="251" r="375" fill="#193c4a"/><path d="M0 677q470-231 1200-93v216H0Z" fill="#365d65"/>'
    art+=serif(65,173,'Light,',104,'#f4e9d1')+serif(64,273,'held still.',88,'#f4e9d1')
    # A fan-like shell and three deliberately different pearl scales/tones.
    art+='''<path d="M610 634 474 417q72-151 214-151 164 2 225 183L720 636Z" fill="#c4bdae"/>
<path d="M671 620 487 422m184 198L532 340m139 280L605 284m66 336 17-346m-17 346 92-327m-92 327 160-272m-160 272 222-171" stroke="#e7dfd1" stroke-width="9"/>
<path d="M610 634q72-17 110 2l-9 31h-92Z" fill="#dbd1bd"/>'''
    art+=pearl(728,450,91)+pearl(968,548,68,True)+pearl(493,622,46)
    for i in range(10):
        a=math.radians(155+i*13);art+=pearl(960+152*math.cos(a),293+135*math.sin(a),10)
    art+=text(70,710,'LUSTRE / OVERTONE / SURFACE',16,'#d5e1d7',spacing=2.7)+text(70,748,'AKOYA   ·   SOUTH SEA   ·   TAHITIAN',12,'#b2c7c3',spacing=2)
    return '#0e2936',art,'THE QUIET GLOW'

def metals():
    art=serif(65,176,'A matter',88,'#efeee5')+serif(65,266,'of metal.',88,'#efeee5')
    art+=text(70,318,'COLOUR. ALLOY. TOUCH.',16,'#9baeb4',spacing=3)
    art+='''<path d="M490 285q232-245 585-81l-78 83Q740 173 576 367Z" fill="#071d28"/>
<path d="M485 260q246-247 600-81l-81 84Q745 147 566 344Z" fill="url(#gold)"/>
<path d="M490 263q235-222 579-79" fill="none" stroke="#fff0bf" stroke-width="2"/>
<path d="M407 445q239-237 668-72l-81 83Q657 337 491 531Z" fill="#061922"/>
<path d="M403 421q237-235 682-71l-83 84Q658 308 483 508Z" fill="url(#silver)"/>
<path d="M405 422q250-213 660-68" fill="none" stroke="#fff" stroke-width="2"/>
<path d="M309 613q245-224 758-51l-78 85Q595 519 389 700Z" fill="#071c25"/>
<path d="M305 587q249-222 775-50l-81 85Q595 488 383 675Z" fill="url(#rose)"/>
<path d="M309 588q260-199 751-45" fill="none" stroke="#fbe3d5" stroke-width="2"/>
<path d="M1060 254v49m-13-49h26m-26 49h26M1080 429v51m-13-51h26m-26 51h26M1050 621v51m-13-51h26m-26 51h26" stroke="#8a9e9f"/>'''
    art+=text(65,705,'YELLOW GOLD',14,'#d5b570',spacing=2.5)+text(65,735,'PLATINUM',14,'#c8d5d6',spacing=2.5)+text(65,765,'ROSE GOLD',14,'#d8a28e',spacing=2.5)
    return '#17313d',art,'A STUDY IN METAL'

def leathers():
    art=serif(65,177,'Surface stories.',78,'#f7ebd4')+text(70,220,'FOUR TEXTURES. FOUR DIFFERENT FEELINGS.',15,'#e2be9f',spacing=2.5)
    art+='''<ellipse cx="644" cy="703" rx="457" ry="38" fill="#472e29" opacity=".19"/>
<g transform="rotate(-14 340 464)"><rect x="116" y="292" width="390" height="336" rx="33" fill="#c59b6c"/><rect x="116" y="292" width="390" height="336" rx="33" fill="url(#grain)"/><rect x="130" y="307" width="361" height="307" rx="25" fill="none" stroke="#f0d5ae" stroke-width="2" stroke-dasharray="4 5"/></g>
<g transform="rotate(7 669 450)"><rect x="462" y="267" width="366" height="374" rx="30" fill="#d6ad86"/><path d="M480 290q145 82 326 0" fill="none" stroke="#f1d7b2" stroke-width="2"/><path d="M807 291v326" stroke="#ad805e" stroke-width="3"/></g>
<g transform="rotate(18 929 534)"><rect x="775" y="341" width="297" height="362" rx="24" fill="#6c5551"/><rect x="789" y="355" width="269" height="333" rx="18" fill="none" stroke="#bfa092" stroke-dasharray="4 5"/><path d="M811 374q94 39 231 0" stroke="#8f7570" fill="none"/></g>
<path d="M171 632q228-134 474 10t395-11l-37 104q-224 47-412-14t-421 13Z" fill="#d7bca2"/>
<path d="M174 632q215-113 461 12t397-12" stroke="#efdbc4" stroke-width="4" fill="none"/>'''
    art+=text(163,515,'PEBBLED',16,'#6f4a35',spacing=3)+text(558,478,'SMOOTH',16,'#79533c',spacing=3)+text(848,555,'SOFT',16,'#e1cbbc',spacing=3)
    return '#9a5445',art,'THE FEEL OF LEATHER'

def scarves():
    art=serif(63,171,'One square.',84,'#372c62')+serif(65,254,'Many lives.',84,'#372c62')
    art+='''<path d="M193 586q173-276 431-103t362-108l72 90q-161 280-445 104T248 707Z" fill="#7c81aa" opacity=".22"/>
<path d="M177 554q174-287 441-104t371-125l80 107q-148 319-467 120T248 687Z" fill="url(#scarf-check)"/>
<path d="M176 554q174-287 442-104t371-125" fill="none" stroke="#ece2c7" stroke-width="8"/>
<path d="M248 687q55-331 354-135t467-120" fill="none" stroke="#e66c43" stroke-width="9"/>
<path d="M577 401q-90-167-118-84t101 162m51-31q170-141 184-52t-166 129" fill="none" stroke="#372d65" stroke-width="54"/>
<path d="M577 401q-90-167-118-84t101 162m51-31q170-141 184-52t-166 129" fill="none" stroke="#eb9b70" stroke-width="32"/>
<path d="m568 445 73-25 41 86-81 28Z" fill="#e16b41"/>
<path d="m566 448 110 52" stroke="#f2cb9e" stroke-width="3"/>
<path d="m574 506-68 253 80-33 42 40 2-237m11-24 156 202 11-61 63 1-172-178" fill="url(#scarf-check)" stroke="#e6d5bb" stroke-width="3"/>'''
    art+=text(70,748,'TIE IT. FOLD IT. MAKE IT YOURS.',15,'#453a6c',spacing=3)
    return '#e0def0',art,'A SQUARE OF POSSIBILITIES'

def vintage():
    art=serif(65,178,'A second chapter.',75,'#f0e0c5')+text(71,224,'GOOD STORIES DESERVE A CLOSER LOOK.',15,'#d1aa91',spacing=2)
    art+='''<g transform="rotate(-7 528 492)"><rect x="168" y="280" width="681" height="404" fill="#412c30" opacity=".3"/><rect x="154" y="265" width="681" height="404" fill="#e3d4b7"/>
<path d="M192 308h116m-116 17h75" stroke="#7e6d5d" stroke-width="3"/>
<path d="M334 422h313l26 179H305Z" fill="#936047"/><path d="M405 435v-69q0-70 47-70t47 70v69m38 0v-69q0-70 43-70t43 70v69" fill="none" stroke="#68432f" stroke-width="13"/>
<path d="m347 437 285 0-24 71H364Z" fill="#af7e59"/><path d="M325 520h335" stroke="#735035" stroke-width="15"/><rect x="476" y="509" width="41" height="27" fill="url(#gold)"/>
<path d="M329 546v39m9-47v48m312-58-4 49" stroke="#be9873" stroke-width="2"/>
</g><g transform="rotate(11 980 401)"><path d="M889 275h173l25 31v270H861V306Z" fill="#e9b493"/><circle cx="972" cy="307" r="8" fill="#865349"/><path d="M972 307q55-183 152-113" fill="none" stroke="#b59472" stroke-width="2"/></g>
<circle cx="827" cy="566" r="98" fill="#f4eddb" fill-opacity=".4" stroke="#253b3a" stroke-width="17"/>
<path d="m899 640 99 98" stroke="#253b3a" stroke-width="29" stroke-linecap="round"/>
<path d="m772 579 97-17m-94 31 97-17" stroke="#c39972" stroke-width="2" stroke-dasharray="4 5"/>'''
    art+=text(974,372,'ARCHIVE',17,'#794c3d',anchor='middle',spacing=2.5)+text(974,417,'CONDITION',12,'#794c3d',anchor='middle',spacing=1.8)+text(974,450,'PROVENANCE',12,'#794c3d',anchor='middle',spacing=1.3)+text(70,752,'THE BEAUTY OF A LIFE ALREADY LIVED.',14,'#d7b49a',spacing=2)
    return '#693e42',art,'STORIES WITH A PAST'

def timepieces():
    art=serif(63,168,'Time,',105,'#26383a')+serif(63,271,'on your terms.',67,'#26383a')
    art+='<circle cx="929" cy="460" r="339" fill="#d6c7aa"/><circle cx="929" cy="450" r="329" fill="#f5f0e1" stroke="#344a48" stroke-width="3"/><circle cx="929" cy="450" r="297" fill="none" stroke="#b6ac92"/>'
    for i in range(60):
        a=math.radians(i*6);r1=269 if i%5==0 else 283;r2=295
        art+=f'<path d="M{929+r1*math.sin(a):.2f} {450-r1*math.cos(a):.2f}  {929+r2*math.sin(a):.2f} {450-r2*math.cos(a):.2f}" stroke="#304846" stroke-width="{5 if i%5==0 else 1.5}"/>'
    art+='<path d="m929 450-137-131m137 131 181-104" stroke="#334b49" stroke-width="16" stroke-linecap="round"/><path d="m929 450-56 222" stroke="#bc593e" stroke-width="3"/><circle cx="929" cy="450" r="13" fill="#bc593e"/>'
    for i,(word,symbol) in enumerate([('MECHANICAL','gear'),('QUARTZ','diamond'),('CONNECTED','wave')]):
        y=400+i*125
        if symbol=='gear':
            art+=f'<circle cx="110" cy="{y}" r="24" fill="none" stroke="#65786b" stroke-width="9"/>'
            for a in range(0,360,45):art+=f'<path d="M110 {y-24}v-11" stroke="#65786b" stroke-width="9" transform="rotate({a} 110 {y})"/>'
        elif symbol=='diamond':art+=f'<path d="m110 {y-31} 26 31-26 31-26-31Z" fill="none" stroke="#65786b" stroke-width="3"/>'
        else:art+=f'<path d="M77 {y+10}q33-40 66 0m-53 9q20-24 40 0m-28 9q8-9 16 0" fill="none" stroke="#65786b" stroke-width="4"/>'
        art+=text(166,y+7,word,17,'#5d6f63',spacing=2.5)
    return '#e7e4d5',art,'TIME, SLOWLY'

def caring():
    art='<path d="M0 580 1200 375v425H0Z" fill="#c7cfb9"/>'+serif(63,168,'Keep a little',79,'#344a3d')+serif(63,253,'beauty close.',79,'#344a3d')
    art+='''<g transform="rotate(-9 303 496)"><path d="M101 344h354l-14 306H86Z" fill="#eee9da"/><path d="M101 344h354l-14 306H86Z" fill="url(#pinstripe)"/><path d="m101 344 41 37h283l30-37" fill="#f8f4e8"/><path d="M139 380v236m21-236v236" stroke="#d5d7c8"/></g>
<g transform="rotate(8 820 504)"><rect x="575" y="315" width="494" height="378" rx="47" fill="#aeb49e"/><rect x="591" y="329" width="463" height="348" rx="35" fill="#e3dfcd"/><path d="M820 333v339M593 500h458" stroke="#b6b59f" stroke-width="8"/>
<path d="M640 378q145-42 126 65t-139 0 107-65" fill="none" stroke="url(#gold)" stroke-width="5"/>
<path d="M877 371q119 75 115 202" fill="none" stroke="#a17c47" stroke-width="2"/>
<path d="M878 374q50 68 95 87" fill="none" stroke="#d8b46f" stroke-width="5"/>
<path d="M636 545h133v92H636Z" fill="#b9c0a9"/><path d="M636 545q67 26 133 0" stroke="#8c9e87" fill="none"/>
</g>'''
    for i in range(9):
        a=math.radians(i*25-110);art+=pearl(947+55*math.cos(a),563+41*math.sin(a),9)
    art+='<g transform="rotate(-19 453 655)"><path d="M359 627h169v48H359Z" fill="#bc9272"/><path d="M362 674v31m8-31v34m8-34v32m8-32v34m8-34v31m8-31v33m8-33v34m8-34v31m8-31v33m8-33v32m8-32v34m8-34v30m8-30v33m8-33v34m8-34v32m8-32v34m8-34v31m8-31v33m8-33v32m8-32v34m8-34v31" stroke="#dfcfb5" stroke-width="5"/></g>'
    art+=text(66,750,'REST. SEPARATE. STORE WITH CARE.',14,'#536b53',spacing=2.5)
    return '#e7eadb',art,'THE ART OF CARING'

def gifts():
    art=serif(65,171,'The thought',90,'#4b3843')+serif(65,267,'counts.',90,'#4b3843')
    # Three different packages, rather than one box copied across the scene.
    art+='''<ellipse cx="652" cy="697" rx="482" ry="35" fill="#8e6764" opacity=".13"/>
<path d="m128 559 221-19 39 39v128l-218 20-42-41Z" fill="#b07265"/><path d="m128 559 42 40 218-20-39-39Z" fill="#d9b0a2"/><path d="m170 599 218-20v128l-218 20Z" fill="#c58b7d"/>
<path d="m230 549 37 40v130l24-2V588l-38-42Z" fill="#3d4b66"/>
<path d="m407 440 270-37 44 35v264l-270 30-44-39Z" fill="#b2b8c8"/><path d="m407 440 44 41 270-43-44-35Z" fill="#d4d7e1"/><path d="m451 481 270-43v264l-270 30Z" fill="#bec6d5"/>
<path d="M532 464v258l29-3V460Z" fill="#f5e7c9"/>
<path d="M547 458q-78-117-100-57t99 59q86-109 107-43t-106 43" fill="none" stroke="#eee0c3" stroke-width="17"/>
<path d="M811 359h237v331H811Z" fill="#ce8164"/><path d="m811 359 39-29h236l-38 29Z" fill="#e8a188"/><path d="m1048 359 38-29v330l-38 30Z" fill="#ae6755"/>
<path d="M811 450h238v27H811Z" fill="#f0d3b8"/><path d="M914 359h25v330h-25Z" fill="#f0d3b8"/>
<path d="M929 360q-21-111-77-93t76 91q17-112 73-95t-72 95" fill="none" stroke="#f0d3b8" stroke-width="16"/>
<g transform="rotate(-8 1045 207)"><rect x="883" y="137" width="275" height="134" fill="#faf3e6"/><path d="M907 185h223m-223 28h164" stroke="#d3b2a3" stroke-width="2"/></g>'''
    art+=serif(917,177,'For you.',24,'#9a6759',italic=True)+text(66,758,'SMALL GESTURES. PERSONAL STORIES.',14,'#8b6463',spacing=2.3)
    return '#f0dbd3',art,'A THOUGHTFUL LITTLE GIFT'

def fragrances():
    art=serif(66,178,'Scent is',100,'#3b5749')+serif(66,283,'memory.',100,'#3b5749')
    art+='''<circle cx="1048" cy="157" r="255" fill="#e4bb57" opacity=".45"/>
<path d="M621 595q180-195 432-180" stroke="#c69f56" stroke-width="2" fill="none"/>
<path d="m879 422-30-89q80 24 73 81m-18 8 66-71q28 66-48 78m37-10 67-39q7 64-75 62" fill="#768b62"/>
<path d="M561 664q124-145 218-144" stroke="#758457" stroke-width="2" fill="none"/>
<path d="M605 612q-75-37-24-72 54 10 51 53m16-1q-8-93 54-77 30 40-27 68" fill="#a1ad75"/>
<ellipse cx="856" cy="705" rx="245" ry="29" fill="#ac8c53" opacity=".15"/>
<rect x="781" y="257" width="163" height="87" rx="4" fill="#355244"/>
<rect x="807" y="343" width="110" height="43" fill="#bf9a51"/>
<path d="M749 386h226l44 52v237q0 18-19 18H721q-18 0-18-18V439Z" fill="#eee6bf" fill-opacity=".65" stroke="#b6a373" stroke-width="3"/>
<path d="M719 491h284v181H719Z" fill="#cda155" fill-opacity=".65"/>
<path d="M717 445v225q0 10 13 10" stroke="#fff9dc" stroke-width="5" fill="none"/>
<rect x="756" y="485" width="208" height="126" fill="#f7f0db"/>
<path d="M757 625h205" stroke="#d1b776"/>
<g transform="rotate(-12 353 507)"><rect x="166" y="393" width="354" height="48" fill="#faf6e5"/><rect x="166" y="473" width="403" height="48" fill="#faf6e5"/><rect x="166" y="553" width="348" height="48" fill="#faf6e5"/>'''
    art+=text(190,424,'01 / CITRUS',15,'#7f8161',spacing=2)+text(190,504,'02 / FLORAL',15,'#7f8161',spacing=2)+text(190,584,'03 / WOODS',15,'#7f8161',spacing=2)+'</g>'
    art+=serif(860,538,'NOTES',30,'#5e6849',anchor='middle',spacing=4)+text(860,577,'A PERSONAL STUDY',11,'#7f8161',anchor='middle',spacing=2)+text(67,747,'FOLLOW WHAT LINGERS.',15,'#697451',spacing=3)
    return '#f0e6bb',art,'A MEMORY IN NOTES'

SCENES=[
 ('mag-01','first-love',first_bag,'靛蓝手袋与生活清单、钥匙组成的日常选包静物插画'),
 ('mag-02','two-rhythms',two_bags,'以建筑制图构图比较双提手与单提手手袋结构的插画'),
 ('mag-03','jewelry-alphabet',symbols,'螺钉、猎豹、四叶草、灵蛇与钥匙组成的五种珠宝符号图谱'),
 ('mag-04','held-light',pearls,'深海蓝背景上的贝壳与不同尺寸的浅色、深色珍珠光泽研究'),
 ('mag-05','matter-of-metal',metals,'深蓝底上黄金、铂金与玫瑰金三道弯曲金属切面的材质插画'),
 ('mag-06','surface-stories',leathers,'赤陶背景上不同纹理、色调与柔软程度的皮革样片插画'),
 ('mag-07','one-square',scarves,'淡紫背景上橙蓝格纹丝巾盘旋成结的动感插画'),
 ('mag-08','second-chapter',vintage,'酒红色档案桌面上的旧手袋、来源标签与检查缝线的放大镜'),
 ('mag-09','time-on-your-terms',timepieces,'奶油色大幅表盘与机械、石英及连接信号三种时间符号'),
 ('mag-10','care-ritual',caring,'鼠尾草绿桌面上分格首饰盘、软布、珍珠、链条与养护刷的静物插画'),
 ('mag-11','the-thought-counts',gifts,'粉杏色背景上三种不同包装与手写卡片组成的礼物静物'),
 ('mag-12','scent-is-memory',fragrances,'浅黄色背景上玻璃香水瓶、植物与三张试香纸组成的气味研究'),
]

def draw_covers(articles):
    OUT.mkdir(parents=True,exist_ok=True)
    result={}
    for i,(article_id,slug,scene,alt) in enumerate(SCENES,1):
        bg,art,label=scene()
        ink='#e4dfca' if article_id in ('mag-04','mag-05','mag-06','mag-08') else '#536052'
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" role="img" aria-labelledby="title desc" data-scene="{slug}"><title id="title">{escape(label)}</title><desc id="desc">{escape(alt)}。原创专题概念插画，不代表具体产品实物。</desc>{DEFS}<rect width="1200" height="800" fill="{bg}"/>{art}{imprint(i,label,ink)}</svg>'''
        path=OUT/f'{article_id}-{slug}.svg';path.write_text(svg)
        result[article_id]={'cover':str(path.relative_to(ROOT)),'coverAlt':alt,'coverScene':slug}
    assert {x['id'] for x in articles}==set(result),'Every article needs its own scene'
    return result

def main():
    path=ROOT/'tools/content.json';data=json.loads(path.read_text())
    covers=draw_covers(data['articles'])
    for article in data['articles']:article.update(covers[article['id']])
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    for article_id in covers:(ROOT/'assets/img'/f'{article_id}.svg').unlink(missing_ok=True)
    print('Drew 12 distinct, article-specific journal covers.')

if __name__=='__main__':main()
