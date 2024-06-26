# -*- coding:utf-8 -*-
# Date: 2021-08-30
# Author:kracer
# Version: 1.5

from config import *
import argparse, sys, ipaddress, os
import dominate, socket
from dominate.tags import *
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import colorama


# 帮助说明函数定义
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython3 ' + sys.argv[0] + " -u http://www.google.com")
    # parser.add_argument("-h", "--help", help="show this help message and exit")
    parser.add_argument("-u", "--url", help="The website to scan")
    parser.add_argument("-p", "--proxy", help="Use an HTTP proxy to perform requests, examples:http://hostname:8080, \nsocks5://hostname:1080,http://user:pass@hostname:8080")
    parser.add_argument("-f", "--file", help="Scanning the address in the file")
    parser.add_argument('--ports', help='ports to scan examples: 80,443,8000-99000')
    parser.add_argument('-t', '--thread', type=int, help='max threads')
    return parser.parse_args()


# 预处理用户输入的URL
def processUrl(url):
    URL = []
    url2list = url.split('.')
    if len(url2list) != 1:  # 排除不是网址的情况
        if url.endswith('/'):  # 去掉末尾'/'
            url = url.rstrip('/')
        if '://' in url:
            url0 = url[url.find(':')+3:]  # 去掉http://或https://
            URL.append(url0)
        else:
            URL.append(url)
    else:
        return URL
    tld_list = ['ac','com.ac','edu.ac','gov.ac','net.ac','mil.ac','org.ac',
                'ad','nom.ad','ae','co.ae','net.ae','org.ae','sch.ae','ac.ae',
                'gov.ae','mil.ae','aero','accident-investigation.aero',
                'accident-prevention.aero','aerobatic.aero','aeroclub.aero','aerodrome.aero',
                'agents.aero','aircraft.aero','airline.aero','airport.aero',
                'air-surveillance.aero','airtraffic.aero','air-traffic-control.aero',
                'ambulance.aero','amusement.aero','association.aero','author.aero',
                'ballooning.aero','broker.aero','caa.aero','cargo.aero','catering.aero',
                'certification.aero','championship.aero','charter.aero','civilaviation.aero',
                'club.aero','conference.aero','consultant.aero','consulting.aero',
                'control.aero','council.aero','crew.aero','design.aero',
                'dgca.aero','educator.aero','emergency.aero','engine.aero',
                'engineer.aero','entertainment.aero','equipment.aero','exchange.aero',
                'express.aero','federation.aero','flight.aero','freight.aero',
                'fuel.aero','gliding.aero','government.aero','groundhandling.aero',
                'group.aero','hanggliding.aero','homebuilt.aero','insurance.aero',
                'journal.aero','journalist.aero','leasing.aero','logistics.aero',
                'magazine.aero','maintenance.aero','marketplace.aero','media.aero',
                'microlight.aero','modelling.aero','navigation.aero',
                'parachuting.aero','paragliding.aero','passenger-association.aero',
                'pilot.aero','press.aero','production.aero',
                'recreation.aero','repbody.aero','res.aero',
                'research.aero','rotorcraft.aero','safety.aero',
                'scientist.aero','services.aero','show.aero',
                'skydiving.aero','software.aero','student.aero',
                'taxi.aero','trader.aero','trading.aero',
                'trainer.aero','union.aero','workinggroup.aero',
                'works.aero','af','gov.af','com.af','org.af','net.af','edu.af',
                'ag','com.ag','org.ag','net.ag','co.ag','nom.ag','ai','off.ai',
                'com.ai','net.ai','org.ai','al','com.al','edu.al','gov.al','mil.al',
                'net.al','org.al','am','an','com.an','net.an','org.an','edu.an',
                'ao','ed.ao','gv.ao','og.ao','co.ao','pb.ao','it.ao','aq','*.ar',
                '!congresodelalengua3.ar','!educ.ar','!gobiernoelectronico.ar',
                '!mecon.ar','!nacion.ar','!nic.ar','!promocion.ar','!retina.ar',
                '!uba.ar','e164.arpa','in-addr.arpa','ip6.arpa','iris.arpa',
                'uri.arpa','urn.arpa','as','gov.as','asia','at','ac.at','co.at',
                'gv.at','or.at','act.au','nsw.au','nt.au','qld.au','sa.au',
                'tas.au','vic.au','wa.au','act.edu.au','nsw.edu.au','nt.edu.au',
                'qld.edu.au','sa.edu.au','tas.edu.au','vic.edu.au','wa.edu.au',
                'act.gov.au','nt.gov.au','qld.gov.au','sa.gov.au','tas.gov.au',
                'vic.gov.au','wa.gov.au','aw','com.aw','ax','az','com.az','net.az',
                'int.az','gov.az','org.az','edu.az','info.az','pp.az','mil.az',
                'name.az','pro.az','biz.az','ba','org.ba','net.ba','edu.ba',
                'gov.ba','mil.ba','unsa.ba','unbi.ba','co.ba','com.ba','rs.ba','bb',
                'biz.bb','com.bb','edu.bb','gov.bb','info.bb','net.bb','org.bb','store.bb','*.bd','be',
                'ac.be','bf','gov.bf','bg','a.bg','b.bg','c.bg','d.bg','e.bg','f.bg','g.bg','h.bg','i.bg',
                'j.bg','k.bg','l.bg','m.bg','n.bg','o.bg','p.bg','q.bg','r.bg','s.bg','t.bg','u.bg','v.bg','w.bg','x.bg','y.bg','z.bg','0.bg','1.bg','2.bg','3.bg','4.bg','5.bg','6.bg','7.bg','8.bg',
                'bh','com.bh','edu.bh','net.bh','org.bh','gov.bh','bi','co.bi','com.bi','edu.bi','or.bi','org.bi','biz','bj','asso.bj','barreau.bj',
                'gouv.bj','bm','com.bm','edu.bm','gov.bm','net.bm','org.bm','*.bn','bo','com.bo','edu.bo','gov.bo','gob.bo','int.bo','org.bo','net.bo',
                'mil.bo','tv.bo','br','adm.br','adv.br','agr.br','am.br','arq.br','art.br','ato.br','b.br','bio.br','blog.br',
                'bmd.br','can.br','cim.br','cng.br','cnt.br','com.br','coop.br','ecn.br','edu.br','emp.br','eng.br','esp.br','etc.br','eti.br','far.br','flog.br',
                'fm.br','fnd.br','fot.br','fst.br','g12.br','ggf.br','gov.br','imb.br','ind.br','inf.br','jor.br','jus.br','lel.br','mat.br','med.br','mil.br','mus.br','net.br','nom.br','not.br','ntr.br','odo.br','org.br','ppg.br','pro.br','psc.br','psi.br','qsl.br','radio.br','rec.br','slg.br','srv.br',
                'taxi.br','teo.br','tmp.br','trd.br','tur.br','tv.br','vet.br','vlog.br','wiki.br','zlg.br','bs','com.bs','net.bs','org.bs','edu.bs','gov.bs','bt','com.bt','edu.bt','gov.bt','net.bt','org.bt','bw','co.bw','org.bw','by','gov.by','mil.by','com.by','of.by','bz','com.bz','net.bz','org.bz','edu.bz','gov.bz','ca','ab.ca','bc.ca','mb.ca',
                'nb.ca','nf.ca','nl.ca','ns.ca','nt.ca','nu.ca','on.ca','pe.ca','qc.ca','sk.ca','yk.ca','gc.ca','cat','cc','cd','gov.cd','cf','cg','ch','ci','org.ci','or.ci','com.ci','co.ci','edu.ci','ed.ci','ac.ci','net.ci','go.ci','asso.ci','int.ci','presse.ci','md.ci','gouv.ci','*.ck','!www.ck','cl','gov.cl','gob.cl','co.cl','mil.cl','cm','gov.cm','cn','ac.cn','com.cn','edu.cn','gov.cn','net.cn','org.cn','mil.cn','ah.cn','bj.cn','cq.cn','fj.cn','gd.cn','gs.cn','gz.cn','gx.cn','ha.cn','hb.cn','he.cn','hi.cn','hl.cn',
                'hn.cn','jl.cn','js.cn','jx.cn','ln.cn','nm.cn','nx.cn','qh.cn','sc.cn','sd.cn','sh.cn','sn.cn','sx.cn','tj.cn','xj.cn','xz.cn','yn.cn','zj.cn','hk.cn','mo.cn','tw.cn','co','arts.co','com.co','edu.co','firm.co','gov.co','info.co','int.co','mil.co','net.co','nom.co','org.co','rec.co','web.co','com','coop','cr','ac.cr','co.cr','ed.cr','fi.cr','go.cr','or.cr','sa.cr','cu','com.cu','edu.cu','org.cu','net.cu','gov.cu','inf.cu','cv','cx','gov.cx','*.cy','cz','de','dj','dk','dm','com.dm','net.dm','org.dm','edu.dm','gov.dm','do','art.do','com.do','edu.do',
                'gob.do','gov.do','mil.do','net.do','org.do','sld.do','web.do','dz','com.dz','org.dz','net.dz','gov.dz','edu.dz','asso.dz','pol.dz','art.dz','ec','com.ec','info.ec','net.ec','fin.ec','k12.ec','med.ec','pro.ec','org.ec','edu.ec','gov.ec','gob.ec','mil.ec','edu','ee','edu.ee','gov.ee','riik.ee','lib.ee','med.ee','com.ee','pri.ee','aip.ee','org.ee','fie.ee','com.eg','edu.eg','eun.eg','gov.eg','mil.eg','name.eg','net.eg','org.eg','sci.eg','*.er','es','com.es','nom.es','org.es','gob.es','edu.es','*.et','eu','fi','aland.fi','*.fj','*.fk','fm','fo','fr','com.fr','asso.fr',
                'nom.fr','prd.fr','presse.fr','tm.fr','aeroport.fr','assedic.fr','avocat.fr','avoues.fr','cci.fr','chambagri.fr','chirurgiens-dentistes.fr','experts-comptables.fr','geometre-expert.fr','gouv.fr','greta.fr','huissier-justice.fr','medecin.fr','notaires.fr','pharmacien.fr','port.fr','veterinaire.fr','ga','gd','ge','com.ge','edu.ge','gov.ge','org.ge','mil.ge','net.ge','pvt.ge','gf','gg','co.gg','org.gg','net.gg','sch.gg','gov.gg','gh','com.gh','edu.gh','gov.gh','org.gh','mil.gh','gi','com.gi','ltd.gi','gov.gi','mod.gi','edu.gi','org.gi','gl','gm','ac.gn','com.gn','edu.gn','gov.gn','org.gn','net.gn','gov','gp','com.gp','net.gp','mobi.gp','edu.gp','org.gp','asso.gp','gq','gr','com.gr','edu.gr','net.gr','org.gr','gov.gr',
                'gs','*.gt','!www.gt','*.gu','gw','gy','co.gy','com.gy','net.gy','hk','com.hk','edu.hk','gov.hk','idv.hk','net.hk','org.hk','hm','hn','com.hn','edu.hn','org.hn','net.hn','mil.hn','gob.hn','hr','iz.hr','from.hr','name.hr','com.hr','ht','com.ht','shop.ht','firm.ht','info.ht','adult.ht','net.ht','pro.ht','org.ht','med.ht','art.ht','coop.ht','pol.ht','asso.ht','edu.ht','rel.ht','gouv.ht','perso.ht','hu','co.hu','info.hu','org.hu','priv.hu','sport.hu','tm.hu','2000.hu','agrar.hu','bolt.hu','casino.hu','city.hu','erotica.hu','erotika.hu','film.hu','forum.hu','games.hu','hotel.hu','ingatlan.hu','jogasz.hu','konyvelo.hu','lakas.hu','media.hu','news.hu','reklam.hu','sex.hu','shop.hu','suli.hu','szex.hu','tozsde.hu','utazas.hu','video.hu','id','ac.id','co.id','go.id','mil.id','net.id','or.id','sch.id','web.id','ie','gov.ie','*.il','im','co.im','ltd.co.im','plc.co.im','net.im','gov.im','org.im','nic.im','ac.im','in','co.in','firm.in','net.in','org.in','gen.in','ind.in','nic.in','ac.in','edu.in','res.in','gov.in','mil.in','info','int','eu.int','io','com.io','iq','gov.iq','edu.iq','mil.iq','com.iq','org.iq','net.iq','ir','ac.ir','co.ir','gov.ir','id.ir','net.ir','org.ir','sch.ir','is','net.is','com.is','edu.is','gov.is','org.is','int.is','it','gov.it','edu.it','agrigento.it','ag.it','alessandria.it','al.it','ancona.it','an.it','aosta.it','aoste.it','ao.it','arezzo.it','ar.it','ascoli-piceno.it','ascolipiceno.it','ap.it','asti.it','at.it','avellino.it','av.it','bari.it','ba.it','andria-barletta-trani.it','andriabarlettatrani.it','trani-barletta-andria.it','tranibarlettaandria.it','barletta-trani-andria.it','barlettatraniandria.it','andria-trani-barletta.it','andriatranibarletta.it','trani-andria-barletta.it','traniandriabarletta.it','bt.it','belluno.it','bl.it','benevento.it','bn.it','bergamo.it','bg.it','biella.it','bi.it','bologna.it','bo.it','bolzano.it','bozen.it','balsan.it','alto-adige.it','altoadige.it','suedtirol.it','bz.it','brescia.it','bs.it','brindisi.it','br.it','cagliari.it','ca.it','caltanissetta.it','cl.it','campobasso.it','cb.it','carboniaiglesias.it','carbonia-iglesias.it','iglesias-carbonia.it','iglesiascarbonia.it',
                'ci.it','caserta.it','ce.it','catania.it','ct.it','catanzaro.it','cz.it','chieti.it','ch.it','como.it','co.it','cosenza.it','cs.it','cremona.it','cr.it','crotone.it','kr.it','cuneo.it','cn.it','dell-ogliastra.it','dellogliastra.it','ogliastra.it','og.it','enna.it','en.it','ferrara.it','fe.it','fermo.it','fm.it','firenze.it','florence.it','fi.it','foggia.it','fg.it','forli-cesena.it','forlicesena.it','cesena-forli.it','cesenaforli.it','fc.it','frosinone.it','fr.it','genova.it','genoa.it','ge.it','gorizia.it','go.it','grosseto.it','gr.it','imperia.it','im.it','isernia.it','is.it','laquila.it','aquila.it','aq.it','la-spezia.it','laspezia.it','sp.it','latina.it','lt.it','lecce.it','le.it','lecco.it','lc.it','livorno.it','li.it',
                'lodi.it','lo.it','lucca.it','lu.it','macerata.it','mc.it','mantova.it','mn.it','massa-carrara.it','massacarrara.it','carrara-massa.it','carraramassa.it','ms.it','matera.it','mt.it','medio-campidano.it','mediocampidano.it','campidano-medio.it','campidanomedio.it','vs.it','messina.it','me.it','milano.it','milan.it','mi.it','modena.it','mo.it','monza.it','monza-brianza.it','monzabrianza.it','monzaebrianza.it','monzaedellabrianza.it','monza-e-della-brianza.it','mb.it','napoli.it','naples.it','na.it','novara.it','no.it','nuoro.it','nu.it','oristano.it','or.it','padova.it','padua.it','pd.it','palermo.it','pa.it','parma.it','pr.it','pavia.it','pv.it','perugia.it','pg.it','pescara.it','pe.it','pesaro-urbino.it','pesarourbino.it','urbino-pesaro.it','urbinopesaro.it','pu.it','piacenza.it','pc.it','pisa.it','pi.it','pistoia.it','pt.it','pordenone.it','pn.it','potenza.it','pz.it','prato.it','po.it','ragusa.it','rg.it','ravenna.it','ra.it','reggio-calabria.it',
                'reggiocalabria.it','rc.it','reggio-emilia.it','reggioemilia.it','re.it','rieti.it','ri.it','rimini.it','rn.it','roma.it','rome.it','rm.it','rovigo.it','ro.it','salerno.it','sa.it','sassari.it','ss.it','savona.it','sv.it','siena.it','si.it','siracusa.it','sr.it','sondrio.it','so.it','taranto.it','ta.it','tempio-olbia.it','tempioolbia.it','olbia-tempio.it','olbiatempio.it','ot.it','teramo.it','te.it','terni.it','tr.it','torino.it','turin.it','to.it','trapani.it','tp.it','trento.it','trentino.it','tn.it','treviso.it','tv.it','trieste.it','ts.it','udine.it','ud.it','varese.it','va.it','venezia.it','venice.it','ve.it','verbania.it','vb.it','vercelli.it','vc.it','verona.it','vr.it','vibo-valentia.it','vibovalentia.it','vv.it','vicenza.it','vi.it','viterbo.it','vt.it','je','co.je','org.je','net.je','sch.je','gov.je','*.jm','jo','com.jo','org.jo','net.jo','edu.jo','sch.jo','gov.jo','mil.jo','name.jo','jobs','jp','ac.jp','ad.jp','co.jp','ed.jp','go.jp','gr.jp','lg.jp','ne.jp','or.jp','*.aichi.jp','*.akita.jp','*.aomori.jp','*.chiba.jp','*.ehime.jp','*.fukui.jp','*.fukuoka.jp','*.fukushima.jp','*.gifu.jp','*.gunma.jp','*.hiroshima.jp','*.hokkaido.jp','*.hyogo.jp','*.ibaraki.jp','*.ishikawa.jp','*.iwate.jp','*.kagawa.jp','*.kagoshima.jp','*.kanagawa.jp','*.kawasaki.jp','*.kitakyushu.jp','*.kobe.jp','*.kochi.jp','*.kumamoto.jp','*.kyoto.jp','*.mie.jp','*.miyagi.jp','*.miyazaki.jp','*.nagano.jp','*.nagasaki.jp','*.nagoya.jp','*.nara.jp','*.niigata.jp','*.oita.jp','*.okayama.jp','*.okinawa.jp','*.osaka.jp','*.saga.jp','*.saitama.jp','*.sapporo.jp','*.sendai.jp','*.shiga.jp','*.shimane.jp','*.shizuoka.jp','*.tochigi.jp','*.tokushima.jp','*.tokyo.jp','*.tottori.jp','*.toyama.jp','*.wakayama.jp','*.yamagata.jp','*.yamaguchi.jp','*.yamanashi.jp','*.yokohama.jp','!metro.tokyo.jp','!pref.aichi.jp','!pref.akita.jp','!pref.aomori.jp','!pref.chiba.jp','!pref.ehime.jp','!pref.fukui.jp','!pref.fukuoka.jp','!pref.fukushima.jp','!pref.gifu.jp','!pref.gunma.jp','!pref.hiroshima.jp','!pref.hokkaido.jp','!pref.hyogo.jp','!pref.ibaraki.jp','!pref.ishikawa.jp','!pref.iwate.jp','!pref.kagawa.jp','!pref.kagoshima.jp','!pref.kanagawa.jp','!pref.kochi.jp','!pref.kumamoto.jp','!pref.kyoto.jp','!pref.mie.jp','!pref.miyagi.jp','!pref.miyazaki.jp','!pref.nagano.jp','!pref.nagasaki.jp','!pref.nara.jp','!pref.niigata.jp','!pref.oita.jp',
                '!pref.okayama.jp','!pref.okinawa.jp','!pref.osaka.jp','!pref.saga.jp','!pref.saitama.jp','!pref.shiga.jp','!pref.shimane.jp','!pref.shizuoka.jp','!pref.tochigi.jp','!pref.tokushima.jp','!pref.tottori.jp','!pref.toyama.jp','!pref.wakayama.jp','!pref.yamagata.jp','!pref.yamaguchi.jp','!pref.yamanashi.jp','!city.chiba.jp','!city.fukuoka.jp','!city.hiroshima.jp','!city.kawasaki.jp','!city.kitakyushu.jp','!city.kobe.jp','!city.kyoto.jp','!city.nagoya.jp','!city.niigata.jp','!city.okayama.jp','!city.osaka.jp','!city.saitama.jp','!city.sapporo.jp','!city.sendai.jp','!city.shizuoka.jp','!city.yokohama.jp','*.ke','kg','org.kg','net.kg','com.kg','edu.kg','gov.kg','mil.kg','*.kh','ki','edu.ki','biz.ki','net.ki','org.ki','gov.ki','info.ki','com.ki','km','org.km','nom.km','gov.km','prd.km','tm.km','edu.km','mil.km','ass.km','com.km','coop.km','asso.km','presse.km','medecin.km','notaires.km','pharmaciens.km','veterinaire.km','gouv.km','kn','net.kn','org.kn','edu.kn','gov.kn','com.kp','edu.kp','gov.kp','org.kp','rep.kp','tra.kp','kr','ac.kr','co.kr','es.kr','go.kr','hs.kr','kg.kr','mil.kr','ms.kr','ne.kr','or.kr','pe.kr','re.kr','sc.kr','busan.kr','chungbuk.kr','chungnam.kr','daegu.kr','daejeon.kr','gangwon.kr','gwangju.kr','gyeongbuk.kr','gyeonggi.kr','gyeongnam.kr','incheon.kr','jeju.kr','jeonbuk.kr','jeonnam.kr','seoul.kr','ulsan.kr','*.kw','ky','edu.ky','gov.ky','com.ky','org.ky','net.ky','kz','org.kz','edu.kz','net.kz','gov.kz','mil.kz','com.kz','la','int.la','net.la','info.la','edu.la','gov.la','per.la','com.la','org.la','com.lb','edu.lb','gov.lb','net.lb','org.lb','lc','com.lc','net.lc','co.lc','org.lc','edu.lc','gov.lc','li','lk','gov.lk','sch.lk','net.lk','int.lk','com.lk','org.lk','edu.lk','ngo.lk','soc.lk','web.lk','ltd.lk','assn.lk','grp.lk','hotel.lk','com.lr','edu.lr','gov.lr','org.lr','net.lr','ls','co.ls','org.ls','lt','gov.lt','lu','lv','com.lv','edu.lv','gov.lv','org.lv','mil.lv','id.lv','net.lv','asn.lv','conf.lv','ly','com.ly','net.ly','gov.ly','plc.ly','edu.ly','sch.ly','med.ly','org.ly','id.ly','ma','co.ma','net.ma','gov.ma','org.ma','ac.ma','press.ma','mc','tm.mc','asso.mc','md','me','co.me','net.me','org.me','edu.me','ac.me','gov.me','its.me','priv.me','mg','org.mg','nom.mg','gov.mg','prd.mg','tm.mg','edu.mg','mil.mg','com.mg','mh','mil','mk','com.mk','org.mk','net.mk','edu.mk','gov.mk','inf.mk','name.mk','ml','com.ml','edu.ml','gouv.ml','gov.ml','net.ml','org.ml','presse.ml','*.mm','mn','gov.mn','edu.mn','org.mn','mo','com.mo','net.mo','org.mo','edu.mo','gov.mo','mobi','mp','mq','mr','gov.mr','ms','*.mt','mu','com.mu','net.mu','org.mu','gov.mu','ac.mu','co.mu','or.mu','museum','academy.museum','agriculture.museum','air.museum','airguard.museum','alabama.museum','alaska.museum','amber.museum','ambulance.museum','american.museum','americana.museum','americanantiques.museum','americanart.museum','amsterdam.museum','and.museum','annefrank.museum','anthro.museum','anthropology.museum','antiques.museum','aquarium.museum','arboretum.museum','archaeological.museum','archaeology.museum','architecture.museum','art.museum','artanddesign.museum','artcenter.museum',
                'artdeco.museum','arteducation.museum','artgallery.museum','arts.museum','artsandcrafts.museum','asmatart.museum','assassination.museum','assisi.museum','association.museum','astronomy.museum','atlanta.museum','austin.museum','australia.museum','automotive.museum','aviation.museum','axis.museum','badajoz.museum','baghdad.museum','bahn.museum','bale.museum','baltimore.museum','barcelona.museum','baseball.museum','basel.museum','baths.museum','bauern.museum','beauxarts.museum','beeldengeluid.museum','bellevue.museum','bergbau.museum','berkeley.museum','berlin.museum','bern.museum','bible.museum','bilbao.museum','bill.museum','birdart.museum','birthplace.museum','bonn.museum','boston.museum','botanical.museum','botanicalgarden.museum','botanicgarden.museum','botany.museum','brandywinevalley.museum','brasil.museum','bristol.museum','british.museum','britishcolumbia.museum','broadcast.museum','brunel.museum','brussel.museum','brussels.museum','bruxelles.museum','building.museum','burghof.museum','bus.museum','bushey.museum','cadaques.museum','california.museum','cambridge.museum','can.museum','canada.museum','capebreton.museum','carrier.museum','cartoonart.museum','casadelamoneda.museum','castle.museum','castres.museum','celtic.museum','center.museum','chattanooga.museum','cheltenham.museum','chesapeakebay.museum','chicago.museum','children.museum','childrens.museum','childrensgarden.museum','chiropractic.museum','chocolate.museum','christiansburg.museum','cincinnati.museum','cinema.museum','circus.museum','civilisation.museum','civilization.museum','civilwar.museum','clinton.museum','clock.museum','coal.museum','coastaldefence.museum','cody.museum','coldwar.museum','collection.museum','colonialwilliamsburg.museum','coloradoplateau.museum','columbia.museum','columbus.museum','communication.museum','communications.museum','community.museum','computer.museum','computerhistory.museum','contemporary.museum','contemporaryart.museum','convent.museum','copenhagen.museum','corporation.museum','corvette.museum','costume.museum','countryestate.museum','county.museum','crafts.museum','cranbrook.museum','creation.museum','cultural.museum','culturalcenter.museum','culture.museum','cyber.museum','cymru.museum','dali.museum','dallas.museum','database.museum','ddr.museum','decorativearts.museum','delaware.museum','delmenhorst.museum','denmark.museum','depot.museum','design.museum','detroit.museum','dinosaur.museum','discovery.museum','dolls.museum','donostia.museum','durham.museum','eastafrica.museum','eastcoast.museum','education.museum','educational.museum','egyptian.museum','eisenbahn.museum','elburg.museum','elvendrell.museum','embroidery.museum','encyclopedic.museum','england.museum','entomology.museum','environment.museum','environmentalconservation.museum','epilepsy.museum','essex.museum','estate.museum','ethnology.museum','exeter.museum','exhibition.museum','family.museum','farm.museum','farmequipment.museum','farmers.museum','farmstead.museum','field.museum','figueres.museum','filatelia.museum','film.museum','fineart.museum','finearts.museum','finland.museum','flanders.museum','florida.museum','force.museum','fortmissoula.museum','fortworth.museum','foundation.museum','francaise.museum','frankfurt.museum','franziskaner.museum','freemasonry.museum','freiburg.museum','fribourg.museum','frog.museum','fundacio.museum','furniture.museum','gallery.museum','garden.museum','gateway.museum','geelvinck.museum','gemological.museum','geology.museum','georgia.museum','giessen.museum','glas.museum','glass.museum','gorge.museum','grandrapids.museum','graz.museum','guernsey.museum','halloffame.museum','hamburg.museum','handson.museum','harvestcelebration.museum','hawaii.museum','health.museum','heimatunduhren.museum','hellas.museum','helsinki.museum','hembygdsforbund.museum','heritage.museum','histoire.museum','historical.museum','historicalsociety.museum','historichouses.museum','historisch.museum','historisches.museum','history.museum','historyofscience.museum','horology.museum','house.museum','humanities.museum','illustration.museum','imageandsound.museum','indian.museum','indiana.museum','indianapolis.museum','indianmarket.museum','intelligence.museum','interactive.museum','iraq.museum','iron.museum','isleofman.museum','jamison.museum','jefferson.museum','jerusalem.museum','jewelry.museum','jewish.museum','jewishart.museum','jfk.museum','journalism.museum','judaica.museum','judygarland.museum','juedisches.museum','juif.museum','karate.museum','karikatur.museum','kids.museum','koebenhavn.museum','koeln.museum','kunst.museum','kunstsammlung.museum','kunstunddesign.museum','labor.museum','labour.museum','lajolla.museum','lancashire.museum','landes.museum','lans.museum','larsson.museum','lewismiller.museum','lincoln.museum','linz.museum','living.museum','livinghistory.museum','localhistory.museum','london.museum','losangeles.museum','louvre.museum','loyalist.museum','lucerne.museum','luxembourg.museum','luzern.museum','mad.museum','madrid.museum','mallorca.museum','manchester.museum','mansion.museum','mansions.museum','manx.museum','marburg.museum','maritime.museum','maritimo.museum','maryland.museum','marylhurst.museum','media.museum','medical.museum','medizinhistorisches.museum',
                'meeres.museum','memorial.museum','mesaverde.museum','michigan.museum','midatlantic.museum','military.museum','mill.museum','miners.museum','mining.museum','minnesota.museum','missile.museum','missoula.museum','modern.museum','moma.museum','money.museum','monmouth.museum','monticello.museum','montreal.museum','moscow.museum','motorcycle.museum','muenchen.museum','muenster.museum','mulhouse.museum','muncie.museum','museet.museum','museumcenter.museum','museumvereniging.museum','music.museum','national.museum','nationalfirearms.museum','nationalheritage.museum','nativeamerican.museum','naturalhistory.museum','naturalhistorymuseum.museum','naturalsciences.museum','nature.museum','naturhistorisches.museum','natuurwetenschappen.museum','naumburg.museum','naval.museum','nebraska.museum','neues.museum','newhampshire.museum','newjersey.museum','newmexico.museum','newport.museum','newspaper.museum','newyork.museum','niepce.museum','norfolk.museum','north.museum','nrw.museum','nuernberg.museum','nuremberg.museum','nyc.museum','nyny.museum','oceanographic.museum','oceanographique.museum','omaha.museum','online.museum','ontario.museum','openair.museum','oregon.museum','oregontrail.museum','otago.museum','oxford.museum','pacific.museum','paderborn.museum','palace.museum','paleo.museum','palmsprings.museum','panama.museum','paris.museum','pasadena.museum','pharmacy.museum','philadelphia.museum','philadelphiaarea.museum','philately.museum','phoenix.museum','photography.museum','pilots.museum','pittsburgh.museum','planetarium.museum','plantation.museum','plants.museum','plaza.museum','portal.museum','portland.museum','portlligat.museum','posts-and-telecommunications.museum','preservation.museum','presidio.museum','press.museum','project.museum','public.museum','pubol.museum','quebec.museum','railroad.museum','railway.museum','research.museum','resistance.museum','riodejaneiro.museum','rochester.museum','rockart.museum','roma.museum','russia.museum','saintlouis.museum','salem.museum','salvadordali.museum','salzburg.museum','sandiego.museum','sanfrancisco.museum','santabarbara.museum','santacruz.museum','santafe.museum','saskatchewan.museum','satx.museum','savannahga.museum','schlesisches.museum','schoenbrunn.museum','schokoladen.museum','school.museum','schweiz.museum','science.museum','scienceandhistory.museum','scienceandindustry.museum','sciencecenter.museum','sciencecenters.museum','science-fiction.museum','sciencehistory.museum','sciences.museum','sciencesnaturelles.museum','scotland.museum','seaport.museum','settlement.museum','settlers.museum',
                'shell.museum','sherbrooke.museum','sibenik.museum','silk.museum','ski.museum','skole.museum','society.museum','sologne.museum','soundandvision.museum','southcarolina.museum','southwest.museum','space.museum','spy.museum','square.museum','stadt.museum','stalbans.museum','starnberg.museum','state.museum','stateofdelaware.museum','station.museum','steam.museum','steiermark.museum','stjohn.museum','stockholm.museum','stpetersburg.museum','stuttgart.museum','suisse.museum','surgeonshall.museum','surrey.museum','svizzera.museum','sweden.museum','sydney.museum','tank.museum','tcm.museum','technology.museum','telekommunikation.museum','television.museum','texas.museum','textile.museum','theater.museum','time.museum','timekeeping.museum','topology.museum','torino.museum','touch.museum','town.museum','transport.museum','tree.museum','trolley.museum','trust.museum','trustee.museum','uhren.museum','ulm.museum','undersea.museum','university.museum','usa.museum','usantiques.museum','usarts.museum','uscountryestate.museum','usculture.museum','usdecorativearts.museum','usgarden.museum','ushistory.museum','ushuaia.museum','uslivinghistory.museum','utah.museum','uvic.museum','valley.museum','vantaa.museum','versailles.museum','viking.museum','village.museum','virginia.museum','virtual.museum','virtuel.museum','vlaanderen.museum','volkenkunde.museum','wales.museum','wallonie.museum','war.museum','washingtondc.museum','watchandclock.museum','watch-and-clock.museum','western.museum','westfalen.museum','whaling.museum','wildlife.museum','williamsburg.museum','windmill.museum','workshop.museum','york.museum','yorkshire.museum','yosemite.museum','youth.museum','zoological.museum','zoology.museum','mv','aero.mv','biz.mv','com.mv','coop.mv','edu.mv','gov.mv','info.mv','int.mv','mil.mv','museum.mv','name.mv','net.mv','org.mv','pro.mv','mw','ac.mw','biz.mw','co.mw','com.mw','coop.mw','edu.mw','gov.mw','int.mw','museum.mw','net.mw','org.mw','mx','com.mx','org.mx','gob.mx','edu.mx','net.mx','my','com.my','net.my','org.my','gov.my','edu.my','mil.my','name.my','*.mz','na','info.na','pro.na','name.na','school.na','or.na','dr.na','us.na','mx.na','ca.na','in.na','cc.na','tv.na','ws.na','mobi.na','co.na','com.na','org.na','name','nc','asso.nc','ne','net','nf','com.nf','net.nf','per.nf','rec.nf','web.nf','arts.nf','firm.nf','info.nf','other.nf','store.nf','ac.ng','com.ng','edu.ng','gov.ng','net.ng','org.ng','*.ni','nl','bv.nl','no','fhs.no','vgs.no','fylkesbibl.no','folkebibl.no','museum.no','idrett.no','priv.no','mil.no','stat.no','dep.no','kommune.no','herad.no','aa.no','ah.no','bu.no','fm.no','hl.no','hm.no','jan-mayen.no','mr.no','nl.no','nt.no','of.no','ol.no','oslo.no','rl.no','sf.no','st.no','svalbard.no','tm.no','tr.no','va.no','vf.no','gs.aa.no','gs.ah.no','gs.bu.no','gs.fm.no','gs.hl.no','gs.hm.no','gs.jan-mayen.no',
                'gs.mr.no','gs.nl.no','gs.nt.no','gs.of.no','gs.ol.no','gs.oslo.no','gs.rl.no','gs.sf.no','gs.st.no','gs.svalbard.no','gs.tm.no','gs.tr.no','gs.va.no','gs.vf.no','akrehamn.no','algard.no','arna.no','brumunddal.no','bryne.no','bronnoysund.no','drobak.no','egersund.no','fetsund.no','floro.no','fredrikstad.no','hokksund.no','honefoss.no','jessheim.no','jorpeland.no','kirkenes.no','kopervik.no','krokstadelva.no','langevag.no','leirvik.no','mjondalen.no','mo-i-rana.no','mosjoen.no','nesoddtangen.no','orkanger.no','osoyro.no','raholt.no','sandnessjoen.no','skedsmokorset.no','slattum.no','spjelkavik.no','stathelle.no','stavern.no','stjordalshalsen.no','tananger.no','tranby.no','vossevangen.no','afjord.no','agdenes.no','al.no','alesund.no','alstahaug.no','alta.no','alaheadju.no','alvdal.no','amli.no','amot.no','andebu.no','andoy.no','andasuolo.no','ardal.no','aremark.no','arendal.no','aseral.no','asker.no','askim.no','askvoll.no','askoy.no','asnes.no','audnedaln.no','aukra.no','aure.no','aurland.no','aurskog-holand.no','austevoll.no','austrheim.no','averoy.no','balestrand.no','ballangen.no','balat.no','balsfjord.no','bahccavuotna.no','bamble.no','bardu.no','beardu.no','beiarn.no','bajddar.no','baidar.no','berg.no','bergen.no','berlevag.no','bearalvahki.no','bindal.no','birkenes.no','bjarkoy.no','bjerkreim.no','bjugn.no','bodo.no','badaddja.no','budejju.no','bokn.no','bremanger.no','bronnoy.no','bygland.no','bykle.no','barum.no','bo.telemark.no','bo.nordland.no','bievat.no','bomlo.no','batsfjord.no','bahcavuotna.no','dovre.no',
                'drammen.no','drangedal.no','dyroy.no','donna.no','eid.no','eidfjord.no','eidsberg.no','eidskog.no','eidsvoll.no','eigersund.no','elverum.no','enebakk.no','engerdal.no','etne.no','etnedal.no','evenes.no','evenassi.no','evje-og-hornnes.no','farsund.no','fauske.no','fuossko.no','fuoisku.no','fedje.no','fet.no','finnoy.no','fitjar.no','fjaler.no','fjell.no','flakstad.no','flatanger.no','flekkefjord.no','flesberg.no','flora.no','fla.no','folldal.no','forsand.no','fosnes.no','frei.no','frogn.no','froland.no','frosta.no','frana.no','froya.no','fusa.no','fyresdal.no','forde.no','gamvik.no','gangaviika.no','gaular.no','gausdal.no','gildeskal.no','giske.no','gjemnes.no','gjerdrum.no','gjerstad.no','gjesdal.no','gjovik.no','gloppen.no','gol.no','gran.no','grane.no','granvin.no','gratangen.no','grimstad.no','grong.no','kraanghke.no','grue.no','gulen.no','hadsel.no','halden.no','halsa.no','hamar.no','hamaroy.no','habmer.no','hapmir.no','hammerfest.no','hammarfeasta.no','haram.no','hareid.no','harstad.no','hasvik.no','aknoluokta.no','hattfjelldal.no','aarborte.no','haugesund.no','hemne.no','hemnes.no','hemsedal.no','heroy.more-og-romsdal.no','heroy.nordland.no','hitra.no','hjartdal.no','hjelmeland.no','hobol.no','hof.no','hol.no','hole.no','holmestrand.no','holtalen.no','hornindal.no','horten.no','hurdal.no','hurum.no','hvaler.no','hyllestad.no','hagebostad.no','hoyanger.no','hoylandet.no','ha.no','ibestad.no','inderoy.no','iveland.no','jevnaker.no','jondal.no','jolster.no','karasjok.no','karasjohka.no','karlsoy.no','galsa.no','karmoy.no','kautokeino.no','guovdageaidnu.no','klepp.no','klabu.no','kongsberg.no','kongsvinger.no','kragero.no','kristiansand.no','kristiansund.no','krodsherad.no','kvalsund.no','rahkkeravju.no','kvam.no','kvinesdal.no','kvinnherad.no','kviteseid.no','kvitsoy.no','kvafjord.no','giehtavuoatna.no','kvanangen.no','navuotna.no','kafjord.no','gaivuotna.no','larvik.no','lavangen.no','lavagis.no','loabat.no','lebesby.no','davvesiida.no','leikanger.no','leirfjord.no','leka.no','leksvik.no','lenvik.no','leangaviika.no','lesja.no','levanger.no','lier.no','lierne.no','lillehammer.no','lillesand.no','lindesnes.no','lindas.no','lom.no','loppa.no','lahppi.no','lund.no','lunner.no','luroy.no','luster.no','lyngdal.no','lyngen.no','ivgu.no','lardal.no','lerdal.no','lodingen.no','lorenskog.no','loten.no','malvik.no','masoy.no','muosat.no','mandal.no','marker.no','marnardal.no','masfjorden.no','meland.no','meldal.no','melhus.no','meloy.no','meraker.no','moareke.no','midsund.no','midtre-gauldal.no','modalen.no','modum.no','molde.no','moskenes.no','moss.no','mosvik.no','malselv.no','malatvuopmi.no','namdalseid.no','aejrie.no','namsos.no','namsskogan.no','naamesjevuemie.no','laakesvuemie.no','nannestad.no','narvik.no','narviika.no','naustdal.no','nedre-eiker.no','nes.akershus.no','nes.buskerud.no','nesna.no','nesodden.no','nesseby.no','unjarga.no','nesset.no','nissedal.no','nittedal.no','nord-aurdal.no','nord-fron.no','nord-odal.no','norddal.no','nordkapp.no','davvenjarga.no','nordre-land.no','nordreisa.no','raisa.no','nore-og-uvdal.no','notodden.no','naroy.no','notteroy.no','odda.no','oksnes.no','oppdal.no','oppegard.no','orkdal.no','orland.no','orskog.no','orsta.no','os.hedmark.no','os.hordaland.no','osen.no','osteroy.no','ostre-toten.no','overhalla.no','ovre-eiker.no','oyer.no','oygarden.no','oystre-slidre.no','porsanger.no','porsangu.no','porsgrunn.no','radoy.no','rakkestad.no','rana.no','ruovat.no','randaberg.no','rauma.no','rendalen.no','rennebu.no','rennesoy.no','rindal.no','ringebu.no','ringerike.no','ringsaker.no','rissa.no',
                'risor.no','roan.no','rollag.no','rygge.no','ralingen.no','rodoy.no','romskog.no','roros.no','rost.no','royken.no','royrvik.no','rade.no','salangen.no','siellak.no','saltdal.no','salat.no','samnanger.no','sande.more-og-romsdal.no','sande.vestfold.no','sandefjord.no','sandnes.no','sandoy.no','sarpsborg.no','sauda.no','sauherad.no','sel.no','selbu.no','selje.no','seljord.no','sigdal.no','siljan.no','sirdal.no','skaun.no','skedsmo.no','ski.no','skien.no','skiptvet.no','skjervoy.no','skierva.no','skjak.no','skodje.no','skanland.no','skanit.no','smola.no','snillfjord.no','snasa.no','snoasa.no','snaase.no','sogndal.no','sokndal.no','sola.no','solund.no','songdalen.no','sortland.no','spydeberg.no','stange.no','stavanger.no','steigen.no','steinkjer.no','stjordal.no','stokke.no','stor-elvdal.no','stord.no','stordal.no','storfjord.no','omasvuotna.no','strand.no','stranda.no','stryn.no','sula.no','suldal.no','sund.no','sunndal.no','surnadal.no','sveio.no','svelvik.no','sykkylven.no','sogne.no','somna.no','sondre-land.no','sor-aurdal.no','sor-fron.no','sor-odal.no','sor-varanger.no','matta-varjjat.no','sorfold.no','sorreisa.no','sorum.no','tana.no','deatnu.no','time.no','tingvoll.no','tinn.no','tjeldsund.no','dielddanuorri.no','tjome.no','tokke.no','tolga.no','torsken.no','tranoy.no','tromso.no','tromsa.no','romsa.no','trondheim.no','troandin.no','trysil.no','trana.no','trogstad.no','tvedestrand.no','tydal.no','tynset.no','tysfjord.no','divtasvuodna.no','divttasvuotna.no','tysnes.no','tysvar.no','tonsberg.no','ullensaker.no','ullensvang.no','ulvik.no','utsira.no','vadso.no','cahcesuolo.no','vaksdal.no','valle.no','vang.no','vanylven.no','vardo.no','varggat.no','vefsn.no','vaapste.no','vega.no','vegarshei.no','vennesla.no','verdal.no','verran.no','vestby.no','vestnes.no','vestre-slidre.no','vestre-toten.no','vestvagoy.no','vevelstad.no','vik.no','vikna.no','vindafjord.no','volda.no','voss.no','varoy.no','vagan.no','voagat.no','vagsoy.no','vaga.no','valer.ostfold.no','valer.hedmark.no','*.np','nr','biz.nr','info.nr','gov.nr','edu.nr','org.nr','net.nr','com.nr','nu','*.nz','*.om','!mediaphone.om','!nawrastelecom.om','!nawras.om','!omanmobile.om','!omanpost.om','!omantel.om','!rakpetroleum.om','!siemens.om','!songfest.om','!statecouncil.om','org','pa','ac.pa','gob.pa','com.pa','org.pa','sld.pa','edu.pa','net.pa','ing.pa','abo.pa','med.pa','nom.pa','pe','edu.pe','gob.pe','nom.pe','mil.pe','org.pe','com.pe','net.pe','pf','com.pf','org.pf','edu.pf','*.pg','ph','com.ph','net.ph','org.ph','gov.ph','edu.ph','ngo.ph','mil.ph','i.ph','pk','com.pk','net.pk','edu.pk','org.pk','fam.pk','biz.pk','web.pk','gov.pk','gob.pk','gok.pk','gon.pk','gop.pk','gos.pk','info.pk','pl','aid.pl','agro.pl','atm.pl','auto.pl','biz.pl','com.pl','edu.pl','gmina.pl','gsm.pl','info.pl','mail.pl','miasta.pl','media.pl','mil.pl','net.pl','nieruchomosci.pl','nom.pl','org.pl','pc.pl','powiat.pl','priv.pl','realestate.pl','rel.pl','sex.pl','shop.pl','sklep.pl','sos.pl','szkola.pl','targi.pl','tm.pl','tourism.pl','travel.pl','turystyka.pl','6bone.pl','art.pl','mbone.pl','gov.pl','uw.gov.pl','um.gov.pl','ug.gov.pl','upow.gov.pl','starostwo.gov.pl','so.gov.pl','sr.gov.pl','po.gov.pl','pa.gov.pl','ngo.pl','irc.pl','usenet.pl','augustow.pl','babia-gora.pl','bedzin.pl','beskidy.pl','bialowieza.pl','bialystok.pl','bielawa.pl','bieszczady.pl','boleslawiec.pl','bydgoszcz.pl','bytom.pl','cieszyn.pl','czeladz.pl','czest.pl','dlugoleka.pl','elblag.pl','elk.pl','glogow.pl','gniezno.pl','gorlice.pl','grajewo.pl','ilawa.pl','jaworzno.pl','jelenia-gora.pl','jgora.pl','kalisz.pl','kazimierz-dolny.pl','karpacz.pl','kartuzy.pl','kaszuby.pl','katowice.pl','kepno.pl','ketrzyn.pl','klodzko.pl','kobierzyce.pl','kolobrzeg.pl','konin.pl','konskowola.pl','kutno.pl','lapy.pl','lebork.pl','legnica.pl','lezajsk.pl','limanowa.pl','lomza.pl','lowicz.pl','lubin.pl','lukow.pl','malbork.pl','malopolska.pl','mazowsze.pl','mazury.pl','mielec.pl','mielno.pl','mragowo.pl','naklo.pl','nowaruda.pl','nysa.pl','olawa.pl','olecko.pl','olkusz.pl','olsztyn.pl','opoczno.pl','opole.pl','ostroda.pl','ostroleka.pl','ostrowiec.pl','ostrowwlkp.pl','pila.pl','pisz.pl','podhale.pl','podlasie.pl','polkowice.pl','pomorze.pl','pomorskie.pl','prochowice.pl','pruszkow.pl','przeworsk.pl','pulawy.pl','radom.pl','rawa-maz.pl','rybnik.pl','rzeszow.pl','sanok.pl','sejny.pl','siedlce.pl','slask.pl','slupsk.pl','sosnowiec.pl','stalowa-wola.pl','skoczow.pl','starachowice.pl','stargard.pl','suwalki.pl','swidnica.pl','swiebodzin.pl','swinoujscie.pl','szczecin.pl','szczytno.pl','tarnobrzeg.pl','tgory.pl','turek.pl','tychy.pl','ustka.pl','walbrzych.pl','warmia.pl','warszawa.pl','waw.pl','wegrow.pl','wielun.pl','wlocl.pl','wloclawek.pl','wodzislaw.pl','wolomin.pl','wroclaw.pl','zachpomor.pl','zagan.pl','zarow.pl','zgora.pl','zgorzelec.pl','gda.pl','gdansk.pl','gdynia.pl','med.pl','sopot.pl','gliwice.pl','krakow.pl','poznan.pl','wroc.pl','zakopane.pl','pn','gov.pn','co.pn','org.pn','edu.pn','net.pn','pr','com.pr','net.pr','org.pr','gov.pr','edu.pr','isla.pr','pro.pr','biz.pr','info.pr','name.pr','est.pr','prof.pr','ac.pr','pro','aca.pro','bar.pro','cpa.pro','jur.pro','law.pro','med.pro','eng.pro','ps','edu.ps','gov.ps','sec.ps','plo.ps','com.ps','org.ps','net.ps','pt','net.pt','gov.pt','org.pt','edu.pt','int.pt','publ.pt','com.pt','nome.pt','pw','co.pw','ne.pw','or.pw','ed.pw','go.pw','belau.pw','*.py','qa','com.qa','edu.qa','gov.qa','mil.qa','name.qa','net.qa','org.qa','sch.qa','re','com.re','asso.re','nom.re','ro','com.ro','org.ro','tm.ro','nt.ro','nom.ro','info.ro','rec.ro','arts.ro','firm.ro','store.ro','www.ro','rs','co.rs','org.rs','edu.rs','ac.rs','gov.rs','in.rs','ru','ac.ru','com.ru','edu.ru','int.ru','net.ru','org.ru','pp.ru','adygeya.ru','altai.ru','amur.ru','arkhangelsk.ru','astrakhan.ru','bashkiria.ru','belgorod.ru','bir.ru','bryansk.ru','buryatia.ru','cbg.ru','chel.ru','chelyabinsk.ru','chita.ru','chukotka.ru','chuvashia.ru','dagestan.ru','dudinka.ru','e-burg.ru','grozny.ru','irkutsk.ru','ivanovo.ru','izhevsk.ru','jar.ru','joshkar-ola.ru','kalmykia.ru','kaluga.ru','kamchatka.ru','karelia.ru','kazan.ru','kchr.ru','kemerovo.ru','khabarovsk.ru','khakassia.ru','khv.ru','kirov.ru','koenig.ru','komi.ru','kostroma.ru','krasnoyarsk.ru','kuban.ru','kurgan.ru','kursk.ru','lipetsk.ru','magadan.ru','mari.ru','mari-el.ru','marine.ru','mordovia.ru','mosreg.ru','msk.ru','murmansk.ru','nalchik.ru','nnov.ru','nov.ru','novosibirsk.ru','nsk.ru','omsk.ru','orenburg.ru','oryol.ru','palana.ru','penza.ru','perm.ru','pskov.ru','ptz.ru','rnd.ru','ryazan.ru','sakhalin.ru','samara.ru','saratov.ru','simbirsk.ru','smolensk.ru','spb.ru','stavropol.ru','stv.ru','surgut.ru','tambov.ru','tatarstan.ru','tom.ru','tomsk.ru','tsaritsyn.ru','tsk.ru','tula.ru','tuva.ru','tver.ru','tyumen.ru','udm.ru','udmurtia.ru','ulan-ude.ru','vladikavkaz.ru','vladimir.ru','vladivostok.ru','volgograd.ru','vologda.ru','voronezh.ru','vrn.ru','vyatka.ru','yakutia.ru','yamal.ru','yaroslavl.ru','yekaterinburg.ru','yuzhno-sakhalinsk.ru','amursk.ru','baikal.ru','cmw.ru','fareast.ru','jamal.ru','kms.ru','k-uralsk.ru','kustanai.ru','kuzbass.ru','magnitka.ru','mytis.ru',
                'nakhodka.ru','nkz.ru','norilsk.ru','oskol.ru','pyatigorsk.ru','rubtsovsk.ru','snz.ru','syzran.ru','vdonsk.ru','zgrad.ru','gov.ru','mil.ru','test.ru','rw','gov.rw','net.rw','edu.rw','ac.rw','com.rw','co.rw','int.rw','mil.rw','gouv.rw','sa','com.sa','net.sa','org.sa','gov.sa','med.sa','pub.sa','edu.sa','sch.sa','sb','com.sb','edu.sb','gov.sb','net.sb','org.sb','sc','com.sc','gov.sc','net.sc','org.sc','edu.sc','sd','com.sd','net.sd','org.sd','edu.sd','med.sd','gov.sd','info.sd','se','a.se','ac.se','b.se','bd.se','brand.se','c.se','d.se','e.se','f.se','fh.se','fhsk.se','fhv.se','g.se','h.se','i.se','k.se','komforb.se','kommunalforbund.se','komvux.se','l.se','lanbib.se','m.se','n.se','naturbruksgymn.se','o.se','org.se','p.se','parti.se','pp.se','press.se','r.se','s.se','sshn.se','t.se','tm.se','u.se','w.se','x.se','y.se','z.se','sg','com.sg','net.sg','org.sg','gov.sg','edu.sg','per.sg','sh','si','sk','sl','com.sl','net.sl','edu.sl','gov.sl','org.sl','sm','sn','art.sn','com.sn','edu.sn','gouv.sn','org.sn','perso.sn','univ.sn','so','com.so','net.so','org.so','sr','st','co.st','com.st','consulado.st','edu.st','embaixada.st','gov.st','mil.st','net.st','org.st','principe.st','saotome.st','store.st','su','*.sv','sy','edu.sy','gov.sy','net.sy','mil.sy','com.sy','org.sy','sz','co.sz','ac.sz','org.sz','tc','td','tel','tf','tg','th','ac.th','co.th','go.th','in.th','mi.th','net.th','or.th','tj','ac.tj','biz.tj','co.tj','com.tj','edu.tj','go.tj','gov.tj','int.tj','mil.tj','name.tj','net.tj','nic.tj','org.tj','test.tj','web.tj','tk','tl','gov.tl','tm','tn','com.tn','ens.tn','fin.tn','gov.tn','ind.tn','intl.tn','nat.tn','net.tn','org.tn','info.tn','perso.tn','tourism.tn','edunet.tn','rnrt.tn','rns.tn','rnu.tn','mincom.tn','agrinet.tn','defense.tn','turen.tn','to','com.to','gov.to','net.to','org.to','edu.to','mil.to','*.tr','!nic.tr','gov.nc.tr','travel','tt','co.tt','com.tt',
                'org.tt','net.tt','biz.tt','info.tt','pro.tt','int.tt','coop.tt','jobs.tt','mobi.tt','travel.tt','museum.tt','aero.tt','name.tt','gov.tt','edu.tt','tv','tw','edu.tw','gov.tw','mil.tw','com.tw','net.tw','org.tw','idv.tw','game.tw','ebiz.tw','club.tw','ac.tz','co.tz','go.tz','mil.tz','ne.tz','or.tz','sc.tz','ua','com.ua','edu.ua','gov.ua','in.ua','net.ua','org.ua','cherkassy.ua','chernigov.ua','chernovtsy.ua','ck.ua','cn.ua','crimea.ua','cv.ua','dn.ua','dnepropetrovsk.ua','donetsk.ua','dp.ua','if.ua','ivano-frankivsk.ua','kh.ua','kharkov.ua','kherson.ua','khmelnitskiy.ua','kiev.ua','kirovograd.ua','km.ua','kr.ua','ks.ua','kv.ua','lg.ua','lugansk.ua','lutsk.ua','lviv.ua','mk.ua','nikolaev.ua','od.ua','odessa.ua','pl.ua','poltava.ua','rovno.ua','rv.ua','sebastopol.ua','sumy.ua','te.ua','ternopil.ua','uzhgorod.ua','vinnica.ua','vn.ua','zaporizhzhe.ua','zp.ua','zhitomir.ua','zt.ua','co.ua','pp.ua','ug','co.ug','ac.ug','sc.ug','go.ug','ne.ug','or.ug','*.uk','*.sch.uk','!bl.uk','!british-library.uk','!icnet.uk','!jet.uk','!mod.uk','!nel.uk','!nhs.uk','!nic.uk','!nls.uk','!national-library-scotland.uk','!parliament.uk','!police.uk','us','dni.us','fed.us','isa.us','kids.us','nsn.us','ak.us','al.us','ar.us','as.us','az.us','ca.us','co.us','ct.us','dc.us','de.us','fl.us','ga.us','gu.us','hi.us','ia.us','id.us','il.us','in.us','ks.us','ky.us','la.us','ma.us','md.us','me.us','mi.us','mn.us','mo.us','ms.us','mt.us','nc.us','nd.us','ne.us','nh.us','nj.us','nm.us','nv.us','ny.us','oh.us','ok.us','or.us','pa.us','pr.us','ri.us','sc.us','sd.us','tn.us','tx.us','ut.us','vi.us','vt.us','va.us','wa.us','wi.us','wv.us','wy.us','k12.ak.us','k12.al.us','k12.ar.us','k12.as.us','k12.az.us','k12.ca.us','k12.co.us','k12.ct.us','k12.dc.us','k12.de.us','k12.fl.us','k12.ga.us','k12.gu.us','k12.ia.us','k12.id.us','k12.il.us','k12.in.us','k12.ks.us','k12.ky.us','k12.la.us','k12.ma.us','k12.md.us','k12.me.us','k12.mi.us','k12.mn.us','k12.mo.us','k12.ms.us','k12.mt.us','k12.nc.us','k12.nd.us','k12.ne.us','k12.nh.us','k12.nj.us','k12.nm.us','k12.nv.us','k12.ny.us','k12.oh.us','k12.ok.us','k12.or.us','k12.pa.us','k12.pr.us','k12.ri.us','k12.sc.us','k12.sd.us','k12.tn.us','k12.tx.us','k12.ut.us','k12.vi.us','k12.vt.us','k12.va.us','k12.wa.us','k12.wi.us','k12.wv.us','k12.wy.us','cc.ak.us','cc.al.us','cc.ar.us','cc.as.us','cc.az.us','cc.ca.us','cc.co.us','cc.ct.us','cc.dc.us','cc.de.us','cc.fl.us','cc.ga.us','cc.gu.us','cc.hi.us','cc.ia.us','cc.id.us','cc.il.us','cc.in.us','cc.ks.us','cc.ky.us','cc.la.us','cc.ma.us','cc.md.us','cc.me.us','cc.mi.us','cc.mn.us','cc.mo.us','cc.ms.us','cc.mt.us','cc.nc.us','cc.nd.us','cc.ne.us','cc.nh.us','cc.nj.us','cc.nm.us','cc.nv.us','cc.ny.us','cc.oh.us','cc.ok.us','cc.or.us','cc.pa.us','cc.pr.us','cc.ri.us','cc.sc.us','cc.sd.us','cc.tn.us','cc.tx.us','cc.ut.us','cc.vi.us','cc.vt.us','cc.va.us','cc.wa.us','cc.wi.us','cc.wv.us',
                'cc.wy.us','lib.ak.us','lib.al.us','lib.ar.us','lib.as.us','lib.az.us','lib.ca.us','lib.co.us','lib.ct.us','lib.dc.us','lib.de.us','lib.fl.us','lib.ga.us','lib.gu.us','lib.hi.us','lib.ia.us','lib.id.us','lib.il.us','lib.in.us','lib.ks.us','lib.ky.us','lib.la.us','lib.ma.us','lib.md.us','lib.me.us','lib.mi.us','lib.mn.us','lib.mo.us','lib.ms.us','lib.mt.us','lib.nc.us','lib.nd.us','lib.ne.us','lib.nh.us','lib.nj.us','lib.nm.us','lib.nv.us','lib.ny.us','lib.oh.us','lib.ok.us','lib.or.us','lib.pa.us','lib.pr.us','lib.ri.us','lib.sc.us','lib.sd.us','lib.tn.us','lib.tx.us','lib.ut.us','lib.vi.us','lib.vt.us','lib.va.us','lib.wa.us','lib.wi.us','lib.wv.us','lib.wy.us','pvt.k12.ma.us','chtr.k12.ma.us','paroch.k12.ma.us','*.uy','uz','com.uz','co.uz','va','vc','com.vc','net.vc','org.vc','gov.vc','mil.vc','edu.vc','*.ve','vg','vi','co.vi','com.vi','k12.vi','net.vi','org.vi','vn','com.vn','net.vn','org.vn','edu.vn','gov.vn','int.vn','ac.vn','biz.vn','info.vn','name.vn','pro.vn','health.vn','vu','ws','com.ws','net.ws','org.ws','gov.ws','edu.ws','xxx','*.ye','*.za','*.zm','*.zw','biz.at','info.at','priv.at','co.ca','ar.com','br.com','cn.com','de.com','eu.com','gb.com','gr.com','hu.com','jpn.com','kr.com','no.com','qc.com','ru.com','sa.com','se.com','uk.com','us.com','uy.com','za.com','gb.net','jp.net','se.net','uk.net','ae.org','us.org','com.de','operaunite.com','appspot.com','iki.fi','c.la','za.net',
                'za.org','co.nl','co.no','co.pl','dyndns-at-home.com','dyndns-at-work.com','dyndns-blog.com','dyndns-free.com','dyndns-home.com','dyndns-ip.com','dyndns-mail.com','dyndns-office.com','dyndns-pics.com','dyndns-remote.com','dyndns-server.com','dyndns-web.com','dyndns-wiki.com','dyndns-work.com','dyndns.biz','dyndns.info','dyndns.org','dyndns.tv','at-band-camp.net','ath.cx','barrel-of-knowledge.info','barrell-of-knowledge.info','better-than.tv','blogdns.com','blogdns.net','blogdns.org','blogsite.org','boldlygoingnowhere.org','broke-it.net','buyshouses.net','cechire.com','dnsalias.com','dnsalias.net','dnsalias.org','dnsdojo.com','dnsdojo.net','dnsdojo.org','does-it.net','doesntexist.com','doesntexist.org','dontexist.com','dontexist.net','dontexist.org','doomdns.com','doomdns.org','dvrdns.org','dyn-o-saur.com','dynalias.com','dynalias.net','dynalias.org','dynathome.net','dyndns.ws','endofinternet.net','endofinternet.org','endoftheinternet.org','est-a-la-maison.com','est-a-la-masion.com','est-le-patron.com','est-mon-blogueur.com','for-better.biz','for-more.biz','for-our.info','for-some.biz','for-the.biz','forgot.her.name','forgot.his.name','from-ak.com','from-al.com','from-ar.com','from-az.net','from-ca.com','from-co.net','from-ct.com','from-dc.com','from-de.com','from-fl.com','from-ga.com','from-hi.com','from-ia.com','from-id.com','from-il.com','from-in.com','from-ks.com','from-ky.com','from-la.net','from-ma.com','from-md.com','from-me.org','from-mi.com','from-mn.com','from-mo.com','from-ms.com','from-mt.com','from-nc.com','from-nd.com','from-ne.com','from-nh.com','from-nj.com','from-nm.com','from-nv.com','from-ny.net','from-oh.com','from-ok.com','from-or.com','from-pa.com','from-pr.com','from-ri.com','from-sc.com','from-sd.com','from-tn.com','from-tx.com','from-ut.com','from-va.com','from-vt.com','from-wa.com','from-wi.com','from-wv.com','from-wy.com','ftpaccess.cc','fuettertdasnetz.de','game-host.org','game-server.cc','getmyip.com','gets-it.net','go.dyndns.org','gotdns.com','gotdns.org','groks-the.info','groks-this.info','ham-radio-op.net','here-for-more.info','hobby-site.com','hobby-site.org','home.dyndns.org','homedns.org','homeftp.net','homeftp.org','homeip.net','homelinux.com','homelinux.net','homelinux.org','homeunix.com','homeunix.net','homeunix.org','iamallama.com','in-the-band.net','is-a-anarchist.com','is-a-blogger.com','is-a-bookkeeper.com','is-a-bruinsfan.org','is-a-bulls-fan.com','is-a-candidate.org','is-a-caterer.com','is-a-celticsfan.org','is-a-chef.com','is-a-chef.net','is-a-chef.org','is-a-conservative.com','is-a-cpa.com','is-a-cubicle-slave.com','is-a-democrat.com','is-a-designer.com','is-a-doctor.com','is-a-financialadvisor.com','is-a-geek.com','is-a-geek.net','is-a-geek.org','is-a-green.com','is-a-guru.com','is-a-hard-worker.com','is-a-hunter.com','is-a-knight.org','is-a-landscaper.com','is-a-lawyer.com','is-a-liberal.com','is-a-libertarian.com','is-a-linux-user.org','is-a-llama.com','is-a-musician.com','is-a-nascarfan.com','is-a-nurse.com','is-a-painter.com','is-a-patsfan.org','is-a-personaltrainer.com','is-a-photographer.com','is-a-player.com','is-a-republican.com','is-a-rockstar.com','is-a-socialist.com','is-a-soxfan.org','is-a-student.com','is-a-teacher.com','is-a-techie.com','is-a-therapist.com','is-an-accountant.com','is-an-actor.com','is-an-actress.com','is-an-anarchist.com','is-an-artist.com','is-an-engineer.com','is-an-entertainer.com','is-by.us','is-certified.com','is-found.org','is-gone.com','is-into-anime.com','is-into-cars.com','is-into-cartoons.com','is-into-games.com','is-leet.com','is-lost.org','is-not-certified.com','is-saved.org','is-slick.com','is-uberleet.com','is-very-bad.org','is-very-evil.org','is-very-good.org','is-very-nice.org','is-very-sweet.org','is-with-theband.com','isa-geek.com','isa-geek.net','isa-geek.org','isa-hockeynut.com','issmarterthanyou.com','isteingeek.de','istmein.de','kicks-ass.net','kicks-ass.org','knowsitall.info','land-4-sale.us','lebtimnetz.de','leitungsen.de','likes-pie.com','likescandy.com','merseine.nu','mine.nu','misconfused.org','mypets.ws','myphotos.cc','neat-url.com','office-on-the.net','on-the-web.tv','podzone.net','podzone.org','readmyblog.org','saves-the-whales.com','scrapper-site.net','scrapping.cc','selfip.biz','selfip.com','selfip.info','selfip.net','selfip.org','sells-for-less.com','sells-for-u.com','sells-it.net','sellsyourhome.org','servebbs.com','servebbs.net','servebbs.org','serveftp.net','serveftp.org','servegame.org','shacknet.nu','simple-url.com','space-to-rent.com','stuff-4-sale.org',
                'stuff-4-sale.us','teaches-yoga.com','thruhere.net','traeumtgerade.de','webhop.biz','webhop.info','webhop.net','webhop.org','worse-than.tv',
                'writesthisblog.com']  # 列举所有的顶级域名
    ''' 获取用户输入的根域名 '''
    url2list = URL[0].split(".")
    if len(url2list) >= 3:
        ''' 判断是否为 xxx.edu.cn 等类型的根域名 '''
        domain = '.'.join(url2list[-2:])  # 取最后两个
        if domain in tld_list:
            newDomain = '.'.join(url2list[-3:])  # 包含则向前取一位
            URL.append(newDomain)
        else:  # 不包含则是根域名
            URL.append(domain)
    else:
            URL.append('.'.join(url2list))
    return URL


