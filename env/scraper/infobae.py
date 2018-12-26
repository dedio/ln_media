# -*- coding: utf-8 -*-

from requests import get
from re import findall
from lxml import html
from time import sleep, strftime

class InfobaeScraper():
    def request(self, url):
        try:
            return get(url).text
        except Exception as e:
            print e

    def arbol(self, cod):
        return html.fromstring(cod)

    def extrae_url(self, url):
        cod = self.request(url)
        tree = html.fromstring(cod)
        return [('https://www.infobae.com' + href) if href[0] == '/' else '' for href in list(set(tree.xpath('//div[contains(@class, "headline")]/a/@href | //h4/ancestor::a/@href')))]

    def extrae_video(self, cod, tree):
        lista = []
        if findall('"stream_type":"mp4","url":"(.+?)"', cod):
            lista.append(findall('"stream_type":"mp4","url":"(.+?)"', cod)[0])
        if tree.xpath('//script[@src="//player-infobae-production.video.arcpublishing.com/prod/powaBoot.js"]'):
            lista.append(u"VÍDEO EMBEBIDO".encode("utf8"))
        return lista

    def extrae_fecha(self, tree):
        fecha = tree.xpath('//div[@class="full-date"]/text()')
        lista = fecha[0].split()

        meses = {'Enero': '-01-', 'Febrero': '-02-', 'Marzo':'-03-',
        'Abril':'-04-', 'Mayo':'-05-', 'Junio':'-06-', 'Julio':'-07-',
        'Agosto':'-08-', 'Septiembre':'-09-', 'Octubre':'-10-', 'Noviembre':'-11-',
        'Diciembre':'-12-'}

        return (lista[5] + meses[lista[3]] + lista[1])

    def carga(self, unid):
        with open('infobae.csv','a') as fichero:
            fichero.write(unid)
            fichero.close()

if __name__=='__main__':
    enlaces = (
        'https://www.infobae.com/',
        'https://www.infobae.com/ultimas-noticias/',
        'https://www.infobae.com/politica/',
        'https://www.infobae.com/sociedad/',
        'https://www.infobae.com/deportes/',
        'https://www.infobae.com/tecno/',
        'https://www.infobae.com/economia/',
        'https://www.infobae.com/documentales/',
        'https://www.infobae.com/campo',
        'https://www.infobae.com/tendencias/',
        'https://www.infobae.com/la-vidriera-de-infobae/',
        'https://www.infobae.com/sociedad/personajes/',
        'https://www.infobae.com/salud/',
        'https://www.infobae.com/series-peliculas/',
        'https://www.infobae.com/autos/',
        'https://www.infobae.com/america/',
        )
    scraper = InfobaeScraper()

    for enlace in enlaces:
        for entrada in scraper.extrae_url(enlace):
            print entrada
            sleep(0.5)
            cod = scraper.request(entrada)
            if type(cod) == 'unicode':
                tree = scraper.arbol(cod)
                videos = ''
                if scraper.extrae_video(cod, tree):
                    videos = scraper.extrae_video(cod, tree)
                fecha = scraper.extrae_fecha(tree)
                scraper.carga(("%s,%s,%s\n" % (fecha, entrada, videos)))
            else:
                scraper.carga(("%s,%s,%s\n" % (strftime("%Y-%m-%d"), entrada, 'NO PARSEABLE')))
