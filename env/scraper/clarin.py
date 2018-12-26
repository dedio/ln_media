# -*- coding: utf-8 -*-

import argparse
from requests import get
from lxml import html
from time import strftime
from datetime import datetime, timedelta
from re import match

class ClarinScraper():
    def request(self, url):
        try:
            return get(url).text
        except Exception as e:
            print e

    def arbol(self, cod):
        return html.fromstring(cod)

    def extrae_url(self, cod):
        tree = self.arbol(cod)
        if tree.xpath('//a/@href'):
            return [url for url in [href.replace('\\', '').replace('"', '') for href in tree.xpath('//a/@href')] if url]

    def extrae_fecha(self, tr):
        return tr.xpath('//meta[@name="cXenseParse:recs:publishtime"]/@content')[0].replace('T', ' ')[:-9]

    def extrae_video(self, tr): 
        return ','.join(list(set(tr.xpath('//div[@class="genoaPlayer"]/@data-src'))))

    def carga(self, unid):
        with open(archivo_csv,'a') as fichero:
            fichero.write(unid)
            fichero.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--fecha_inicial", help = "Fecha inicial formato YYYY-MM-DD")
    parser.add_argument("-f", "--fecha_final", help = "Fecha final formato YYYY-MM-DD")
    args = parser.parse_args()

    if args.fecha_inicial and args.fecha_final:
        if match('\d{4}\-\d{2}\-\d{2}', args.fecha_inicial) and match('\d{4}\-\d{2}\-\d{2}', args.fecha_final):
            if args.fecha_inicial <= args.fecha_final:
                inicio = datetime.strptime(args.fecha_inicial.replace('-', ''), '%Y%m%d')
                fin = datetime.strptime(args.fecha_final.replace('-', ''), '%Y%m%d')
            else:
                print 'LA FECHA INICIAL DEBE SER ANTERIOR O IGUAL A LA FECHA FINAL '
        else:
            print 'RANGO DE FECHAS INVÁLIDO: ', args.fecha_inicial, ' ', args.fecha_final
            print "Comando correcto: python clarin.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"
    else:
        print "FALTAN ARGUMENTOS"
        print "Comando correcto: python clarin.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"

    archivo_csv = ('clarin_' + args.fecha_inicial + '_' + args.fecha_final + '.csv')

    scraper = ClarinScraper()
    for fecha in [inicio + timedelta(days = d) for d in range((fin - inicio).days + 1)]:
        pag = 1
        flag = True
        base_url = 'https://www.clarin.com/ediciones-anteriores/archivo/pager.json?date=' + fecha.strftime("%Y%m%d") + '&page='
        while flag:
            cod = scraper.request((base_url + str(pag)))
            if scraper.extrae_url(cod):
                for url in scraper.extrae_url(cod):
                    cf = scraper.request('https://www.clarin.com' + url)
                    tr = scraper.arbol(cf)
                    fecha = scraper.extrae_fecha(tr)
                    videos = ''
                    if scraper.extrae_video(tr):
                        videos = scraper.extrae_video(tr)
                    scraper.carga(("%s,%s,%s\n" % (fecha, ('https://www.clarin.com' + url), videos)))
                pag += 1
            else:
                flag = False