# 判断该网站是否存活
def isAlive(url):
    header = headers(url)
    times = 0
    url1 = 'http://'+url
    url2 = 'https://'+url
    try:
        requests.get(url=url1, headers=header, timeout=10, proxies=proxies, verify=False).text
        requests.get(url=url2, headers=header, timeout=10, proxies=proxies, verify=False).text
    except Exception as e:
        times += 1
    if times == 2:
        return False
    else:
        return True
# 判断是否为IP地址
def isIP(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# 对allDict的数据处理函数
def processData(allDict):
    global nowIP, historyIP, isCDN, domain, ports, pangZhan, whois, urlPATH, beiAn, framework, cms, waf, houTai, error
    nowIP = allDict['nowIP']
    if nowIP == []:
        nowIP = ['空', '空']
    else:
        nowIP = nowIP[0].split('::')
    historyIP = allDict['historyIP']
    historyIP_list = []
    if historyIP == []:
        historyIP = ['空', '空']
    isCDN = allDict['isCDN']
    if isCDN == []:
        isCDN = [{'ip': '空', 'location': '空', 'exist': '空'}]
    else:
        if len(isCDN) >= 2:
            isCDN += [{'exist': "存在CDN"}]
        else:
            isCDN += [{'exist': "不存在CDN"}]
    domain0 = allDict["domain"]
    if domain0 == []:
        domain = ['空']
    else:
        domain = list(set(domain0))   # 去重
    ports0 = allDict["ports"]
    if ports0 == []:
        ports = ['空']
    else:
        ports = list(set(ports0))
    pangZhan0 = allDict["pangZhan"]
    if pangZhan0 == []:
        pangZhan = ['空']
    else:
        pangZhan = list(set(pangZhan0))
    whois = allDict["whois"]
    if (whois == [[]]) or (whois == []):
        whois = {'空': '空'}
    else:
        whois = whois[0]
    urlPathList = []
    for urlPath in allDict["urlPATH"]:
        if '://' in urlPath:
            url0 = urlPath[urlPath.find(':')+3:]
            urlPathList.append(url0)
        else:
            urlPathList.append(urlPath)
    urlPATH = list(set(urlPathList))
    if urlPATH == []:
        urlPATH = ['空']
    beiAn = allDict["beiAn"]
    if beiAn == []:
        beiAn = ['空:空', '空:空']
    framework = allDict["framework"]
    if framework[0] == []:
        framework[0] = ['空', '空']
    cms = framework[1]
    if cms == {}:
        cms = {'空': '空'}
    waf = framework[2]
    if waf == {}:
        waf = {'waf': '没有侦测到waf'}
    houTai_list = ['admin', 'login', 'pass', 'user', 'member', 'system', 'manage', 'service', 'main']
    houTai = []
    for d in urlPATH:
        for k in houTai_list:
            if k in d:
                houTai.append(d)
    for t in houTai:
        try:
            urlPATH.remove(t)
        except Exception as e:
            continue
    error = allDict['error']


# 生成html文件报告
def all2HTML(url, allDict):
    if not os.path.exists('output'):
        os.mkdir('output')
    processData(allDict)
    doc = dominate.document(title='webscan_report')

    with doc.head:
        link(rel='stylesheet', type="text/css", href='..\lib\\css\\bootstrap.min.css')
        meta(charset="utf-8")
        meta(name="viewport", content="width=device-width, initial-scale=1")

    with doc.body:
        body(cls="table-responsive")
        h2('探测目标：{0}'.format(url), cls="text-center text-success")  # 定义上文

        br()
        '''域名ip地址解析----allDict["nowIP"]、allDict["histotyIP"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("域名地址解析", cls="text-center text-info bg-success")
            tr(td('当前域名ip解析:', align="center"), td('{0}'.format(nowIP[0]), align="center"), td('{0}'.format(nowIP[1]), align="center"))
            for i in historyIP:
                data = i.split("::")
                if len(data) < 2:
                    data = ["空", "空"]
                tr(td('历史域名ip解析:', align="center"), td('{0}'.format(data[0]), align="center"), td('{0}'.format(data[1]), align="center"))

        br()

        '''网站是否存在CDN解析----allDict["isCDN"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("是否存在CDN", cls="text-center text-info bg-success")
            tr(td('ip', align="center"), td('location', align="center"))
            data1 = []
            for i in isCDN:
                for k, v in i.items():
                    data1.append(v)
            for j in range(0, (len(data1)-1), 2):
                tr(td('{0}'.format(data1[j]), align="center"), td('{0}'.format(data1[j+1]), align="center"))
            tr(td('{0}'.format(data1[-1]), align="center", colspan="2"))

        br()

        '''网站是子域名解析----allDict["domain"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("子域名解析", cls="text-center text-info bg-success")
            for i in domain:
                tr(td('{0}'.format(i), align="center"))

        br()

        '''网站端口开放解析----allDict["ports"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网站端口开放情况", cls="text-center text-info bg-success")
            for i in ports:
                tr(td('{0}'.format(i), align="center"))

        br()

        '''网站的旁站解析----allDict["pangZhan"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网站的旁站情况", cls="text-center text-info bg-success")
            for i in pangZhan:
                tr(td('{0}'.format(i), align="center"))

        br()

        '''根域名的whois解析----allDict["whois"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网站的whois情况", cls="text-center text-info bg-success")
            for i, k in whois.items():
                tr(td('{0}'.format(i), align="center"), td('{0}'.format(k), align="center"))

        br()

        '''网址的目录解析----allDict["urlPATH"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网址的目录解析", cls="text-center text-info bg-success")
            for h in houTai:
                tr(td('可能的后台地址: {0}'.format(h), align="center"))
            for i in urlPATH:
                tr(td('{0}'.format(i), align="center"))

        br()

        '''网站的备案解析----allDict["beiAn"]'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网站的备案信息", cls="text-center text-info bg-success")
            for i in beiAn:
                if type(i) != dict:
                    data = i.split(":")
                    tr(td('{0}'.format(data[0]), align="center"), td('{0}'.format(data[1]), align="center"))
                else:
                    for k, v in i.items():
                        tr(td('{0}'.format(k), align="center"), td('{0}'.format(v), align="center"))

        br()

        '''网站的whatweb架构信息----whatweb'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网址的架构解析", cls="text-center text-info bg-success")
            for i in framework[0]:
                tr(td('{0}'.format(i), align="center"))

        br()

        '''网站的CMS架构信息----cms'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网址的CMS解析", cls="text-center text-info bg-success")
            for k, v in cms.items():
                tr(td('{0}'.format(k), align="center"), td('{0}'.format(v), align="center"))

        br()

        '''网站的WAF信息----waf'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("网址的WAF解析", cls="text-center text-info bg-success")
            for k, v in waf.items():
                tr(td('{0}'.format(k), align="center"), td('{0}'.format(v), align="center"))

        br()

        '''侦测过程的报错信息----error'''
        with table(cls="table table-responsive table-bordered table-hover").add(tbody()):
            caption("侦测过程的错误信息", cls="text-center text-info bg-success")
            if error != []:
                for e in error:
                    tr(td('{0}'.format(e), align="center"))
            else:
                tr(td('{0}'.format("运行过程完好无报错!"), align="center"))

        br()
        br()
        br()

    with open('output/{0}_report.html'.format(url), 'w', encoding='utf-8') as f:
        f.write(doc.render())
        print("\033[1;34m[*] 检测报告位置: output/{0}_report.html!!\033[0m \n".format(url))

def port_scan(host, port, proxy=()):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if proxy:
        #     s = create_proxy((host,port), proxy)
        s.settimeout(timeout)
        s.connect((host, port))
        s.send(b'Vol\r\n')
        s.close()
        return True
    except:
        s.close()
        return False

def create_proxy(address, proxy_address):
    # 创建代理连接
    proxy_socket = socket.create_connection(proxy_address)
    # 发送 CONNECT 请求，告知代理要连接的目标地址和端口
    target_host, target_port = address
    request = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
    proxy_socket.sendall(request.encode())
    # 接收代理的响应
    response = proxy_socket.recv(4096).decode()
    if "200 Connection established" not in response:
        raise Exception(f"Failed to establish connection through proxy. Response: {response}")
    # 返回通过代理建立的连接
    return proxy_socket

def print_error(*values: object,
    sep: str = " ",
    end: str = "\n",
    file: str = None,
    flush: bool = False):
    print(colorama.Fore.RED + sep.join(values) + colorama.Style.RESET_ALL, end=end, file=file, flush=flush)