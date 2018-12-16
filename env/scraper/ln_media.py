# -*- coding: utf-8 -*-

import argparse
from requests import get
from json import loads
from lxml import html, etree
from re import findall, match
from time import strftime
from datetime import datetime, timedelta

class LanacionComArScraper():
    def request(self, url):
        try:
            cod = get(url).text
            return cod
        except Exception as e:
            print e

    def sec(self, cf):
        tree = html.fromstring(cf)
        return ['http://servicios.lanacion.com.ar' + href for href in tree.xpath('//span[@class="derecha"]/a/@href')]

    def art(self, cf):
        tree = html.fromstring(cf)
        return tree.xpath('//h3/a/@href')

    def extrae_url(self, json):
        return [art['url'] for art in json['articles']]

    def link_xml(self, claves):
        lista = []
        for clave in claves:
            url = 'https://content.jwplatform.com/jw6/' + str(clave) + '.xml'
            codxml = self.request(url)
            lista.append(findall('<link>(.+?)</link>', codxml)[0])
        return ','.join(lista)

    def parse_video(self, cod):
        videos = []
        if 'data-jwkey="' in cod:
            videos.append(self.link_xml(findall('data-jwkey="(.+?)"', cod)))
        treehtml = html.fromstring(cod)
        if treehtml.xpath('//iframe[contains(@src, "youtube")]'):
            videos.append(','.join(treehtml.xpath('//iframe[contains(@src, "youtube")]/@src')))

        return ','.join(videos)

    def parse_social(self, cod):
        social = []
        treehtml = html.fromstring(cod)
        if treehtml.xpath('//div[@class="externo instagram"]'):
            instagram = treehtml.xpath('//div[@class="externo instagram"]//a[@target="_blank"]/@href')
            social.append(','.join(instagram))
        if treehtml.xpath('//div[@class="externo twitter"]'):
            twitter = treehtml.xpath('//div[@class="externo twitter"]//a[contains(@href, "https://twitter.com")]/@href')
            social.append(','.join(twitter))
        return ''.join(social)

    def carga(self, unid):
        with open(archivo_csv,'a') as fou:
            fou.write(unid)
            fou.close()

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
            print 'RANGO DE FECHA INVÁLIDO: ', args.fecha_inicial, ' ', args.fecha_final
            print "Comando correcto: python ln_media.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"
    else:
        print "FALTAN ARGUMENTOS"
        print "Comando correcto: python ln_media.py -i <YYYY-MM-DD> -f <YYYY-MM-DD>"

    s = LanacionComArScraper()
    archivo_csv = ('ln_' + args.fecha_inicial + '_' + args.fecha_final + '.csv')

    urls = []
    for fecha in  [inicio + timedelta(days = d) for d in range((fin - inicio).days + 1)]:
        cf = s.request('http://servicios.lanacion.com.ar/archivo-f' + fecha.strftime("%d/%m/%Y"))
        for link in s.sec(cf):
            cf = s.request(link)
            for link in s.art(cf):
                urls.append(link)
    print 'Cargando: ' + str(len(urls)) + ' entradas...'
    for url in urls:
        cf = s.request(url)
        videos = s.parse_video(cf)
        social = s.parse_social(cf)
        s.carga(("%s,%s\n" % (url, (videos + social))))
