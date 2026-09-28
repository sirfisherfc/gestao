# -*- coding: utf-8 -*-
import json
import os
import urllib.request
import io
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
SITE_IMG = os.path.abspath(os.path.join(RAIZ, "..", "site", "assets", "img"))

# Mapeamento dos 22 itens novos do Hubt que não tinham foto no catálogo
ITENS_NOVOS = [
    {
        "id": "london-fish-n-chips",
        "hubt_title": "London - Fish N’ Chips",
        "base": "london-fish-and-chips-sir-fisher",
        "alt": "Peixe frito em massa dourada na cerveja, servido com batatas fritas crocantes",
    },
    {
        "id": "patinha-de-caranguejo",
        "hubt_title": "Patinha de caranguejo",
        "base": "patinha-de-caranguejo-sir-fisher",
        "alt": "Patinhas de caranguejo empanadas e crocantes, servidas com batatas fritas e molho da casa",
    },
    {
        "id": "bolinha-de-peixe-cremosa",
        "hubt_title": "Bolinha de Peixe Cremosa",
        "base": "bolinha-de-peixe-cremosa-sir-fisher",
        "alt": "Bolinhas de peixe cremosas empanadas e douradas, servidas com molho artesanal",
    },
    {
        "id": "crocante-carne-de-sol",
        "hubt_title": "Crocante de Carne de Sol com Abóbora",
        "base": "crocante-carne-de-sol-sir-fisher",
        "alt": "Petiscos crocantes de carne de sol com abóbora, dourados e sequinhos",
    },
    {
        "id": "crocante-calabresa",
        "hubt_title": "Crocante de Calabresa e Alho Poró",
        "base": "crocante-calabresa-sir-fisher",
        "alt": "Petiscos crocantes de calabresa e alho-poró com molho da casa",
    },
    {
        "id": "big-ben-fries",
        "hubt_title": "Big Ben Fries",
        "base": "big-ben-fries-sir-fisher",
        "alt": "Batatas fritas especiais Big Ben servidas com coberturas da casa",
    },
    {
        "id": "pasteizinhos",
        "hubt_title": "Pasteizinhos",
        "base": "pasteizinhos-sir-fisher",
        "alt": "Porção de pasteizinhos crocantes e dourados",
    },
    {
        "id": "crispy-spicy-chicken",
        "hubt_title": "Crispy Spicy Chicken",
        "base": "crispy-spicy-chicken-sir-fisher",
        "alt": "Tiras de frango crocantes e levemente apimentadas, servidas com molho especial",
    },
    {
        "id": "fisher-burger",
        "hubt_title": "Fisher Burger",
        "base": "fisher-burger-sir-fisher",
        "alt": "Hambúrguer Fisher Burger com blend da casa em pão brioche artesanal",
    },
    {
        "id": "edimburger",
        "hubt_title": "Edimburger",
        "base": "edimburger-sir-fisher",
        "alt": "Hambúrguer Edimburger suculento em pão brioche",
    },
    {
        "id": "file-mignon-trinchado",
        "hubt_title": "Filé Mignon Trinchado",
        "base": "file-mignon-trinchado-sir-fisher",
        "alt": "Filé mignon trinchado acebolado servido na chapa com acompanhamentos",
    },
    {
        "id": "caldo-de-peixe",
        "hubt_title": "Caldo de Peixe",
        "base": "caldo-de-peixe-sir-fisher",
        "alt": "Caldo de peixe quente e temperado, servido em cumbuca",
    },
    {
        "id": "calabresa-acebolada-com-fritas",
        "hubt_title": "Calabresa Acebolada com Fritas",
        "base": "calabresa-acebolada-com-fritas-sir-fisher",
        "alt": "Calabresa fatiada acebolada servida com batatas fritas crocantes",
    },
    {
        "id": "macaxeira-ou-batata-frita",
        "hubt_title": "Macaxeira Frita ou Batata Frita",
        "base": "macaxeira-ou-batata-frita-sir-fisher",
        "alt": "Porção de macaxeira frita ou batatas fritas douradas",
    },
    {
        "id": "brownie-de-chocolate",
        "hubt_title": "Brownie de Chocolate",
        "base": "brownie-de-chocolate-sir-fisher",
        "alt": "Fatia de brownie artesanal de chocolate",
    },
    {
        "id": "brownie-com-sorvete",
        "hubt_title": "Brownie com Sorvete",
        "base": "brownie-com-sorvete-sir-fisher",
        "alt": "Brownie quente de chocolate acompanhado de bola de sorvete",
    },
    {
        "id": "cafe-expresso",
        "hubt_title": "Café Expresso",
        "base": "cafe-expresso-sir-fisher",
        "alt": "Xícara de café expresso tirado na hora",
    },
    {
        "id": "molho-extra",
        "hubt_title": "Molho Extra",
        "base": "molho-extra-sir-fisher",
        "alt": "Porção extra de molho artesanal da casa em ramequim",
    },
    {
        "id": "arroz-extra",
        "hubt_title": "Arroz Extra",
        "base": "arroz-extra-sir-fisher",
        "alt": "Porção extra de arroz branco soltinho",
    },
    {
        "id": "rolha",
        "hubt_title": "Rolha",
        "base": "rolha-sir-fisher",
        "alt": "Taxa de rolha para consumo de vinho trazido pelo cliente",
    },
    {
        "id": "pacote-gelo",
        "hubt_title": "Pacote Gelo",
        "base": "pacote-gelo-sir-fisher",
        "alt": "Pacote de gelo em cubos",
    },
    {
        "id": "embalagem-viagem",
        "hubt_title": "Embalagem Viagem",
        "base": "embalagem-viagem-sir-fisher",
        "alt": "Embalagem reforçada para viagem",
    },
]

