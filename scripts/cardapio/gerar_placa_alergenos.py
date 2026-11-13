"""Gera placa A3 com os dez pictogramas oficiais ja usados no cardapio.

Uso: python scripts/cardapio/gerar_placa_alergenos.py --saida caminho.pdf
Requer reportlab. O PDF e um artefato local, nao uma prova de afixacao.
"""
import argparse
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def gerar(saida):
    assets = Path(__file__).resolve().parents[3] / 'site/assets/img/alergenos'
    itens = [('gluten', 'GLÚTEN'), ('lactose', 'LACTOSE'), ('leite', 'LEITE'),
             ('ovo', 'OVO'), ('peixe', 'PEIXE'), ('crustaceos', 'CRUSTÁCEOS'),
             ('soja', 'SOJA'), ('castanhas', 'CASTANHAS'), ('amendoas', 'AMÊNDOAS'),
             ('corantes', 'CORANTES')]
    saida.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(saida), pagesize=A3)
    c.setTitle('Sir Fisher - Tabela indicativa de alergênicos')
    w, h = A3
    c.setFillColor(colors.HexColor('#392b23'))
    c.rect(0, h-66*mm, w, 66*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#fff7e8'))
    c.setFont('Times-Bold', 36)
    c.drawCentredString(w/2, h-24*mm, 'SIR FISHER')
    c.setFont('Helvetica-Bold', 23)
    c.drawCentredString(w/2, h-39*mm, 'TABELA DE ALERGÊNICOS')
    c.setFont('Helvetica', 12)
    c.drawCentredString(w/2, h-51*mm, 'Consulte os ícones ao lado do nome de cada produto no cardápio.')
    cw, rh = (w-36*mm)/2, 55*mm
    top = h-78*mm
    for i, (arquivo, nome) in enumerate(itens):
        x, y = 18*mm+(i%2)*cw, top-(i//2+1)*rh
        c.setStrokeColor(colors.HexColor('#ded6cc'))
        c.roundRect(x+3*mm,y+3*mm,cw-6*mm,rh-6*mm,4*mm,stroke=1,fill=0)
        icone = next(assets.glob(arquivo+'.*.png'))
        c.drawImage(str(icone),x+(cw-80*mm)/2,y+14*mm,80*mm,40*mm,
                    preserveAspectRatio=True,anchor='c',mask='auto')
        c.setFillColor(colors.HexColor('#30261e'))
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(x+cw/2,y+8*mm,nome)
    c.setFillColor(colors.HexColor('#392b23'))
    c.setFont('Helvetica-Bold',16)
    c.drawCentredString(w/2,46*mm,'ALERGIA? AVISE ANTES DO PEDIDO.')
    c.setFont('Helvetica',14)
    c.drawCentredString(w/2,37*mm,'Pode ter contaminação cruzada.')
    c.setFont('Helvetica',10)
    c.drawCentredString(w/2,25*mm,'Leite e lactose são indicados separadamente.')
    c.drawCentredString(w/2,17*mm,'Lei Estadual/CE nº 17.899/2022 - Anexo I - art. 1º, §§ 2º e 3º')
    c.save()


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saida',type=Path,required=True)
    gerar(ap.parse_args().saida)
