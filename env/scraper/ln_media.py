# -*- coding: utf-8 -*-

import csv
import argparse
from urllib2 import urlopen, Request
from json import loads, dump
from lxml import html, etree
from re import findall, match
from time import strftime

class LanacionComArScraper():
    def request(self, url):
        try:
            cod = urlopen(Request(url)).read()
            return cod
        except Exception as e:
            print e

    def extrae_url(self, json):
        return [art['url'] for art in json['articles']]

    def link_xml(self, claves):
        lista = []
        for clave in claves:
            url = 'https://content.jwplatform.com/jw6/' + str(clave) + '.xml'
            codxml = self.request(url)
            treexml = etree.fromstring(codxml)
            lista.append(treexml[0].findtext('link'))
        return ','.join(lista)

    def parse_video(self, url):
        videos = []
        cod = self.request(url)
        if 'data-jwkey="' in cod:
            videos.append(self.link_xml(findall('data-jwkey="(.+?)"', cod)))
        treehtml = html.fromstring(cod)
        if treehtml.xpath('//iframe[contains(@src, "youtube")]'):
            videos.append(' '.join(treehtml.xpath('//iframe[contains(@src, "youtube")]/@src')))

        #return {'video_url': videos}
        return ''.join(videos)

    def parse_social(self, url):
        social = []
        cod = self.request(url)
        treehtml = html.fromstring(cod)
        if treehtml.xpath('//div[@class="externo instagram"]'):
            instagram = treehtml.xpath('//div[@class="externo instagram"]//a[@target="_blank"]/@href')
            social.append(' '.join(instagram))
        if treehtml.xpath('//div[@class="externo twitter"]'):
            twitter = treehtml.xpath('//div[@class="externo twitter"]//a[contains(@href, "https://twitter.com")]/@href')
            social.append(' '.join(twitter))
        return ''.join(social)

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--fecha_inicial", help = "Fecha inicial formato YYYY-MM-DD")
    parser.add_argument("-f", "--fecha_final", help = "Fecha final formato YYYY-MM-DD")
    args = parser.parse_args()

    api = '&apiKey=ea72f4e20f714102beb15a10787cb2ac'
    base = 'https://newsapi.org/v2/everything?sources=la-nacion'
    fecha1 = '&from='
    fecha2 = '&to='
    pagesize = '&pageSize=100'
    #page = '&page=1'
    page = '&page='
    fecha_inicial = ''
    fecha_final = ''

    if args.fecha_inicial and args.fecha_final:
        if match('\d{4}\-\d{2}\-\d{2}', args.fecha_inicial):
            if args.fecha_inicial < args.fecha_final:
                fecha_inicial = fecha1 + args.fecha_inicial
            else:
                print '########## LA FECHA INICIAL DEBE SER ANTERIOR A LA FECHA FINAL '
        else:
            print '########## RANGO DE FECHA INVÁLIDO: ', args.fecha_inicial, ' ', args.fecha_final
            print "############ Comando correcto:"
            print "python ln_media.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"
        if match('\d{4}\-\d{2}\-\d{2}', args.fecha_final):
            if args.fecha_inicial < args.fecha_final:
                fecha_final = fecha2 + args.fecha_final
            else:
                print '########## LA FECHA INICIAL DEBE SER ANTERIOR A LA FECHA FINAL '
        else:
            print '########## RANGO DE FECHA INVÁLIDO: ', args.fecha_inicial, ' ', args.fecha_final
            print "############ Comando correcto:"
            print "python ln_media.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"
    else:
        print "############ FALTAN ARGUMENTOS"
        print "############ Comando correcto:"
        print "python ln_media.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"
    if fecha_inicial and fecha_final:
        scraper = LanacionComArScraper()
        flag = True
        num = 1
        datos = []
        while flag:
            url = base + fecha_inicial + fecha_final + pagesize + page + str(num) + api
            json = loads(scraper.request(url))
            if json['articles']:
                for url in scraper.extrae_url(json):
                    unid = []
                    videos = scraper.parse_video(url)
                    social = scraper.parse_social(url)
                    unid.append(url)
                    unid.append(videos)
                    unid.append(social)
                    datos.append(unid)
                num = num + 1
            else:
               flag = False

        with open(('ln_media' + strftime("%Y%m%d%H%M%S") + '.csv'),'wb') as fou:
            dw = csv.writer(fou, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            dw.writerow(['url', 'videos', 'social'])
            dw.writerows(datos)
            fou.close()

        with open(('ln_media' + strftime("%Y%m%d%H%M%S") + '.json'), 'wb') as fichero:
            dump(json, fichero)
            fichero.close()