def crop_4_5(img):
    """Corta centralizado na proporção 4:5 (largura/altura = 0.8)."""
    w, h = img.size
    target_ratio = 4.0 / 5.0
    current_ratio = w / float(h)
    
    if current_ratio > target_ratio:
        # Imagem é mais larga que 4:5 -> corta as laterais
        new_w = int(round(h * target_ratio))
        left = (w - new_w) // 2
        top = 0
        right = left + new_w
        bottom = h
    else:
        # Imagem é mais alta que 4:5 -> corta em cima/baixo
        new_h = int(round(w / target_ratio))
        top = (h - new_h) // 2
        left = 0
        bottom = top + new_h
        right = w
        
    return img.crop((left, top, right, bottom))

def processar():
    with open(os.path.join(RAIZ, "hubt_items_with_images.json"), "r", encoding="utf-8") as f:
        hubt_items = json.load(f)

    hubt_map = {h["title"]: h["images"][0] for h in hubt_items}

    print(f"Salvando imagens em: {SITE_IMG}")
    os.makedirs(SITE_IMG, exist_ok=True)

    for item in ITENS_NOVOS:
        title = item["hubt_title"]
        src = hubt_map.get(title)
        if not src:
            # tenta busca insensível
            for k, v in hubt_map.items():
                if k.lower() == title.lower():
                    src = v
                    break
        if not src:
            print(f"AVISO: Imagem para '{title}' não encontrada no Hubt!")
            continue

        url = "https:" + src + "=s0"
        print(f"Baixando '{title}' ({url})...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = resp.read()

        img = Image.open(io.BytesIO(data))
        if img.mode != "RGB":
            img = img.convert("RGB")

        cropped = crop_4_5(img)
        base = item["base"]

        for w_target in [440, 660]:
            h_target = int(round(w_target * 5.0 / 4.0))
            resized = cropped.resize((w_target, h_target), Image.Resampling.LANCZOS)
            
            # 1. JPG
            jpg_path = os.path.join(SITE_IMG, f"{base}-{w_target}.jpg")
            resized.save(jpg_path, "JPEG", quality=85, optimize=True)
            
            # 2. WebP
            webp_path = os.path.join(SITE_IMG, f"{base}-{w_target}.webp")
            resized.save(webp_path, "WEBP", quality=85)
            
            # 3. AVIF
            avif_path = os.path.join(SITE_IMG, f"{base}-{w_target}.avif")
            resized.save(avif_path, "AVIF", quality=80)

        print(f"  OK: {base} [440x550, 660x825] gerados em jpg, webp e avif.")

if __name__ == "__main__":
    processar()
